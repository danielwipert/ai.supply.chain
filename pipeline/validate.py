"""Validate data/ against the spec (sections 5.2-5.5).

Usage:
    python -m pipeline.validate            # Phase 1: missing roster cards are warnings
    python -m pipeline.validate --strict   # Phase 2+: missing roster cards are errors

Exits with code 1 if there are any errors.
"""

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

from jsonschema import Draft202012Validator

from pipeline.data import DATA_DIR, load_components, load_roster, load_schema, load_tiers

# Spec 5.5: a component may not reference a tier more than this many steps away.
MAX_TIER_DISTANCE = 2
# Exception (docs/decisions.md, gate 2026-10-20): fab equipment may feed any tier that runs fabs.
EQUIPMENT_TIER = "T1"
FAB_TIERS = {"T2", "T4"}


def tier_link_allowed(tier_a: str, tier_b: str, tier_order: dict) -> bool:
    if {tier_a, tier_b} & {EQUIPMENT_TIER} and {tier_a, tier_b} & FAB_TIERS:
        return True
    return abs(tier_order[tier_a] - tier_order[tier_b]) <= MAX_TIER_DISTANCE


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def iter_sourced_values(node, path=""):
    """Yield (path, obj) for every sourced value (any dict with a 'confidence' key)."""
    if isinstance(node, dict):
        if "confidence" in node and "source" in node:
            yield path, node
        for key, child in node.items():
            yield from iter_sourced_values(child, f"{path}.{key}" if path else key)
    elif isinstance(node, list):
        for i, child in enumerate(node):
            yield from iter_sourced_values(child, f"{path}[{i}]")


def expected_label(shares: list[float]) -> str:
    """Spec 5.4: work out the concentration label from market shares (0-1)."""
    shares = sorted(shares, reverse=True)
    if shares and shares[0] >= 0.90:
        return "monopoly"
    if len(shares) >= 2 and sum(shares[:2]) >= 0.85:
        return "duopoly"
    if len(shares) >= 3 and sum(shares[:5]) >= 0.75:
        return "oligopoly"
    return "competitive"


def check_card(cid: str, card: dict, schema_validator, tier_ids: set, roster: dict, report: Report):
    """Checks that only need this one card."""
    for err in schema_validator.iter_errors(card):
        where = "/".join(str(p) for p in err.absolute_path) or "(root)"
        report.errors.append(f"{cid}: schema: {where}: {err.message}")

    if card.get("id") != cid:
        report.errors.append(f"{cid}: 'id' is {card.get('id')!r} but the file is named {cid}.json")
    if cid not in roster:
        report.errors.append(f"{cid}: not in data/roster.json")
    elif card.get("tier") != roster[cid]["tier"]:
        report.errors.append(f"{cid}: tier {card.get('tier')} does not match roster tier {roster[cid]['tier']}")
    if card.get("tier") not in tier_ids:
        report.errors.append(f"{cid}: tier {card.get('tier')!r} is not in data/tiers.json")

    # Every sourced value must point to a real source; approved cards need source + verified.
    source_ids = [s.get("id") for s in card.get("sources", [])]
    for dup in {s for s in source_ids if source_ids.count(s) > 1}:
        report.errors.append(f"{cid}: source id {dup} is used more than once")
    approved = card.get("meta", {}).get("status") == "approved"
    for path, sv in iter_sourced_values(card):
        if sv.get("source") and sv["source"] not in source_ids:
            report.errors.append(f"{cid}: {path} cites {sv['source']}, which is not in 'sources'")
        if approved:
            if not sv.get("source"):
                report.errors.append(f"{cid}: approved card but {path} has no source")
            if not sv.get("verified"):
                report.errors.append(f"{cid}: approved card but {path} has no verified date")
    if approved and not card["meta"].get("approved_by"):
        report.errors.append(f"{cid}: approved card has no meta.approved_by")

    # Concentration label vs. market shares (warning only: shares can be partial).
    shares = [m["market_share"]["value"] for m in card.get("makers", [])
              if isinstance(m.get("market_share"), dict) and m["market_share"].get("value") is not None]
    label = card.get("concentration", {}).get("label")
    if label and shares and len(shares) == len(card.get("makers", [])):
        if sum(shares) > 1.0001:
            report.errors.append(f"{cid}: market shares add up to more than 100%")
        elif expected_label(shares) != label:
            report.warnings.append(
                f"{cid}: label is '{label}' but the market shares suggest '{expected_label(shares)}'"
            )


def check_graph(components: dict, roster: dict, tier_order: dict, strict: bool, report: Report):
    """Spec 5.5 graph rules."""
    for cid, card in components.items():
        for field_name, reverse_name in (("inputs", "customers"), ("customers", "inputs")):
            for ref in card.get(field_name, []):
                if ref == cid:
                    report.errors.append(f"{cid}: lists itself in '{field_name}'")
                    continue
                if ref not in components:
                    if ref in roster:
                        msg = f"{cid}: {field_name} -> {ref}: card not written yet"
                        (report.errors if strict else report.warnings).append(msg)
                    else:
                        report.errors.append(f"{cid}: {field_name} -> {ref}: no such component ID")
                    continue
                # Both directions must agree.
                if cid not in components[ref].get(reverse_name, []):
                    report.errors.append(
                        f"{cid}: lists {ref} in '{field_name}', but {ref} does not list {cid} in '{reverse_name}'"
                    )

        # Tier distance.
        my_tier = card.get("tier")
        for ref in card.get("inputs", []) + card.get("customers", []):
            ref_tier = (components.get(ref) or roster.get(ref) or {}).get("tier")
            if my_tier in tier_order and ref_tier in tier_order and not tier_link_allowed(my_tier, ref_tier, tier_order):
                report.errors.append(
                    f"{cid} ({my_tier}) -> {ref} ({ref_tier}): more than {MAX_TIER_DISTANCE} tiers apart"
                )


def validate(data_dir: Path = DATA_DIR, strict: bool = False) -> Report:
    report = Report()

    tiers = load_tiers(data_dir)
    tier_ids = [t["id"] for t in tiers]
    if len(set(tier_ids)) != len(tier_ids):
        report.errors.append("tiers.json: duplicate tier IDs")
    tier_order = {t["id"]: t["order"] for t in tiers}

    roster_list = load_roster(data_dir)
    roster = {r["id"]: r for r in roster_list}
    if len(roster) != len(roster_list):
        report.errors.append("roster.json: duplicate component IDs")
    for r in roster_list:
        if r["tier"] not in tier_order:
            report.errors.append(f"roster.json: {r['id']} has unknown tier {r['tier']}")

    schema_validator = Draft202012Validator(load_schema(data_dir))
    components = load_components(data_dir)
    for cid, card in components.items():
        check_card(cid, card, schema_validator, set(tier_ids), roster, report)
    check_graph(components, roster, tier_order, strict, report)

    if strict:
        for missing in sorted(set(roster) - set(components)):
            report.errors.append(f"roster: {missing} has no card in data/components/")

    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--strict", action="store_true", help="treat missing roster cards as errors")
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    args = parser.parse_args(argv)

    report = validate(args.data_dir, strict=args.strict)
    for w in report.warnings:
        print(f"WARNING  {w}")
    for e in report.errors:
        print(f"ERROR    {e}")
    n_cards = len(load_components(args.data_dir))
    print(f"\n{n_cards} card(s) checked: {len(report.errors)} error(s), {len(report.warnings)} warning(s)")
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
