# Maintainer notes

## One-time repository setup

1. Settings → Pages → Source: **GitHub Actions**.
2. Settings → Actions → General → Workflow permissions: **Read and write**, and enable
   **Allow GitHub Actions to create and approve pull requests** (needed by the submission bot).
3. Create the label `lipid-class-submission` (the issue form and the bot use it).
4. Protect `main` and require the *Validate lipid classes* check for pull requests.

Pull requests opened by the submission bot do not trigger other workflows (GitHub rule for
`GITHUB_TOKEN`). The bot validates the class itself; to re-run the full check, run
*Validate lipid classes* manually on the branch.

## Updating the built-in classes and allowed values

When mzmine adds lipid classes, chain types, rule types or ionization types, export them from mzmine
(a JSON list per built-in class in `builtin/` plus `enums.json` with all enum values), then run:

```bash
python scripts/import_builtin.py <export-dir> <mzmine-version>
python scripts/validate.py
```

`import_builtin.py` also regenerates `schema/lipid-class.schema.json`.
Update `EXTENDED_RULES_MIN_MZMINE` in `scripts/lipidlib.py` once the release with the extended chain
rules is out.
