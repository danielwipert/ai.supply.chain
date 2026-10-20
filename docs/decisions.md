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
| 2026-10-20 | **Gate: search API.** Tavily for `SearchProvider` (settles spec 10.1) | Built for AI agents, returns page text, free tier to start. Lives in `pipeline/providers/` (coming) |

## Open questions

1. **`grid-power`**: own card, or a note on `dc-colocation` (spec 10.2)? Decide when T7 research starts.
2. **Domain name and site title** (spec 10.3).
