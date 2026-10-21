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
  providers/               # LLM (OpenRouter), search (Tavily), fetch (readability)
  check_providers.py       # one real call to each provider, to test your keys
  reports/                 # verification reports (pipeline output)
  story.json               # the words of the map's story + short box labels
site/                      # static website (see site/README.md)
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

## Preview the website

```bash
python site/build.py                       # build the pages into site/dist/
python -m http.server -d site/dist 8000    # then open http://localhost:8000
```

More in [`site/README.md`](site/README.md).

## API keys

The research pipeline needs two keys, set as environment variables. Never put them in the code.

| Variable | Used for | Get one at |
|---|---|---|
| `OPENROUTER_API_KEY` | LLM calls (draft + verify) | openrouter.ai → Keys |
| `TAVILY_API_KEY` | Web search | tavily.com → dashboard |

In a Claude Code cloud session, add them in the environment settings (the environment menu in the session's title bar → Edit), then start a new session. On your own computer, run `export TAVILY_API_KEY=...` in the terminal first.

To check the keys work (one tiny real call to each service):

```bash
python -m pipeline.check_providers
```

## Phase 1 progress

- [x] Repo layout, schema, `tiers.json`, roster, validator
- [x] Skeleton cards for `euv-lithography`, `leading-edge-fab`, `hbm` (no numbers yet)
- [x] Pipeline: provider interfaces (LLM, search, fetch) in `pipeline/providers/`
- [ ] Pipeline: `draft.py` and `verify.py` on the three cards
- [ ] Dan approves the three cards
- [x] Site: flow map with built-in story, tier pages, component pages, method page
- [ ] PDF: T4 Memory tier brief
- [x] GitHub Pages deploy workflow (`.github/workflows/deploy-site.yml`)
- [ ] Turn on GitHub Pages + point `supplychain.aiautomations.ai` at it
