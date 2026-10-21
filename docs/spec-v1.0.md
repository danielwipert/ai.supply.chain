# AI Supply Chain Map — Product Spec v1.0

**Project:** AI Supply Chain Map (working title)
**Owner:** Dan Wipert, Chorus AI Systems
**Status:** Spec locked 2026-10-19 — ready for Phase 1 build
**Version:** 1.1 (amended 2026-10-21: model tributary added, see section 2.4 and `docs/decisions.md`)

---

## 1. Purpose

A public website and a set of PDFs that map the AI compute supply chain component by component. For every component the site answers five questions:

1. **What is it?** — what the component does in the chain
2. **Who makes it, and where?** — companies and countries
3. **Is it a monopoly?** — a concentration label backed by market-share numbers
4. **What does it cost?** — unit price or price band
5. **Where does it flow?** — what feeds it, and what it feeds

Every number carries a dated source, a confidence rating, and a last-verified date. The site is meant to be citable; the PDFs are meant to be forwarded.

**Positioning:** Most AI supply chain coverage is either a single explainer article or a paywalled analyst deck. This is a maintained, sourced, open reference you can click through from the EUV scanner to the inference API.

---

## 2. Scope

### 2.1 In scope for v1 — the compute spine

Nine tiers, upstream to downstream:

| Tier | Name | What it covers |
|---|---|---|
| T1 | Lithography & fab equipment | The machines that make chips |
| T2 | Wafer fabrication | Leading-edge logic foundries |
| T3 | Chip design | GPUs and AI accelerators |
| T4 | Memory | High-bandwidth memory (HBM) |
| T5 | Advanced packaging | Joining logic and memory into one package |
| T6 | Servers & networking | GPU nodes and the fabric between them |
| T7 | Data centers & power | Buildings, cooling, electrical, grid |
| T8 | Compute providers | Neoclouds and hyperscalers renting GPU hours |
| T9 | Inference | Token-serving providers and serving engines |

### 2.2 Deferred to v2

- **Upstream raw materials:** silicon wafers, photoresists, specialty gases (neon, helium), rare earths, substrates
- **Model layer extras:** distillation and fine-tuning services (the core model layer moved into v1.1, section 2.4)
- **Sub-components within tiers:** optical transceivers, transformers, switchgear, cooling distribution units, power generation

v2 materials slot in as T0 without changing the schema.

### 2.4 v1.1 amendment: the model tributary

Added 2026-10-21. The map has two streams that merge:

| Tier | Stream | Name | What it covers |
|---|---|---|---|
| T1–T8 | compute | (as in 2.1) | Fab tools to compute providers |
| D1 | data | Training inputs | Data, human feedback and the software models are trained with |
| T9 | trunk | Model training | Where compute and data meet: trained models |
| T10 | trunk | Inference | Serving models (was T9 in v1.0) |
| T11 | trunk | Applications | The AI products people use |

New components (10): `web-crawl-data`, `licensed-content`, `human-data`, `ml-frameworks` (D1);
`frontier-models`, `open-weight-models` (T9); `model-apis` (T10); `chat-assistants`, `coding-agents`,
`enterprise-ai` (T11). The roster is now 37 components; `data/roster.json` is the source of truth.

### 2.3 Out of scope

- Live pricing feeds, stock data, or financial analysis of the companies
- Forecasting or scenario modeling
- Non-AI semiconductor supply chains (mobile, automotive)

---

## 3. Decision Log

All eight planning gates locked 2026-10-19.

