"""Download the pinned Hugging Face model and prepare the offline server index."""

import shutil
import tempfile
from pathlib import Path
from urllib.request import urlopen

from services.studio_search import MODEL_FILES, MODEL_ID, REVISION, build_index, catalog_passages, model_directory


def main():
    from app import app, studio_schemes

    directory = model_directory(app.root_path)
    directory.mkdir(parents=True, exist_ok=True)
    for remote, filename in MODEL_FILES.items():
        destination = directory / filename
        if destination.is_file():
            continue
        print(f"Downloading {filename} from {MODEL_ID}...", flush=True)
        temporary = None
        try:
            with urlopen(f"https://huggingface.co/{MODEL_ID}/resolve/{REVISION}/{remote}", timeout=60) as source:
                with tempfile.NamedTemporaryFile(dir=directory, delete=False) as target:
                    temporary = Path(target.name)
                    shutil.copyfileobj(source, target)
            temporary.replace(destination)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    rows = catalog_passages(studio_schemes)
    print(f"Embedding {len(rows)} passages from {len(studio_schemes)} schemes...", flush=True)
    build_index(directory, rows)
    print(f"Semantic index ready at {directory}", flush=True)


if __name__ == "__main__":
    main()
