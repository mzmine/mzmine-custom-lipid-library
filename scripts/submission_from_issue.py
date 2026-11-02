"""Turns a lipid class submission issue into class files in classes/community.

Reads the issue form body from the ISSUE_BODY environment variable. Writes the created file
paths to created_files.txt and a markdown report to submission_report.md. Exits with 1 if the
submission is invalid.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import lipidlib

NO_RESPONSE = "_No response_"


def parse_issue_form(body: str) -> dict[str, str]:
    """Splits an issue form body into {label: value}."""
    fields: dict[str, str] = {}
    for block in re.split(r"^### ", body, flags=re.MULTILINE)[1:]:
        label, _, value = block.partition("\n")
        value = value.strip()
        fields[label.strip()] = "" if value == NO_RESPONSE else value
    return fields


def strip_code_fence(text: str) -> str:
    m = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, flags=re.DOTALL)
    return m.group(1) if m else text


def parse_references(text: str) -> list[dict]:
    refs = []
    for line in text.splitlines():
        line = line.strip(" -*\t")
        if not line:
            continue
        doi = re.search(r"\b(10\.\d{4,9}/\S+)", line)
        if line.startswith(("http://", "https://")) and not doi:
            refs.append({"url": line})
        elif doi and line.startswith(("http://", "https://")):
            refs.append({"doi": doi.group(1).rstrip(".,;")})
        elif doi:
            refs.append({"doi": doi.group(1).rstrip(".,;"), "citation": line})
        else:
            refs.append({"citation": line})
    return refs


def unique_id(base: str, taken: set[str]) -> str:
    candidate, i = base, 2
    while candidate in taken or (lipidlib.COMMUNITY_DIR / f"{candidate}.json").exists():
        candidate, i = f"{base}-{i}", i + 1
    return candidate


def main() -> int:
    fields = parse_issue_form(os.environ.get("ISSUE_BODY", ""))
    issue_url = os.environ.get("ISSUE_URL", "")
    github_user = os.environ.get("ISSUE_AUTHOR", "")
    report_lines: list[str] = []
    created: list[Path] = []

    try:
        data = json.loads(strip_code_fence(fields.get("Lipid class JSON", "")))
    except json.JSONDecodeError as e:
        report_lines.append(f"- The lipid class JSON could not be read: `{e}`")
        data = None
    classes = data if isinstance(data, list) else [data] if isinstance(data, dict) else []
    if data is not None and not classes:
        report_lines.append("- The JSON does not contain a lipid class.")

    author = {"name": fields.get("Author name", "").strip()}
    if fields.get("ORCID (optional)"):
        author["orcid"] = fields["ORCID (optional)"].strip()
    if github_user:
        author["github"] = github_user
    tags = [t.strip() for t in fields.get("Tags (optional)", "").split(",") if t.strip()]

    agreement = fields.get("Contributor agreement", "")
    if not re.search(r"- \[[xX]\]", agreement):
        report_lines.append("- Please accept the Contributor Agreement (tick the checkbox).")

    existing = {}
    for path in lipidlib.COMMUNITY_DIR.glob("*.json"):
        c = lipidlib.load_class_file(path)[0]
        existing[f"{c.get('abbr')}|{c.get('name')}".lower()] = path.stem

    taken: set[str] = set()
    ok = not report_lines
    for lipid_class in classes:
        if not isinstance(lipid_class, dict):
            report_lines.append("- Every entry of the JSON list must be a lipid class object.")
            ok = False
            continue
        lipid_class.pop("_meta", None)
        class_id = unique_id(lipidlib.slugify(f"{lipid_class.get('abbr', '')} "
                                              f"{lipid_class.get('name', 'lipid-class')}"), taken)
        taken.add(class_id)
        meta = {
            "id": class_id,
            "source": "community",
            "version": "1.0.0",
            "description": fields.get("Description", "").strip(),
            "authors": [author],
            "references": parse_references(fields.get("References (optional)", "")),
            "instrument": fields.get("Tested on (optional)", "").strip(),
            "tags": tags,
            "submission": issue_url,
            "rightsHolder": lipidlib.RIGHTS_HOLDER,
            "license": lipidlib.TERMS,
            "licenseUrl": lipidlib.TERMS_URL,
            "contributorAgreement": lipidlib.CONTRIBUTOR_AGREEMENT,
        }
        if lipidlib.requires_extended_rules(lipid_class):
            meta["minMzmineVersion"] = lipidlib.EXTENDED_RULES_MIN_MZMINE
        lipid_class["_meta"] = meta

        path = lipidlib.COMMUNITY_DIR / f"{class_id}.json"
        path.write_text(json.dumps([lipid_class], indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
        report = lipidlib.validate_file(path, community=True)
        name = f"**{lipid_class.get('abbr', '?')}** {lipid_class.get('name', '')}"
        duplicate = existing.get(f"{lipid_class.get('abbr')}|{lipid_class.get('name')}".lower())
        if duplicate:
            report.error(f"a class with the same name and abbreviation already exists: {duplicate}. "
                         "Please choose another name or abbreviation.")
        if report.errors:
            ok = False
            path.unlink()
            report_lines.append(f"- {name}: ❌ needs changes")
            report_lines += [f"  - {e}" for e in report.errors]
        else:
            created.append(path)
            report_lines.append(f"- {name}: ✅ valid")
        report_lines += [f"  - ⚠️ {w}" for w in report.warnings]

    if not ok:
        # decision: write nothing unless the whole submission is valid
        for path in created:
            path.unlink(missing_ok=True)
        created = []
    Path("created_files.txt").write_text(
        "\n".join(str(p.relative_to(lipidlib.ROOT)) for p in created), encoding="utf-8")
    header = ("All classes are valid. A pull request for review is on its way."
              if ok else "Some problems were found. Please edit this issue to fix them; "
                         "the check runs again automatically.")
    Path("submission_report.md").write_text(
        f"### Lipid class check\n\n{header}\n\n" + "\n".join(report_lines) + "\n",
        encoding="utf-8")
    print("\n".join(report_lines))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
