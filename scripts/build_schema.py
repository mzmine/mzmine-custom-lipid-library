"""Writes schema/lipid-class.schema.json from schema/enums.json for editor support.

The Python validator in lipidlib.py is the reference; the schema helps when editing files by hand.
"""
from __future__ import annotations

import json

import lipidlib


def names(key: str) -> list[str]:
    values = lipidlib.ENUMS[key]
    return values if isinstance(values[0], str) else [v["name"] for v in values]


def main() -> None:
    # reload in case enums.json was just replaced by import_builtin.py
    lipidlib.ENUMS.clear()
    lipidlib.ENUMS.update(json.loads((lipidlib.ROOT / "schema" / "enums.json").read_text("utf-8")))
    rule = {
        "type": "object",
        "required": ["polarityType", "ionizationType"],
        "properties": {
            "polarityType": {"enum": ["POSITIVE", "NEGATIVE"]},
            "ionizationType": {"enum": names("IonizationType")},
            "lipidFragmentationRuleType": {"enum": names("LipidFragmentationRuleType")},
            "lipidFragmentInformationLevelType": {"enum": names("LipidAnnotationLevel")},
            "molecularFormula": {
                "type": "string",
                "description": "Formula of the rule. Chain plus/minus formula rules also accept "
                               "signed formulas like +O2-H2.",
            },
            "lipidFragmentationRuleRating": {"enum": names("LipidFragmentationRuleRating")},
            "relativeIntensityWeight": {"type": "integer", "minimum": 0, "maximum": 100},
        },
    }
    meta = {
        "type": "object",
        "required": ["id", "description", "authors"],
        "properties": {
            "id": {"type": "string", "pattern": "^[a-z0-9]+(-[a-z0-9]+)*$"},
            "source": {"enum": ["community", "builtin"]},
            "version": {"type": "string"},
            "description": {"type": "string", "minLength": 1},
            "authors": {"type": "array", "minItems": 1, "items": {
                "type": "object", "required": ["name"],
                "properties": {"name": {"type": "string"}, "orcid": {"type": "string"},
                               "github": {"type": "string"}}}},
            "references": {"type": "array", "items": {
                "type": "object",
                "properties": {"doi": {"type": "string"}, "url": {"type": "string"},
                               "citation": {"type": "string"}}}},
            "instrument": {"type": "string"},
            "tags": {"type": "array", "items": {"type": "string"}},
            "minMzmineVersion": {"type": "string"},
            "submission": {"type": "string"},
            "rightsHolder": {"type": "string"},
            "license": {"type": "string"},
            "licenseUrl": {"type": "string"},
            "contributorAgreement": {"type": "string"},
        },
    }
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "mzmine custom lipid class file",
        "description": "A JSON list with one lipid class as exported by mzmine, plus a _meta "
                       "block that mzmine ignores on import.",
        "type": "array", "minItems": 1, "maxItems": 1,
        "items": {
            "type": "object",
            "required": ["name", "abbr", "coreClass", "mainClass", "backBoneFormula",
                         "chainTypes", "fragmentationRules"],
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "abbr": {"type": "string", "minLength": 1},
                "coreClass": {"enum": names("LipidCategories")},
                "mainClass": {"enum": names("LipidMainClasses")},
                "backBoneFormula": {"type": "string", "minLength": 1},
                "chainTypes": {"type": "array", "items": {"enum": names("LipidChainType")}},
                "fragmentationRules": {"type": "array", "minItems": 1, "items": rule},
                "_meta": meta,
            },
        },
    }
    path = lipidlib.ROOT / "schema" / "lipid-class.schema.json"
    path.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
