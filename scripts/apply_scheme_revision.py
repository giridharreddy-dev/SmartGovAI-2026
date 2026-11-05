"""Preview or record an explicitly verified operational revision."""

import argparse
import json
import tempfile
from pathlib import Path

from scripts.discover_schemes import ROOT, source_catalog
from services.scheme_revisions import (
    REVISION_PATH, ReviewedRevision, apply_revisions, checklist, read_revisions, section_statuses,
)
from utils import generate_slug


def apply_file(root, catalog, revision, write=False):
    root = Path(root)
    path = root / REVISION_PATH

    def candidate():
        revisions = [*read_revisions(root), revision]
        updated = apply_revisions(catalog, revisions)
        name = next(name for name, item in catalog.items()
                    if (item.get("slug") or generate_slug(name)) == revision.scheme_id)
        return revisions, updated[name]

    if not write:
        return candidate()[1]
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_suffix(".lock")
    with lock.open("x", encoding="utf-8"):
        pass
    temporary = None
    try:
        revisions, updated = candidate()
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False, mode="w", encoding="utf-8") as output:
            temporary = Path(output.name)
            json.dump({"revisions": [item.model_dump(mode="json", exclude_unset=True) for item in revisions]},
                      output, indent=2, ensure_ascii=False)
            output.write("\n")
        temporary.replace(path)
        return updated
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        lock.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("patch", type=Path, help="JSON object with lead_id, scheme_id, status=verified, reviewed_on, source_url, and changed fields")
    parser.add_argument("--apply", action="store_true", help="Record the patch in the catalog overlay")
    args = parser.parse_args()
    try:
        revision = ReviewedRevision.model_validate_json(args.patch.read_text(encoding="utf-8-sig"))
        updated = apply_file(ROOT, source_catalog(), revision, write=args.apply)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Revision rejected: {error}\n")
    print(json.dumps({
        "operations": updated["operations"],
        "effective_checklist": checklist(updated)[0],
        "section_statuses": section_statuses(updated),
    }, ensure_ascii=False, indent=2))
    print("Recorded reviewed revision." if args.apply else "Preview only. Use --apply to record the reviewed revision.")


if __name__ == "__main__":
    main()
