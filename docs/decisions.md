# Decisions & open questions

Running log of decisions made during the build. The locked planning gates are in `spec-v1.0.md` section 3.

## Build decisions

| Date | Decision | Why |
|---|---|---|
| 2026-10-20 | Added `data/roster.json` (the 27 IDs from spec section 4) | The validator needs to tell "card not written yet" apart from "typo / no such ID" |
| 2026-10-20 | Missing roster cards are **warnings** by default and **errors** with `--strict` | In Phase 1 only 3 cards exist, so every edge to an unwritten card would otherwise fail the build. Phase 2 exit test = `python -m pipeline.validate --strict` passes |
| 2026-10-20 | Sourced values may be `null` (value, source, confidence, verified) while a card is a draft | Spec 6.2: the draft model "may write `null` but may not invent". `approved` cards must have `source` and `verified` |
| 2026-10-20 | Concentration label vs. market shares mismatch is a warning, not an error | Shares are often partial or estimated; Dan makes the call |
| 2026-10-20 | **Gate: tier-distance rule.** Keep the 2-tier limit (spec 5.5), but T1 equipment may feed any tier that runs fabs (T2, T4). Too-far links are now errors | HBM (T4) really is made with T1 tools; the rule still blocks odd links. Lives in `pipeline/validate.py` (`tier_link_allowed`) |
| 2026-10-20 | **Gate: search API.** Tavily for `SearchProvider` (settles spec 10.1) | Built for AI agents, returns page text, free tier to start. Lives in `pipeline/providers/tavily.py` |
| 2026-10-20 | **Gate: draft model.** DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash`) | Cheapest option. Risk of broken JSON or guesses is covered by schema-check + retry in `draft.py` and by the verify step. Lives in `pipeline/config.py` |
| 2026-10-20 | **Gate: verify model.** GPT-6.1 Sol (`openai/gpt-6.1-sol`), $2 / $10 per M tokens | Top-tier, different family from the drafter, about half the cost of Opus 5.5 (~$10 per full 27-card run). Lives in `pipeline/config.py` |
| 2026-10-21 | **Gate: site layers.** The map is the home page and the star. The story is told *on* the map (a step-through of the 9 tiers), cards sit one layer down, and each card has its own layers (quick read, detail, "for experts") | The map is the thesis; a separate story page would hide it. Replaces the "thesis paragraph below the map" in spec 7.2 |
| 2026-10-21 | **Gate: mobile map.** Phones and upright tablets get a vertical map (a timeline, top to bottom, story text inside each tier); screens 1100px and wider get the horizontal map | Replaces the spec 7.2 "list on mobile" fallback so phone visitors still see the map. Lines are drawn only on the horizontal map; on the timeline, tapping a box lights its path instead |
| 2026-10-21 | **Gate: visual style.** Clean "engineering blueprint" look with a colour per tier and gentle motion (flowing lines, glowing active tier). Motion is off when the device asks for reduced motion | Serious enough for experts, alive enough for a portfolio. Node colour = tier (not concentration as in spec 7.2); concentration shows as a badge on the card |
| 2026-10-21 | **Gate: domain and title.** `supplychain.aiautomations.ai`, titled "The AI Supply Chain", tagline "From EUV scanner to inference API. Every number sourced." | Plain and searchable. Settles spec 10.3 |
| 2026-10-21 | Map shows all 27 roster components, not only written cards. Planned links live in `roster.json` (`planned_customers`) and follow the same graph rules; a written card's own `inputs`/`customers` replace them | A 3-node map can't tell the start-to-finish story. The validator checks planned links too |
| 2026-10-21 | Story text and short box labels live in `data/story.json` | Words can be edited without touching code. Narrative only, no numbers: numbers stay in sourced cards |
| 2026-10-21 | Map drawn with plain JavaScript + SVG, not D3 | The layout is a fixed tier grid laid out by CSS; D3 would add a dependency for nothing. Spec 7.1 |

## Open questions

1. **`grid-power`**: own card, or a note on `dc-colocation` (spec 10.2)? Decide when T7 research starts.
2. **Search API key.** `TAVILY_API_KEY` is not set in the cloud environment yet, so `draft.py` can't search. Add it before the research step.
