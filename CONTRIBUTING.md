# Contributing lipid classes

## The easy way: submission form

1. Build and test your class in mzmine (**Lipid annotation → Custom lipid classes → Add…**).
2. Select it and click **Export…** to save it as `.json`.
3. Open a [submission](https://github.com/mzmine/mzmine-custom-lipid-library/issues/new?template=submit-lipid-class.yml),
   paste the file content and fill in the description.

A bot checks the class within a minute. If there is a problem, it comments on your issue: edit the
issue to fix it and the check runs again. If the class is valid, the bot opens a pull request and a
maintainer reviews it.

## With git

Add one file per class to `classes/community/<id>.json`. The file is the mzmine export (a JSON list
with one class) plus a `_meta` block, which mzmine ignores on import:

```json
[
  {
    "name": "...", "abbr": "...", "coreClass": "...", "mainClass": "...",
    "backBoneFormula": "...", "chainTypes": ["..."], "fragmentationRules": [ ... ],
    "_meta": {
      "id": "same-as-file-name",
      "version": "1.0.0",
      "description": "What the class is and how it was validated.",
      "authors": [{ "name": "Jane Doe", "orcid": "0000-0000-0000-0000", "github": "janedoe" }],
      "references": [{ "doi": "10.xxxx/yyyy" }],
      "instrument": "Orbitrap Exploris 240, ESI, HCD 30",
      "tags": ["polyol lipids"],
      "minMzmineVersion": "4.12.0",
      "rightsHolder": "mzio GmbH",
      "license": "mzmine custom lipid library terms of use",
      "licenseUrl": "https://github.com/mzmine/mzmine-custom-lipid-library/blob/main/LICENSE.md",
      "contributorAgreement": "CONTRIBUTOR_AGREEMENT.md v1"
    }
  }
]
```

Run `python scripts/validate.py` before opening the pull request and tick the Contributor Agreement
checkbox in the pull request description.

## Fragmentation rule formulas

Chain plus/minus formula rules accept a plain formula like `C3H5O` or a **signed formula** that adds
and removes atoms at once, e.g. `+O2-H2` (two more O and two fewer H than the chain). Classes using
signed formulas or the extended chain rule types need a recent mzmine version; the check reminds you
to set `minMzmineVersion`.

## Review checklist for maintainers

- The description says what the class covers and how it was validated (standards, spectra).
- Rule ratings are sensible: MAJOR rules alone are enough to annotate the class.
- The class does not duplicate a built-in or existing community class.
- Warnings from the check are understood or fixed.
- For pull requests not created by the submission bot: the author ticked the Contributor Agreement
  checkbox. Do not merge without it.

## Rights

Every contribution is covered by the [Contributor Agreement](CONTRIBUTOR_AGREEMENT.md): you grant
mzio GmbH exclusive rights to your class, keep the right to use it for your own research, and are
named as its author. Only submit classes you created or have the right to share.
