# AI Supply Chain Map

A sourced, maintained map of the AI compute supply chain, from the EUV scanner to the inference API. Every number has a dated source, a confidence rating, and a last-verified date.

- Full spec: [`docs/spec-v1.0.md`](docs/spec-v1.0.md)
- Build decisions & open questions: [`docs/decisions.md`](docs/decisions.md)

## Repo layout

```
data/
  tiers.json               # the nine tiers, in order (T1-T9)
  roster.json              # the 27 planned components (spec section 4)
  schema/
    component.schema.json  # what a component card must look like
  components/
    <id>.json              # one card per component
pipeline/                  # research + validation scripts
  data.py                  # loads data/ (shared by site and PDF builds)
  validate.py              # checks schema + graph rules
  reports/                 # verification reports (pipeline output)
site/                      # static site build (coming)
pdf/                       # PDF build (coming)
tests/                     # pytest tests
docs/                      # spec, decisions
```

## Getting started

1. Install the Python packages (one time):

   ```bash
   pip install -r requirements.txt
   ```

2. Check that all the data is valid:

   ```bash
   python -m pipeline.validate
   ```

   - `ERROR` lines mean something is broken and must be fixed.
   - `WARNING` lines are OK during Phase 1. Most of them say "card not written yet".
   - Add `--strict` to turn "card not written yet" into errors. That is the Phase 2 exit test.

3. Run the tests:

   ```bash
   python -m pytest
   ```

GitHub Actions runs steps 2 and 3 on every push.

## Phase 1 progress

- [x] Repo layout, schema, `tiers.json`, roster, validator
- [x] Skeleton cards for `euv-lithography`, `leading-edge-fab`, `hbm` (no numbers yet)
- [ ] Pipeline: provider interfaces (LLM, search, fetch)
- [ ] Pipeline: `draft.py` and `verify.py` on the three cards
- [ ] Dan approves the three cards
- [ ] Site: flow map + component pages
- [ ] PDF: T4 Memory tier brief
- [ ] GitHub Pages deploy