| # | Gate | Decision | Why |
|---|---|---|---|
| 1 | Scope | Compute spine, T1–T9 | Sharpest monopoly and cost story; materials and models are v2 |
| 2 | Unit of record | Sourced card | Dated source, confidence, and last-verified date on every number make it citable |
| 3 | Depth | ~25 components | Chokepoints plus key challengers at each tier; finishable |
| 4 | Data model | One JSON file per component, in-repo | Matches the Chorus spine; `inputs`/`customers` references produce the graph for free |
| 5 | Site structure | Interactive flow map home + one page per component | The map is the thesis; the pages are the evidence |
| 6 | PDF outputs | Full report + one brief per tier | Briefs get shared; the report is the reference; same generator, two templates |
| 7 | Research pipeline | LLM-drafted, LLM-verified, human-approved | Generator-verifier pattern; nothing ships unapproved |
| 8 | Build phases | Thin slice first (3 cards end to end) | Find schema problems on card 3, not card 25 |

---

## 4. Component Roster (v1)

Twenty-seven components. Each tier lists the chokepoint first, then alternatives. The pipeline (Section 6) fills in the numbers; this table is the plan, not the data.

| ID | Tier | Component | Primary maker(s) | Alternatives / challengers |
|---|---|---|---|---|
| `euv-lithography` | T1 | EUV lithography scanners | ASML (NL) | None |
| `duv-lithography` | T1 | DUV lithography scanners | ASML | Nikon, Canon (JP) |
| `deposition-etch` | T1 | Deposition & etch equipment | Applied Materials, Lam Research (US) | Tokyo Electron (JP) |
| `leading-edge-fab` | T2 | Leading-edge logic fabrication (3nm/2nm class) | TSMC (TW) | — |
| `samsung-foundry` | T2 | Samsung Foundry | Samsung (KR) | challenger to TSMC |
| `intel-foundry` | T2 | Intel Foundry | Intel (US) | challenger to TSMC |
| `nvidia-gpu` | T3 | Nvidia data center GPUs (Hopper, Blackwell) | Nvidia (US) | — |
| `amd-instinct` | T3 | AMD Instinct accelerators (MI300/MI350 class) | AMD (US) | challenger to Nvidia |
| `google-tpu` | T3 | Google TPU | Google with Broadcom (US) | hyperscaler custom silicon |
| `aws-trainium` | T3 | AWS Trainium / Inferentia | Amazon Annapurna Labs (US) | hyperscaler custom silicon |
| `microsoft-maia` | T3 | Microsoft Maia | Microsoft (US) | hyperscaler custom silicon |
| `inference-asics` | T3 | Inference-specialized silicon | Groq, Cerebras (US) | startup challengers |
| `hbm` | T4 | High-bandwidth memory (HBM3E / HBM4) | SK Hynix (KR) | Samsung (KR), Micron (US) |
| `cowos-packaging` | T5 | CoWoS advanced packaging | TSMC (TW) | — |
| `alt-packaging` | T5 | Alternative advanced packaging | Intel (Foveros/EMIB) | ASE, Amkor (OSATs) |
| `gpu-servers-oem` | T6 | Branded GPU servers | Supermicro, Dell, HPE (US) | — |
| `gpu-servers-odm` | T6 | ODM GPU servers | Foxconn, Quanta, Wiwynn (TW) | alternative to OEMs |
| `nvlink-infiniband` | T6 | NVLink & InfiniBand interconnect | Nvidia / Mellanox (US) | — |
| `ethernet-fabric` | T6 | AI Ethernet fabric | Broadcom, Arista (US) | challenger to InfiniBand |
| `dc-colocation` | T7 | Data center colocation & build | Equinix, Digital Realty, QTS, Vantage | — |
| `liquid-cooling` | T7 | Liquid cooling systems | Vertiv (US) | Schneider, CoolIT, others |
| `power-equipment` | T7 | Electrical equipment (transformers, switchgear, UPS) | Siemens, Schneider, Eaton, ABB | — |
| `grid-power` | T7 | Grid power & interconnection | Regional utilities | on-site generation |
| `neoclouds` | T8 | Neoclouds | CoreWeave, Lambda, Nebius, Crusoe | — |
| `hyperscalers` | T8 | Hyperscaler GPU capacity | AWS, Azure, GCP, Oracle | alternative to neoclouds |
| `inference-providers` | T9 | Open-weight inference providers | Together, Fireworks, Groq, DeepInfra, Baseten | — |
| `serving-engines` | T9 | Serving engines & aggregation | vLLM, SGLang, TensorRT-LLM; OpenRouter | open-source / aggregator |

