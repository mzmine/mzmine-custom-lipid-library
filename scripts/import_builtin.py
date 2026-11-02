"""Copies mzmine's built-in lipid classes into classes/builtin as read-only references.

Maintainers export the built-in classes from mzmine (see docs/maintainers.md) and run:
python scripts/import_builtin.py <export-dir>
where <export-dir> contains builtin/*.json and enums.json.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import build_schema
import lipidlib


def main(export_dir: Path, mzmine_version: str) -> None:
    shutil.copy(export_dir / "enums.json", lipidlib.ROOT / "schema" / "enums.json")
    for old in lipidlib.BUILTIN_DIR.glob("*.json"):
        old.unlink()
    for path in sorted((export_dir / "builtin").glob("*.json")):
        lipid_class = json.loads(path.read_text(encoding="utf-8"))[0]
        class_id = lipidlib.slugify(path.stem)
        lipid_class["_meta"] = {
            "id": class_id,
            "source": "builtin",
            "description": f"Built-in mzmine lipid class {lipid_class['abbr']}. "
                           "Use it as a template for your own classes.",
            "authors": [{"name": "mzmine development team"}],
            "mzmineVersion": mzmine_version,
            "license": "MIT",
            "licenseUrl": "https://github.com/mzmine/mzmine/blob/master/LICENSE.txt",
        }
        (lipidlib.BUILTIN_DIR / f"{class_id}.json").write_text(
            json.dumps([lipid_class], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    build_schema.main()
    print(f"Imported {len(list(lipidlib.BUILTIN_DIR.glob('*.json')))} built-in classes.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: python scripts/import_builtin.py <export-dir> <mzmine-version>")
    main(Path(sys.argv[1]), sys.argv[2])
