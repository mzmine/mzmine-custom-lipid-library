"""Shared helpers to read, validate and describe mzmine custom lipid class files.

Only uses the Python standard library so it runs anywhere without installing packages.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLASSES_DIR = ROOT / "classes"
COMMUNITY_DIR = CLASSES_DIR / "community"
BUILTIN_DIR = CLASSES_DIR / "builtin"
ENUMS = json.loads((ROOT / "schema" / "enums.json").read_text(encoding="utf-8"))

RIGHTS_HOLDER = "mzio GmbH"
TERMS = "mzmine custom lipid library terms of use"
TERMS_URL = "https://github.com/mzmine/mzmine-custom-lipid-library/blob/main/LICENSE.md"
CONTRIBUTOR_AGREEMENT = "CONTRIBUTOR_AGREEMENT.md v1"

# assumption: the chain rule types added in 2026 and signed formulas like +O2-H2 ship with this
# mzmine version. Update once the release is out.
EXTENDED_RULES_MIN_MZMINE = "4.12.0"

# rule types that existed before the extended chain rules
LEGACY_RULE_TYPES = {
    "HEADGROUP_FRAGMENT", "HEADGROUP_FRAGMENT_NL", "ACYLCHAIN_FRAGMENT", "ACYLCHAIN_FRAGMENT_NL",
    "ACYLCHAIN_PLUS_FORMULA_FRAGMENT", "ACYLCHAIN_PLUS_FORMULA_FRAGMENT_NL",
    "ACYLCHAIN_MINUS_FORMULA_FRAGMENT", "ACYLCHAIN_MINUS_FORMULA_FRAGMENT_NL",
    "TWO_ACYLCHAINS_PLUS_FORMULA_FRAGMENT", "ALKYLCHAIN_FRAGMENT", "ALKYLCHAIN_FRAGMENT_NL",
    "ALKYLCHAIN_PLUS_FORMULA_FRAGMENT", "ALKYLCHAIN_PLUS_FORMULA_FRAGMENT_NL",
    "ALKYLCHAIN_MINUS_FORMULA_FRAGMENT", "ALKYLCHAIN_MINUS_FORMULA_FRAGMENT_NL",
    "SPHINGOLIPID_MONO_HYDROXY_BACKBONE_CHAIN_FRAGMENT",
    "SPHINGOLIPID_DI_HYDROXY_BACKBONE_CHAIN_FRAGMENT",
    "SPHINGOLIPID_TRI_HYDROXY_BACKBONE_CHAIN_FRAGMENT",
    "SPHINGOLIPID_MONO_HYDROXY_BACKBONE_CHAIN_PLUS_FORMULA_FRAGMENT_NL",
    "SPHINGOLIPID_DI_HYDROXY_BACKBONE_CHAIN_PLUS_FORMULA_FRAGMENT_NL",
    "SPHINGOLIPID_TRI_HYDROXY_BACKBONE_CHAIN_PLUS_FORMULA_FRAGMENT_NL",
    "SPHINGOLIPID_MONO_HYDROXY_BACKBONE_CHAIN_MINUS_FORMULA_FRAGMENT_NL",
    "SPHINGOLIPID_DI_HYDROXY_BACKBONE_CHAIN_MINUS_FORMULA_FRAGMENT_NL",
    "SPHINGOLIPID_TRI_HYDROXY_BACKBONE_CHAIN_MINUS_FORMULA_FRAGMENT_NL",
    "SPHINGOLIPID_MONO_HYDROXY_BACKBONE_CHAIN_PLUS_FORMULA_FRAGMENT",
    "SPHINGOLIPID_DI_HYDROXY_BACKBONE_CHAIN_PLUS_FORMULA_FRAGMENT",
    "SPHINGOLIPID_TRI_HYDROXY_BACKBONE_CHAIN_PLUS_FORMULA_FRAGMENT",
    "SPHINGOLIPID_MONO_HYDROXY_BACKBONE_CHAIN_MINUS_FORMULA_FRAGMENT",
    "SPHINGOLIPID_DI_HYDROXY_BACKBONE_CHAIN_MINUS_FORMULA_FRAGMENT",
    "SPHINGOLIPID_TRI_HYDROXY_BACKBONE_CHAIN_MINUS_FORMULA_FRAGMENT",
    "AMID_CHAIN_FRAGMENT", "AMID_CHAIN_FRAGMENT_NL", "AMID_CHAIN_PLUS_FORMULA_FRAGMENT",
    "AMID_CHAIN_PLUS_FORMULA_FRAGMENT_NL", "AMID_CHAIN_MINUS_FORMULA_FRAGMENT",
    "AMID_CHAIN_MINUS_FORMULA_FRAGMENT_NL", "AMID_MONO_HYDROXY_CHAIN_FRAGMENT",
    "AMID_MONO_HYDROXY_CHAIN_PLUS_FORMULA_FRAGMENT", "AMID_MONO_HYDROXY_CHAIN_MINUS_FORMULA_FRAGMENT",
    "PRECURSOR",
}

# prefix of a rule type -> chain type the rule refers to (mirrors LipidFragmentationRuleType)
RULE_CHAIN_PREFIXES = [
    ("ACYL_MONO_HYDROXY_CHAIN_", "ACYL_MONO_HYDROXY_CHAIN"),
    ("ACYLCHAIN_", "ACYL_CHAIN"),
    ("TWO_ACYLCHAINS_", "TWO_ACYL_CHAINS_COMBINED"),
    ("ALKYLCHAIN_", "ALKYL_CHAIN"),
    ("SPHINGOLIPID_MONO_HYDROXY_BACKBONE_CHAIN_", "SPHINGOLIPID_MONO_HYDROXY_BACKBONE_CHAIN"),
    ("SPHINGOLIPID_DI_HYDROXY_BACKBONE_CHAIN_", "SPHINGOLIPID_DI_HYDROXY_BACKBONE_CHAIN"),
    ("SPHINGOLIPID_TRI_HYDROXY_BACKBONE_CHAIN_", "SPHINGOLIPID_TRI_HYDROXY_BACKBONE_CHAIN"),
    ("AMID_MONO_HYDROXY_CHAIN_", "AMID_MONO_HYDROXY_CHAIN"),
    ("AMID_CHAIN_", "AMID_CHAIN"),
]

CHAIN_LABELS = {
    "ACYL_CHAIN": "Acyl chain",
    "ACYL_MONO_HYDROXY_CHAIN": "Acyl mono-hydroxy chain",
    "TWO_ACYL_CHAINS_COMBINED": "Two acyl chains combined",
    "ALKYL_CHAIN": "Alkyl chain",
    "AMID_CHAIN": "Amid chain",
    "AMID_MONO_HYDROXY_CHAIN": "Amid mono-hydroxy chain",
    "SPHINGOLIPID_MONO_HYDROXY_BACKBONE_CHAIN": "Sphingoid base (1 OH)",
    "SPHINGOLIPID_DI_HYDROXY_BACKBONE_CHAIN": "Sphingoid base (2 OH)",
    "SPHINGOLIPID_TRI_HYDROXY_BACKBONE_CHAIN": "Sphingoid base (3 OH)",
}

CATEGORY_LABELS = {
    "FATTYACYLS": "Fatty acyls", "GLYCEROLIPIDS": "Glycerolipids",
    "GLYCEROPHOSPHOLIPIDS": "Glycerophospholipids", "SPHINGOLIPIDS": "Sphingolipids",
    "STEROLLIPIDS": "Sterol lipids", "PRENOLLIPIDS": "Prenol lipids",
    "SACCHAROLIPIDS": "Saccharolipids", "POLYKETIDES": "Polyketides",
}

# monoisotopic masses of the major isotopes
MONOISOTOPIC = {
    "H": 1.00782503207, "D": 2.0141017778, "T": 3.0160492777, "Li": 7.016004548,
    "B": 11.0093054, "C": 12.0, "N": 14.0030740048, "O": 15.99491461956, "F": 18.99840322,
    "Na": 22.9897692809, "Mg": 23.985041699, "Si": 27.9769265325, "P": 30.97376163,
    "S": 31.972071, "Cl": 34.96885268, "K": 38.96370668, "Ca": 39.96259098, "Fe": 55.9349375,
    "Cu": 62.9295975, "Zn": 63.9291422, "Se": 79.9165213, "Br": 78.9183371, "I": 126.904473,
}
ELECTRON_MASS = 0.00054857990946

_ELEMENT = r"(?:\[\d+[A-Z][a-z]?\]|[A-Z][a-z]?)\d*"
_FORMULA = re.compile(rf"^(?:{_ELEMENT})+$")
_CHARGED_FORMULA = re.compile(rf"^\[?((?:{_ELEMENT})+)\]?(\d*[+-]|[+-]\d*)?$")
_SIGNED_FORMULA = re.compile(r"^[+-]?[^+-]+(?:[+-][^+-]+)*$")
_SIGNED_PART = re.compile(r"([+-])([^+-]+)")
_ELEMENT_COUNT = re.compile(r"(\[\d+[A-Z][a-z]?\]|[A-Z][a-z]?)(\d*)")


def chain_type_of_rule(rule_type: str) -> str | None:
    """Chain type the rule refers to or None for head group and precursor rules."""
    for prefix, chain in RULE_CHAIN_PREFIXES:
        if rule_type.startswith(prefix):
            return chain
    return None


def is_chain_formula_rule(rule_type: str) -> bool:
    return "_PLUS_FORMULA_" in rule_type or "_MINUS_FORMULA_" in rule_type


def requires_formula(rule_type: str) -> bool:
    return rule_type in ("HEADGROUP_FRAGMENT", "HEADGROUP_FRAGMENT_NL") or is_chain_formula_rule(
        rule_type)


def parse_counts(formula: str) -> dict[str, int] | None:
    """Element counts of an uncharged formula or None if it cannot be parsed."""
    if not _FORMULA.match(formula):
        return None
    counts: dict[str, int] = {}
    for symbol, n in _ELEMENT_COUNT.findall(formula):
        element = re.sub(r"[\[\]\d]", "", symbol)
        if element not in MONOISOTOPIC:
            return None
        counts[element] = counts.get(element, 0) + (int(n) if n else 1)
    return counts


def is_valid_formula(formula: str, allow_charge: bool = True) -> bool:
    formula = re.sub(r"\s+", "", formula)
    if allow_charge:
        m = _CHARGED_FORMULA.match(formula)
        return bool(m) and parse_counts(m.group(1)) is not None
    return parse_counts(formula) is not None


def is_signed_formula(formula: str) -> bool:
    """True if the formula adds and removes atoms, like +O2-H2 (mirrors LipidChainFormulaModification)."""
    f = re.sub(r"\s+", "", formula)
    return bool(_SIGNED_FORMULA.match(f)) and ("-" in f.lstrip("+-") or f.startswith("-"))


def is_valid_chain_formula(formula: str) -> bool:
    f = re.sub(r"\s+", "", formula)
    if not f:
        return False
    if not _SIGNED_FORMULA.match(f):
        # legacy formula with trailing charge like C2H-
        return is_valid_formula(f, allow_charge=True)
    signed = f if f[0] in "+-" else "+" + f
    parts = _SIGNED_PART.findall(signed)
    return all(parse_counts(p) is not None for _, p in parts)


def monoisotopic_mass(formula: str) -> float | None:
    counts = parse_counts(re.sub(r"\s+", "", formula))
    if counts is None:
        return None
    return sum(MONOISOTOPIC[e] * n for e, n in counts.items())


def describe_rule(rule: dict) -> str:
    """Human readable description of a fragmentation rule."""
    rule_type = rule.get("lipidFragmentationRuleType") or ""
    formula = (rule.get("molecularFormula") or "").strip()
    if not rule_type:
        return "Adduct only (MS1, no fragment)"
    if rule_type == "PRECURSOR":
        return "Precursor ion"
    if rule_type == "HEADGROUP_FRAGMENT":
        return f"Head group fragment ion {formula}"
    if rule_type == "HEADGROUP_FRAGMENT_NL":
        return f"Neutral loss of {formula} from the precursor"
    chain = CHAIN_LABELS.get(chain_type_of_rule(rule_type) or "", "Chain")
    modification = ""
    if "_PLUS_FORMULA_" in rule_type:
        modification = f" + {formula}" if not is_signed_formula(formula) else f" {formula}"
    elif "_MINUS_FORMULA_" in rule_type:
        modification = f" − {formula}" if not is_signed_formula(formula) else f" − ({formula})"
    if rule_type.endswith("_NL"):
        return f"Neutral loss of {chain[0].lower() + chain[1:]}{modification} from the precursor"
    text = chain + modification
    return f"{text} fragment ion"


def requires_extended_rules(lipid_class: dict) -> bool:
    for rule in lipid_class.get("fragmentationRules") or []:
        if (rule.get("lipidFragmentationRuleType") or "PRECURSOR") not in LEGACY_RULE_TYPES:
            return True
        formula = rule.get("molecularFormula") or ""
        if is_chain_formula_rule(rule.get("lipidFragmentationRuleType") or "") and is_signed_formula(
                formula):
            return True
    return False


@dataclass
class Report:
    path: Path
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def load_class_file(path: Path) -> list:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_class(lipid_class: dict, report: Report, community: bool) -> None:
    """Checks one lipid class object as exported by mzmine plus the _meta block."""
    names = {k: set(v if isinstance(v[0], str) else [x["name"] for x in v]) for k, v in
             ENUMS.items()}
    main_class_category = {m["name"]: m["category"] for m in ENUMS["LipidMainClasses"]}
    ion_polarity = {i["name"]: i["polarity"] for i in ENUMS["IonizationType"]}

    for key in ("name", "abbr", "backBoneFormula"):
        if not isinstance(lipid_class.get(key), str) or not lipid_class[key].strip():
            report.error(f"'{key}' is missing or empty")
    if lipid_class.get("coreClass") not in names["LipidCategories"]:
        report.error(f"unknown coreClass '{lipid_class.get('coreClass')}'")
    if lipid_class.get("mainClass") not in names["LipidMainClasses"]:
        report.error(f"unknown mainClass '{lipid_class.get('mainClass')}'")
    elif main_class_category[lipid_class["mainClass"]] != lipid_class.get("coreClass"):
        report.warn(f"mainClass '{lipid_class['mainClass']}' belongs to category "
                    f"'{main_class_category[lipid_class['mainClass']]}', not "
                    f"'{lipid_class.get('coreClass')}'")
    backbone = lipid_class.get("backBoneFormula")
    if isinstance(backbone, str) and backbone.strip() and not is_valid_formula(backbone, False):
        report.error(f"backBoneFormula '{backbone}' is not a valid formula")

    chains = lipid_class.get("chainTypes")
    if not isinstance(chains, list):
        report.error("'chainTypes' must be a list")
        chains = []
    for chain in chains:
        if chain not in names["LipidChainType"]:
            report.error(f"unknown chain type '{chain}'")

    rules = lipid_class.get("fragmentationRules")
    if not isinstance(rules, list) or not rules:
        report.error("'fragmentationRules' must be a non-empty list")
        rules = []
    for i, rule in enumerate(rules, start=1):
        where = f"rule {i}"
        rule_type = rule.get("lipidFragmentationRuleType")
        polarity = rule.get("polarityType")
        ion = rule.get("ionizationType")
        if rule_type is None:
            # decision: a rule with only polarity and ionization declares an MS1 adduct
            if ion not in ion_polarity:
                report.error(f"{where}: unknown ionizationType '{ion}'")
            continue
        if rule_type not in names["LipidFragmentationRuleType"]:
            report.error(f"{where}: unknown rule type '{rule_type}'")
            continue
        if polarity not in ("POSITIVE", "NEGATIVE"):
            report.error(f"{where}: polarityType must be POSITIVE or NEGATIVE")
        if ion not in ion_polarity:
            report.error(f"{where}: unknown ionizationType '{ion}'")
        elif polarity in ("POSITIVE", "NEGATIVE") and ion_polarity[ion] != polarity:
            report.error(f"{where}: ionization '{ion}' is {ion_polarity[ion]} but rule is {polarity}")
        if rule.get("lipidFragmentInformationLevelType") not in names["LipidAnnotationLevel"]:
            report.error(f"{where}: unknown annotation level "
                         f"'{rule.get('lipidFragmentInformationLevelType')}'")
        if rule.get("lipidFragmentationRuleRating") not in names["LipidFragmentationRuleRating"]:
            report.error(f"{where}: rating must be MAJOR or MINOR")
        weight = rule.get("relativeIntensityWeight", 0)
        if not isinstance(weight, int) or not 0 <= weight <= 100:
            report.error(f"{where}: relativeIntensityWeight must be an integer 0-100")

        formula = (rule.get("molecularFormula") or "").strip()
        if requires_formula(rule_type) and not formula:
            report.error(f"{where}: rule type {rule_type} requires a molecularFormula")
        elif formula and is_chain_formula_rule(rule_type):
            if not is_valid_chain_formula(formula):
                report.error(f"{where}: '{formula}' is not a valid formula. Use e.g. C3H5O or +O2-H2")
        elif formula and requires_formula(rule_type) and not is_valid_formula(formula):
            report.error(f"{where}: '{formula}' is not a valid formula")

        chain = chain_type_of_rule(rule_type)
        if chain == "TWO_ACYL_CHAINS_COMBINED":
            if chains.count("ACYL_CHAIN") < 2:
                report.warn(f"{where}: {rule_type} expects at least two ACYL_CHAIN chain types")
        elif chain and chain not in chains:
            report.warn(f"{where}: {rule_type} refers to {chain}, which is not in chainTypes")
        if rule_type.startswith("SPHINGOLIPID_") and lipid_class.get("coreClass") != "SPHINGOLIPIDS":
            report.warn(f"{where}: sphingolipid specific rule in a non-sphingolipid class")

    meta = lipid_class.get("_meta")
    if community:
        if not isinstance(meta, dict):
            report.error("community classes need a '_meta' block, see CONTRIBUTING.md")
            return
        if meta.get("id") != report.path.stem:
            report.error(f"_meta.id '{meta.get('id')}' must match the file name '{report.path.stem}'")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", str(meta.get("id", ""))):
            report.error("_meta.id must be lowercase letters, digits and dashes")
        authors = meta.get("authors")
        if not isinstance(authors, list) or not authors or not all(
                isinstance(a, dict) and a.get("name") for a in authors):
            report.error("_meta.authors needs at least one author with a name")
        if not str(meta.get("description", "")).strip():
            report.error("_meta.description is missing")
        if meta.get("rightsHolder") != RIGHTS_HOLDER:
            report.error(f"_meta.rightsHolder must be '{RIGHTS_HOLDER}'")
        if not meta.get("contributorAgreement"):
            report.error("_meta.contributorAgreement is missing: contributors must accept "
                         "CONTRIBUTOR_AGREEMENT.md")
        if requires_extended_rules(lipid_class) and not meta.get("minMzmineVersion"):
            report.warn("uses extended chain rules or signed formulas: set _meta.minMzmineVersion "
                        f"to {EXTENDED_RULES_MIN_MZMINE}")


def validate_file(path: Path, community: bool) -> Report:
    report = Report(path)
    try:
        data = load_class_file(path)
    except (OSError, json.JSONDecodeError) as e:
        report.error(f"cannot read JSON: {e}")
        return report
    # decision: files are a JSON list with exactly one class so that mzmine can import them directly
    if not isinstance(data, list) or len(data) != 1 or not isinstance(data[0], dict):
        report.error("file must be a JSON list with exactly one lipid class, as exported by mzmine")
        return report
    validate_class(data[0], report, community)
    return report


def all_class_files() -> list[tuple[Path, bool]]:
    files = [(p, True) for p in sorted(COMMUNITY_DIR.glob("*.json"))]
    files += [(p, False) for p in sorted(BUILTIN_DIR.glob("*.json"))]
    return files


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
