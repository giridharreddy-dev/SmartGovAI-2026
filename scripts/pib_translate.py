"""Prepare and run a local English-to-Telugu IndicTrans2 review translator."""

import argparse
import shutil
import tempfile
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import urlopen

from scripts.pib_regional import telugu_text

MODEL = "naklitechie/indictrans2-en-indic-dist-200M-ONNX-int8"
REVISION = "e88c4f837dfbf2abecf239b5c89169dfa31580bb"
DEFAULT_MODEL_DIR = Path(__file__).resolve().parents[1] / "scratch" / "pib-indictrans2"
FILES = {
    "encoder_model.onnx": 75_979_645,
    "decoder_model.onnx": 142_868_773,
    "tokenizer_src.json": 3_380_130,
    "tokenizer_tgt.json": 17_666_531,
}
SOURCE_VOCAB_SIZE = 32_322
PUNCTUATION = str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'", "–": "-", "—": "-"})


def prepare(directory):
    directory.mkdir(parents=True, exist_ok=True)

    def fetch(item):
        name, size = item
        dest = directory / name
        if dest.is_file() and dest.stat().st_size == size:
            return
        temporary = None
        try:
            url = f"https://huggingface.co/{MODEL}/resolve/{REVISION}/{name}"
            with urlopen(url, timeout=60) as response, tempfile.NamedTemporaryFile(dir=directory, delete=False) as output:
                temporary = Path(output.name)
                shutil.copyfileobj(response, output)
            if temporary.stat().st_size != size:
                raise ValueError(f"Incomplete model file: {name}")
            temporary.replace(dest)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(fetch, FILES.items()))


def _telugu_script(text):
    # IndicTrans2 emits Telugu in a shared Devanagari representation. The
    # corresponding letters and marks occupy aligned Indic Unicode blocks.
    output = []
    for character in text:
        code = ord(character)
        if 0x0900 <= code <= 0x097F:
            target = chr(code + 0x0300)
            if unicodedata.name(target, "").startswith("TELUGU"):
                character = target
        output.append(character)
    return "".join(output).replace("।", ".").strip()


class LocalTranslator:
    def __init__(self, directory=DEFAULT_MODEL_DIR):
        import numpy as np
        import onnxruntime as ort
        from tokenizers import Tokenizer

        if any(not (directory / name).is_file() or (directory / name).stat().st_size != size
               for name, size in FILES.items()):
            raise ValueError("Prepare the Telugu model with python -m scripts.pib_translate --prepare.")
        self.np = np
        self.source = Tokenizer.from_file(str(directory / "tokenizer_src.json"))
        self.target = Tokenizer.from_file(str(directory / "tokenizer_tgt.json"))
        options = ort.SessionOptions()
        options.intra_op_num_threads = 2
        self.encoder = ort.InferenceSession(str(directory / "encoder_model.onnx"), options, providers=["CPUExecutionProvider"])
        self.decoder = ort.InferenceSession(str(directory / "decoder_model.onnx"), options, providers=["CPUExecutionProvider"])

    def translate(self, english):
        text = unicodedata.normalize("NFKC", " ".join(english.split())).translate(PUNCTUATION)
        encoding = self.source.encode("eng_Latn tel_Telu " + text)
        ids = []
        for token, token_id in zip(encoding.tokens, encoding.ids):
            if token_id >= SOURCE_VOCAB_SIZE:
                # The export's fast tokenizer adds some punctuation IDs above
                # the encoder's vocabulary. Use the original SentencePiece form.
                replacement = self.source.token_to_id("▁" + token)
                token_id = replacement if replacement is not None and replacement < SOURCE_VOCAB_SIZE else 3
            ids.append(token_id)
        if len(ids) > 256:
            raise ValueError("The excerpt exceeds the translation model context.")
        tokens = self.np.array([ids], dtype=self.np.int64)
        attention = self.np.ones_like(tokens)
        hidden = self.encoder.run(["last_hidden_state"], {"input_ids": tokens, "attention_mask": attention})[0]
        output = [2]
        for _ in range(120):
            logits = self.decoder.run(["logits"], {
                "input_ids": self.np.array([output], dtype=self.np.int64),
                "encoder_attention_mask": attention,
                "encoder_hidden_states": hidden,
            })[0]
            word = int(logits[0, -1].argmax())
            if word == 2:
                break
            output.append(word)
        else:
            raise ValueError("The translation model did not finish its draft.")
        text = _telugu_script(self.target.decode(output[1:], skip_special_tokens=True))
        if not telugu_text(text):
            raise ValueError("The model did not return enough Telugu text.")
        return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true", required=True, help="Download about 240 MB of pinned model files")
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    args = parser.parse_args()
    prepare(args.model_dir)
    print(f"Local Telugu model ready at {args.model_dir}")


if __name__ == "__main__":
    main()
