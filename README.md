# mzmine custom lipid library

A community library of **custom lipid classes** for rule-based lipid annotation in
[mzmine](https://github.com/mzmine/mzmine).

**Browse the catalog:** https://mzmine.github.io/mzmine-custom-lipid-library/

Every file in this repository can be imported into mzmine as it is.

## Use a class in mzmine

1. Find a class in the [catalog](https://mzmine.github.io/mzmine-custom-lipid-library/) and click
   **Download for mzmine**. Select several classes to download them as one file.
2. In mzmine open **Lipid annotation → Custom lipid classes → Import…** and choose the file.

Direct links for tools and scripts:

| What | URL |
|---|---|
| Catalog of all classes | `https://mzmine.github.io/mzmine-custom-lipid-library/index.json` |
| One class | `https://mzmine.github.io/mzmine-custom-lipid-library/classes/<id>.json` |
| All community classes | `https://mzmine.github.io/mzmine-custom-lipid-library/bundles/community.json` |
| All built-in classes | `https://mzmine.github.io/mzmine-custom-lipid-library/bundles/builtin.json` |

## Share your class

[Submit a lipid class](https://github.com/mzmine/mzmine-custom-lipid-library/issues/new?template=submit-lipid-class.yml):
paste the JSON you exported from mzmine and describe the class. The class is checked
automatically and a maintainer reviews it. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Repository layout

| Path | Content |
|---|---|
| `classes/community/` | Classes shared by the community, one class per file |
| `classes/builtin/` | Classes that ship with mzmine, as templates (generated, do not edit) |
| `schema/` | Allowed values synced from mzmine and a JSON schema for editors |
| `scripts/` | Validation, catalog build and submission handling (Python standard library only) |
| `site/` | The catalog website |

Check and build locally:

```bash
python scripts/validate.py
python scripts/build_site.py && python -m http.server -d _site
```

## Rights and terms of use

The community lipid classes and the library are owned by **mzio GmbH**. You may download them and
use them in mzmine to analyze your data, academic or commercial, and publish your results freely.
Redistributing the classes or reusing them in other tools needs permission. See the
[terms of use](LICENSE.md).

Contributors grant mzio GmbH exclusive rights to their classes and are credited as authors, see the
[Contributor Agreement](CONTRIBUTOR_AGREEMENT.md).

Built-in classes in `classes/builtin/` are part of mzmine and MIT licensed. The code in this
repository is MIT licensed.