Rules for the roster:

- A component is a **product category**, not a company. Nvidia appears because "Nvidia data center GPUs" is the category; the card lists Nvidia as the maker.
- Where one company owns a category outright (ASML EUV, TSMC CoWoS), the component and the company are effectively the same thing; the card says so.
- Hyperscaler custom silicon gets separate cards because each has a different fab, packaging, and HBM path, and the flow map needs those edges.

---

## 5. Data Model

### 5.1 Repository layout

```
ai-supply-chain/
  data/
    tiers.json                 # the nine tiers, ordered
    components/
      euv-lithography.json
      hbm.json
      ...                      # one file per component
  pipeline/                    # research scripts (Section 6)
  site/                        # static site build (Section 7)
  pdf/                         # PDF build (Section 8)
  docs/                        # this spec, runbook
```

### 5.2 Component file schema

One JSON file per component. Every numeric field is a **sourced value** (5.3), not a bare number.

```json
{
  "id": "hbm",
  "tier": "T4",
  "name": "High-bandwidth memory (HBM3E / HBM4)",
  "summary": "Stacked DRAM placed next to the GPU die. Every modern AI accelerator needs it, and only three companies make it.",
  "what_it_does": "Two or three paragraphs, plain English.",

  "makers": [
    {
      "company": "SK Hynix",
      "country": "KR",
      "hq_city": "Icheon",
      "fab_locations": ["Icheon, KR", "Cheongju, KR"],
      "market_share": { "value": 0.0, "unit": "share", "source": "src-001", "confidence": "medium", "verified": "2026-10-19" }
    }
  ],

  "concentration": {
    "label": "oligopoly",
    "hhi": { "value": 0, "unit": "index", "source": "src-001", "confidence": "low", "verified": "2026-10-19" },
    "note": "Why this label. One or two sentences."
  },

  "cost": {
    "unit": "per GB",
    "price_band": { "low": 0, "high": 0, "currency": "USD", "source": "src-002", "confidence": "low", "verified": "2026-10-19" },
    "note": "What the number represents and what it excludes."
  },

  "lead_time": { "value": 0, "unit": "weeks", "source": "src-003", "confidence": "low", "verified": "2026-10-19" },

  "inputs": ["deposition-etch", "duv-lithography"],
  "customers": ["nvidia-gpu", "amd-instinct", "google-tpu", "aws-trainium"],

  "chokepoint_notes": "Why this component matters to the chain. Geopolitical exposure, single points of failure.",

  "sources": [
    {
      "id": "src-001",
      "title": "Exact page or report title",
      "publisher": "Who published it",
      "url": "https://...",
      "date": "2026-09-15",
      "accessed": "2026-10-19",
      "type": "analyst | company-filing | news | government | academic"
    }
  ],

  "meta": {
    "status": "draft | verified | approved",
    "drafted_by": "model-id",
    "verified_by": "model-id",
    "approved_by": "dan",
    "approved_on": "2026-10-19",
    "last_refreshed": "2026-10-19"
  }
}
```

### 5.3 Sourced value

Every number in a card is an object, never a bare number:

| Field | Meaning |
|---|---|
| `value` | The number |
| `unit` | What it's measured in |
| `source` | ID of an entry in the card's `sources` list |
| `confidence` | `high` — primary source, recent, corroborated. `medium` — one credible source or slightly dated. `low` — estimate, inference, or single secondary source |
| `verified` | Date a human last confirmed the number against the source |

A card cannot reach `approved` status with any sourced value missing a `source` or `verified`.

### 5.4 Concentration labels

