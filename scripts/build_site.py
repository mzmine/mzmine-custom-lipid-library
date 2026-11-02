"""Builds the static catalog website into _site/.

Output, also used by mzmine to browse and download classes:
  index.json                 catalog with one entry per class
  classes/<id>.json          mzmine importable file of one class
  bundles/community.json     all community classes in one mzmine importable file
  bundles/builtin.json       all built-in reference classes
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import lipidlib

OUT = lipidlib.ROOT / "_site"


def last_changed(path: Path) -> str | None:
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(path)],
                             cwd=lipidlib.ROOT, capture_output=True, text=True, check=True)
        return out.stdout.strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def catalog_entry(lipid_class: dict, community: bool, path: Path) -> dict:
    meta = lipid_class.get("_meta", {})
    rules = lipid_class.get("fragmentationRules", [])
    return {
        "id": meta["id"],
        "source": "community" if community else "builtin",
        "name": lipid_class["name"],
        "abbr": lipid_class["abbr"],
        "coreClass": lipid_class["coreClass"],
        "mainClass": lipid_class["mainClass"],
        "backBoneFormula": lipid_class["backBoneFormula"],
        "backBoneMass": lipidlib.monoisotopic_mass(lipid_class["backBoneFormula"]),
        "chainTypes": lipid_class["chainTypes"],
        "polarities": sorted({r.get("polarityType") for r in rules if r.get("polarityType")}),
        "ionizations": sorted({r.get("ionizationType") for r in rules if r.get("ionizationType")}),
        "rules": [{**r, "description": lipidlib.describe_rule(r)} for r in rules],
        "description": meta.get("description", ""),
        "authors": meta.get("authors", []),
        "references": meta.get("references", []),
        "tags": meta.get("tags", []),
        "instrument": meta.get("instrument", ""),
        "version": meta.get("version", ""),
        "minMzmineVersion": meta.get("minMzmineVersion")
                            or (lipidlib.EXTENDED_RULES_MIN_MZMINE
                                if lipidlib.requires_extended_rules(lipid_class) else None),
        "updated": last_changed(path),
        "rightsHolder": meta.get("rightsHolder"),
        "license": meta.get("license"),
        "licenseUrl": meta.get("licenseUrl"),
        "file": f"classes/{meta['id']}.json",
    }


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(lipidlib.ROOT / "site", OUT)
    (OUT / "classes").mkdir()
    (OUT / "bundles").mkdir()

    entries, bundles = [], {"community": [], "builtin": []}
    for path, community in lipidlib.all_class_files():
        report = lipidlib.validate_file(path, community)
        if report.errors:
            print(f"Skipping invalid {path.name}: {report.errors}", file=sys.stderr)
            continue
        lipid_class = lipidlib.load_class_file(path)[0]
        entry = catalog_entry(lipid_class, community, path)
        entries.append(entry)
        bundles[entry["source"]].append(lipid_class)
        (OUT / entry["file"]).write_text(json.dumps([lipid_class], indent=2, ensure_ascii=False),
                                         encoding="utf-8")

    for name, classes in bundles.items():
        (OUT / "bundles" / f"{name}.json").write_text(
            json.dumps(classes, indent=2, ensure_ascii=False), encoding="utf-8")
    index = {
        "formatVersion": 1,
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "enums": lipidlib.ENUMS,
        "chainLabels": lipidlib.CHAIN_LABELS,
        "categoryLabels": lipidlib.CATEGORY_LABELS,
        "classes": entries,
    }
    (OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
    print(f"Built catalog with {len(entries)} classes into {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
