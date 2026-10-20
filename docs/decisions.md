# Decisions & open questions

Running log of decisions made during the build. The locked planning gates are in `spec-v1.0.md` section 3.

## Build decisions

| Date | Decision | Why |
|---|---|---|
| 2026-10-20 | Added `data/roster.json` (the 27 IDs from spec section 4) | The validator needs to tell "card not written yet" apart from "typo / no such ID" |
| 2026-10-20 | Missing roster cards are **warnings** by default and **errors** with `--strict` | In Phase 1 only 3 cards exist, so every edge to an unwritten card would otherwise fail the build. Phase 2 exit test = `python -m pipeline.validate --strict` passes |
| 2026-10-20 | Sourced values may be `null` (value, source, confidence, verified) while a card is a draft | Spec 6.2: the draft model "may write `null` but may not invent". `approved` cards must have `source` and `verified` |
| 2026-10-20 | Concentration label vs. market shares mismatch is a warning, not an error | Shares are often partial or estimated; Dan makes the call |

## Open questions

1. **Tier-distance rule (spec 5.5) conflicts with HBM.** The rule says a card may not reference a tier more than two steps away. But HBM (T4) is made with EUV/DUV scanners and deposition/etch tools (T1), which are 3 tiers away. The spec's own HBM example lists `deposition-etch` and `duv-lithography` as inputs. The validator treats this as a **warning** for now. Options:
   - (a) Drop the rule
   - (b) Keep it, but allow T1 equipment to feed any fab-like tier (T2, T4)
   - (c) Keep it strict, and drop the T1 -> HBM edges from the map
2. **Search API** for `SearchProvider`: Tavily, Exa, or SerpAPI (spec 10.1).
3. **`grid-power`**: own card, or a note on `dc-colocation` (spec 10.2)?
4. **Domain name and site title** (spec 10.3).
