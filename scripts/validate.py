"""Validates lipid class files. Exits with 1 if any file has errors.

Usage: python scripts/validate.py [files...]   (default: all files in classes/)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import lipidlib


def main(argv: list[str]) -> int:
    if argv:
        files = [(Path(a).resolve(), lipidlib.BUILTIN_DIR not in Path(a).resolve().parents)
                 for a in argv]
    else:
        files = lipidlib.all_class_files()

    reports = [lipidlib.validate_file(path, community) for path, community in files]

    # ids and names must be unique across community classes
    seen: dict[str, Path] = {}
    for path, community in files:
        if not community:
            continue
        try:
            lipid_class = lipidlib.load_class_file(path)[0]
        except (OSError, json.JSONDecodeError, IndexError, KeyError):
            continue
        key = f"{lipid_class.get('abbr')}|{lipid_class.get('name')}".lower()
        if key in seen:
            next(r for r in reports if r.path == path).error(
                f"a class with the same name and abbreviation exists: {seen[key].name}")
        seen[key] = path

    failed = 0
    for r in reports:
        rel = r.path.relative_to(lipidlib.ROOT) if lipidlib.ROOT in r.path.parents else r.path
        for e in r.errors:
            print(f"::error file={rel}::{e}")
        for w in r.warnings:
            print(f"::warning file={rel}::{w}")
        failed += bool(r.errors)
    print(f"Checked {len(reports)} files: {failed} with errors, "
          f"{sum(bool(r.warnings) for r in reports)} with warnings.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