| Label | Rule |
|---|---|
| `monopoly` | One maker holds ≥ 90% |
| `duopoly` | Two makers hold ≥ 85% combined |
| `oligopoly` | Three to five makers hold ≥ 75% combined |
| `competitive` | None of the above |

HHI is recorded when calculable, but the label is the thing readers see.

### 5.5 Graph rules

- `inputs` and `customers` reference component IDs only. The build fails if a reference points to a missing ID.
- Every `customers` entry on component A must appear as an `inputs` entry on component B. The build checks both directions.
- A component may reference components in the same tier (Ethernet fabric sits inside GPU servers) but may not reference a tier more than two steps away.

---

## 6. Research Pipeline

### 6.1 Pattern

Generator-verifier with a human approval gate. Nothing reaches `approved` without Dan.

```
draft  →  verify  →  review  →  approve  →  commit
(cheap)   (top-tier)   (Dan)     (Dan)
```

### 6.2 Steps

**Step 1 — Draft.** `pipeline/draft.py <component-id>`

- Loads the roster entry and the schema.
- Runs 5–10 web searches per card (makers, market share, pricing, lead times, fab locations).
- A cheap model (via OpenRouter) fills the card from the search results. Every number must cite a URL from the results; the model is told it may write `null` but may not invent.
- Writes `data/components/<id>.json` with `meta.status = "draft"`.

**Step 2 — Verify.** `pipeline/verify.py <component-id>`

- A top-tier model receives the draft card and the fetched text of every cited source.
- For each sourced value it answers: does the source actually say this? Is the number current? Is the confidence rating fair?
- Produces a verification report (`pipeline/reports/<id>.md`) listing passes, failures, and suggested corrections. Failures are applied as proposed edits, not committed.
- Sets `meta.status = "verified"` if no hard failures.

**Step 3 — Review and approve.** Dan reads the card and the verification report together, edits the JSON by hand where needed, and sets `meta.status = "approved"` with his name and the date. Then commits.

**Step 4 — Refresh.** `pipeline/refresh.py --all`

- Re-runs draft + verify on every approved card, writes results to a `refresh/` branch, and opens a pull request with a per-card diff and the new verification reports.
- Dan reviews the diff, merges what's right. Nothing changes on `main` without the merge.
- Cadence: monthly by GitHub Actions. Can also be run on one card at a time.

### 6.3 Provider abstraction

Python `Protocol` interfaces, as everywhere in Chorus:

- `LLMProvider` — `complete(prompt, model) -> str`. Implementation: OpenRouter.
- `SearchProvider` — `search(query) -> list[Result]`. Implementation: one paid search API (Tavily, Exa, or SerpAPI; pick in Phase 1).
- `FetchProvider` — `fetch(url) -> str`. Implementation: plain requests + readability extraction.

All three swap without touching the pipeline.

### 6.4 Models

- Draft: cheapest capable model on OpenRouter.
- Verify: top-tier model.
- Many small calls: one call per section of the card, not one call for the whole card.

---

## 7. Site

### 7.1 Stack

- **Static site, built by Python.** `site/build.py` reads `data/`, renders Jinja2 templates to `site/dist/`, deployed to GitHub Pages by Actions on every push to `main`.
- **Flow map:** D3.js, one JavaScript file, reads `components.json` (a bundle the build script writes from the per-component files).
- **No framework.** Twenty-seven pages and one diagram don't need Next.js. Tailwind via CDN or a single hand-written stylesheet.

### 7.2 Pages

**Home — the flow map**

- Nine columns left to right, one per tier.
- One node per component. Node color = concentration label (monopoly darkest, competitive lightest). Node size = fixed in v1.
- Edges drawn from `inputs`/`customers`. Hover a node: highlight its edges and dim the rest. Click: go to the component page.
- Below the map: a one-paragraph thesis and a "Chokepoints" strip showing the monopoly and duopoly nodes.
- Mobile: columns stack vertically into a scrollable list grouped by tier; the map itself is desktop-first.

