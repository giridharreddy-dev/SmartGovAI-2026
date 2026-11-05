"""Local multilingual E5 retrieval for the public Citizen Studio catalog."""

import hashlib
import json
import os
import tempfile
from functools import lru_cache
from pathlib import Path
from threading import BoundedSemaphore, Lock

MODEL_ID = "Xenova/multilingual-e5-small"
REVISION = "761b726dd34fb83930e26aab4e9ac3899aa1fa78"
MODEL_FILES = {"onnx/model_quantized.onnx": "model_quantized.onnx", "tokenizer.json": "tokenizer.json"}
INDEX_NAME = "catalog.npz"
_load_lock = Lock()
_query_slots = BoundedSemaphore(2)


class SearchUnavailable(Exception):
    """The optional local model is missing, stale, or at capacity."""


def model_directory(root):
    return Path(os.getenv("STUDIO_SEARCH_MODEL_DIR") or Path(root) / ".studio-search").resolve()


def catalog_passages(schemes):
    """One passage per available language, with a stable scheme ID for both."""
    rows = []
    for name, item in schemes.items():
        for key in ("simplified", "telugu"):
            sections = item.get(key) or {}
            summary = " ".join(
                str(sections.get(field) or "") for field in ("description", "benefits", "eligibility")
            ).strip()
            if not summary:
                continue
            text = " ".join(filter(None, (
                (item.get("telugu_name") or name) if key == "telugu" else name,
                item.get("category"),
                " ".join(item.get("keywords") or []),
                summary,
            )))
            rows.append((item["slug"], text))
    return tuple(rows)


def _fingerprint(rows):
    data = json.dumps((REVISION, rows), ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(data.encode()).hexdigest()


class _Encoder:
    def __init__(self, directory):
        import numpy as np
        import onnxruntime as ort
        from tokenizers import Tokenizer

        self.np = np
        self.tokenizer = Tokenizer.from_file(str(directory / "tokenizer.json"))
        self.tokenizer.enable_truncation(max_length=192)
        self.tokenizer.enable_padding(pad_id=self.tokenizer.token_to_id("<pad>"), pad_token="<pad>")
        options = ort.SessionOptions()
        options.intra_op_num_threads = 2
        self.session = ort.InferenceSession(
            str(directory / "model_quantized.onnx"), options, providers=["CPUExecutionProvider"],
        )
        self.input_names = {item.name for item in self.session.get_inputs()}

    def encode(self, texts):
        np = self.np
        tokens = self.tokenizer.encode_batch(texts)
        mask = np.array([token.attention_mask for token in tokens], dtype=np.int64)
        inputs = {
            "input_ids": np.array([token.ids for token in tokens], dtype=np.int64),
            "attention_mask": mask,
        }
        if "token_type_ids" in self.input_names:
            inputs["token_type_ids"] = np.zeros_like(mask)
        hidden = self.session.run(["last_hidden_state"], inputs)[0]
        pooled = (hidden * mask[..., None]).sum(axis=1) / mask.sum(axis=1, keepdims=True)
        vectors = pooled.astype(np.float32)
        return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


def build_index(directory, rows):
    encoder = _Encoder(directory)
    texts = ["passage: " + text for _, text in rows]
    vectors = encoder.np.concatenate([
        encoder.encode(texts[start:start + 8]) for start in range(0, len(texts), 8)
    ])
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=directory, suffix=".npz", delete=False) as temp:
            temp_path = Path(temp.name)
            encoder.np.savez(temp, vectors=vectors, fingerprint=_fingerprint(rows))
        temp_path.replace(directory / INDEX_NAME)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


@lru_cache(maxsize=1)
def _load(directory, expected, _index_version, row_count):
    import numpy as np

    with np.load(directory / INDEX_NAME, allow_pickle=False) as index:
        if index["fingerprint"].item() != expected:
            raise SearchUnavailable("The semantic index needs to be rebuilt.")
        vectors = index["vectors"]
    if vectors.shape != (row_count, 384) or not np.isfinite(vectors).all():
        raise SearchUnavailable("The semantic index is invalid.")
    return _Encoder(directory), vectors


def semantic_ids(directory, rows, fingerprint, query, allowed):
    if not allowed:
        return []
    if not _query_slots.acquire(blocking=False):
        raise SearchUnavailable("Semantic search is busy.")
    try:
        try:
            info = (directory / INDEX_NAME).stat()
            with _load_lock:
                encoder, vectors = _load(directory, fingerprint, info.st_mtime_ns, len(rows))
        except (ImportError, OSError) as error:
            raise SearchUnavailable("The semantic model and index need to be installed.") from error
        scores = vectors @ encoder.encode(["query: " + query])[0]
        best = {}
        for (slug, _), score in zip(rows, scores):
            if slug in allowed:
                best[slug] = max(best.get(slug, 0), float(score))
        ranked = sorted(best, key=best.get, reverse=True)
        if not ranked:
            return []
        # E5 cosine scores are compressed. Ignore weak neighbors and cap suggestions.
        cutoff = max(0.825, best[ranked[0]] - 0.045)
        return [slug for slug in ranked[:8] if best[slug] >= cutoff]
    finally:
        _query_slots.release()


def search_corpus(schemes):
    rows = catalog_passages(schemes)
    return rows, _fingerprint(rows)
