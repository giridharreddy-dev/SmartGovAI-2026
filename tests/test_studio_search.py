from unittest.mock import patch

import pytest

from services.studio_search import INDEX_NAME, SearchUnavailable, build_index, search_corpus, semantic_ids


def test_search_index_rejects_stale_data_and_weak_or_filtered_neighbors(tmp_path):
    np = pytest.importorskip("numpy")

    class ExampleEncoder:
        def __init__(self, directory):
            self.np = np

        def encode(self, texts):
            scores = {"Housing grant": 0.9, "Job placement": 0.86, "Water bill": 0.79}
            vectors = np.zeros((len(texts), 384), dtype=np.float32)
            for i, text in enumerate(texts):
                vectors[i, 0] = next((score for title, score in scores.items() if title in text), 1.0)
            return vectors

    schemes = {
        title: {"slug": slug, "simplified": {"description": title}}
        for title, slug in (("Housing grant", "house"), ("Job placement", "jobs"), ("Water bill", "water"))
    }
    rows, fingerprint = search_corpus(schemes)
    with patch("services.studio_search._Encoder", ExampleEncoder):
        with pytest.raises(SearchUnavailable):
            semantic_ids(tmp_path, rows, fingerprint, "query", {"house"})
        build_index(tmp_path, rows)
        assert (tmp_path / INDEX_NAME).is_file()
        assert semantic_ids(tmp_path, rows, fingerprint, "query", {"house", "jobs", "water"}) == ["house", "jobs"]
        assert semantic_ids(tmp_path, rows, fingerprint, "query", {"jobs", "water"}) == ["jobs"]
        assert semantic_ids(tmp_path, rows, fingerprint, "query", {"water"}) == []
        assert semantic_ids(tmp_path, rows, fingerprint, "query", set()) == []
        with pytest.raises(SearchUnavailable, match="rebuilt"):
            semantic_ids(tmp_path, rows, "different catalog", "query", {"house"})