**Component page — `/c/<id>/`**

Sections, in order:

1. Name, tier, one-line summary, concentration badge
2. What it does
3. Who makes it — table of makers with country, locations, market share, each number showing its confidence and verified date on hover
4. Concentration — label, rule it met, note
5. Cost — price band, unit, note
6. Flow — "Fed by" and "Feeds" lists linking to neighbor cards, plus a mini three-column map (inputs / this / customers)
7. Why it matters — chokepoint notes
8. Sources — numbered list, every one linked, with date and type
9. Card metadata — status, last refreshed

**Tier page — `/t/<id>/`**

Tier name, a paragraph, and its components as cards. Prev/next tier links.

**About / Methodology — `/about/`**

What the confidence ratings mean, how concentration labels are computed, how the pipeline works, how to report an error. Links to the PDFs.

### 7.3 Freshness display

Every sourced value renders with a small marker: green (verified ≤ 90 days), amber (90–180), red (> 180). Same convention as TokenTicker.

---

## 8. PDFs

### 8.1 Generator

`pdf/build.py` renders Jinja2 HTML templates from `data/` and converts them with WeasyPrint. Same data, same template language as the site, so a card can't say one thing on the web and another in print.

### 8.2 Outputs

**Full report — `AI_Supply_Chain_Map_<date>.pdf`**

1. Cover with date and version
2. Thesis page
3. Flow map as a static SVG (exported from the same D3 layout, or a hand-drawn SVG in Phase 1)
4. Chokepoints summary — one table of every monopoly and duopoly
5. Tier sections T1–T9, each with its component cards in full
6. Sources appendix, numbered across the whole document
7. Methodology

**Tier briefs — `Brief_T4_Memory_<date>.pdf`, one per tier**

3–5 pages: tier overview, flow mini-map, the tier's cards, sources. Designed to be posted or emailed on their own.

### 8.3 Build rule

PDFs are rebuilt by Actions whenever `main` changes and attached to a GitHub Release tagged with the date. The site's About page links to the latest release.

---

## 9. Build Phases

Each phase ends with something runnable.

### Phase 1 — Thin slice (end to end)

- Repo, schema, `tiers.json`, validation script for graph rules (5.5)
- Pipeline draft + verify for three cards: `euv-lithography`, `leading-edge-fab`, `hbm`
- Dan approves all three
- Flow map rendering those three nodes and their edges; component pages for all three
- One tier brief (T4 Memory) built by the PDF generator
- GitHub Pages deploy working

**Exit test:** open the site, click HBM on the map, land on a card where every number has a source and a verified date, and open a PDF brief that matches it.

### Phase 2 — Fill the roster

- Run the pipeline on the remaining 24 cards, one tier at a time, upstream to downstream
- Dan approves each tier before the next starts
- Tier pages live as each tier completes

**Exit test:** all 27 cards approved, graph validation passes with no missing references.

### Phase 3 — Polish and refresh

- Flow map: hover highlighting, chokepoint strip, mobile fallback
- Full report PDF and all nine tier briefs
- Monthly refresh workflow in Actions, opening a reviewed PR
- About / Methodology page
- Freshness markers

**Exit test:** a refresh run opens a PR with a readable diff, and the full report builds from `main` without manual steps.

---

## 10. Open Questions (to settle during Phase 1)

1. Which search API for `SearchProvider` — settle by trying one on the three Phase 1 cards.
2. Whether `grid-power` is a real card or a note on `dc-colocation` — decide once the T7 research starts.
3. Domain name and site title.

---

## 11. Success Criteria for v1

- Every one of the 27 cards is `approved` with no unsourced numbers.
- A reader can trace a path from `euv-lithography` to `inference-providers` on the map with no dead ends.
- The full report and nine briefs build from the same data with zero hand edits.
- A refresh run produces a diff Dan can review in under an hour.
