"""Build the static site (spec section 7) from data/ into site/dist/.

Usage (run it as a file: "site" is also the name of a built-in Python module, so `-m` won't work):
    python site/build.py            # build into site/dist/
    python site/build.py --out DIR  # build somewhere else

Then preview it:
    python -m http.server -d site/dist 8000    # open http://localhost:8000
"""

import argparse
import json
import shutil
import sys
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

SITE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SITE_DIR.parent))

from pipeline.data import DATA_DIR, load_components, load_json, load_roster, load_tiers  # noqa: E402

DEFAULT_OUT = SITE_DIR / "dist"
DOMAIN = "supplychain.aiautomations.ai"

# Spec 5.4: the rule each concentration label stands for.
CONCENTRATION_RULES = {
    "monopoly": "One maker holds 90% or more.",
    "duopoly": "Two makers hold 85% or more combined.",
    "oligopoly": "Three to five makers hold 75% or more combined.",
    "competitive": "No small group of makers dominates.",
}
CONFIDENCE_TEXT = {
    "high": "Primary source, recent, corroborated.",
    "medium": "One credible source, or slightly dated.",
    "low": "Estimate, inference, or a single secondary source.",
}


# ---------- helpers used by the templates ----------

def freshness(verified, today: date) -> str:
    """Spec 7.3: green <= 90 days, amber 90-180, red > 180, none if never verified."""
    if not verified:
        return "none"
    age = (today - date.fromisoformat(verified)).days
    return "green" if age <= 90 else "amber" if age <= 180 else "red"


def format_value(sv) -> str:
    """Render a sourced value's number for people. Returns '' when there is no number yet."""
    if not isinstance(sv, dict) or sv.get("value") is None:
        return ""
    value, unit = sv["value"], sv.get("unit") or ""
    if unit == "share":
        return f"{value * 100:.0f}%"
    if unit == "index":
        return f"{value:,.0f}"
    return f"{value:,} {unit}".strip()


def format_band(band, unit) -> str:
    if not isinstance(band, dict) or band.get("low") is None:
        return ""
    cur = "$" if band.get("currency") == "USD" else f"{band.get('currency', '')} "
    low, high = band["low"], band.get("high")
    text = f"{cur}{low:,}" if high in (None, low) else f"{cur}{low:,} to {cur}{high:,}"
    return f"{text} {unit or ''}".strip()


# ---------- the graph ----------

def build_graph(tiers, roster, components, story):
    """One node per roster entry, edges from cards where written, else from the roster plan."""
    tier_ids = [t["id"] for t in tiers]
    nodes = []
    for r in roster:
        card = components.get(r["id"])
        nodes.append({
            "id": r["id"],
            "tier": r["tier"],
            "name": card["name"] if card else r["name"],
            "label": story["labels"].get(r["id"], r["name"]),
            "makers": ", ".join(m["company"] for m in card["makers"]) if card and card.get("makers") else r["primary_makers"],
            "summary": (card or {}).get("summary") or "",
            "status": card["meta"]["status"] if card else "planned",
            "concentration": (card or {}).get("concentration", {}).get("label"),
        })

    edges = set()
    for r in roster:
        card = components.get(r["id"])
        if card:
            edges.update((r["id"], c) for c in card.get("customers", []))
            edges.update((i, r["id"]) for i in card.get("inputs", []))
        else:
            edges.update((r["id"], c) for c in r.get("planned_customers", []))
    known = {n["id"] for n in nodes}
    edges = sorted((a, b) for a, b in edges if a in known and b in known)

    nodes.sort(key=lambda n: tier_ids.index(n["tier"]))
    return nodes, [{"from": a, "to": b} for a, b in edges]


# ---------- build ----------

def page_root(depth: int) -> str:
    """Relative path back to the site root, so the site works at any URL (or straight from disk)."""
    return "../" * depth if depth else "./"


def build(out: Path = DEFAULT_OUT, data_dir: Path = DATA_DIR, today: date | None = None) -> Path:
    today = today or date.today()
    tiers = load_tiers(data_dir)
    roster = load_roster(data_dir)
    components = load_components(data_dir)
    story = load_json(data_dir / "story.json")
    nodes, edges = build_graph(tiers, roster, components, story)
    node_by_id = {n["id"]: n for n in nodes}
    tier_by_id = {t["id"]: t for t in tiers}

    env = Environment(
        loader=FileSystemLoader(SITE_DIR / "templates"),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["value"] = format_value
    env.filters["fresh"] = lambda v: freshness(v, today)
    env.globals.update(
        story=story, tiers=tiers, tier_by_id=tier_by_id, node_by_id=node_by_id,
        rules=CONCENTRATION_RULES, confidence_text=CONFIDENCE_TEXT, format_band=format_band,
        built_on=today.isoformat(), domain=DOMAIN,
    )

    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(SITE_DIR / "static", out / "static")

    def render(template, path, depth, **ctx):
        target = out / path
        target.parent.mkdir(parents=True, exist_ok=True)
        ctx.setdefault("root", page_root(depth))
        html = env.get_template(template).render(**ctx)
        target.write_text(html, encoding="utf-8")

    bundle = {"tiers": tiers, "nodes": nodes, "edges": edges, "story": story}
    (out / "components.json").write_text(json.dumps(bundle, indent=1), encoding="utf-8")

    # "<\/" keeps any text in the data from closing the <script> tag it is embedded in.
    render("index.html", "index.html", 0, bundle_json=json.dumps(bundle).replace("</", "<\\/"), page="map")
    render("about.html", "about/index.html", 1, page="about")
    # GitHub Pages serves 404.html at any missing URL, so its links must start from the domain root.
    render("404.html", "404.html", 0, page="404", root="/")

    for i, tier in enumerate(tiers):
        render(
            "tier.html", f"t/{tier['id']}/index.html", 2, page="tier", tier=tier,
            nodes=[n for n in nodes if n["tier"] == tier["id"]],
            prev=tiers[i - 1] if i > 0 else None,
            next=tiers[i + 1] if i + 1 < len(tiers) else None,
        )

    for node in nodes:
        card = components.get(node["id"])
        render(
            "component.html", f"c/{node['id']}/index.html", 2, page="component", node=node, card=card,
            roster_entry=next(r for r in roster if r["id"] == node["id"]),
            fed_by=[node_by_id[e["from"]] for e in edges if e["to"] == node["id"]],
            feeds=[node_by_id[e["to"]] for e in edges if e["from"] == node["id"]],
        )
        if card:
            (out / "c" / node["id"] / "card.json").write_text(json.dumps(card, indent=2), encoding="utf-8")

    (out / "CNAME").write_text(DOMAIN + "\n")
    (out / ".nojekyll").write_text("")
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    out = build(args.out)
    print(f"Built {sum(1 for _ in out.rglob('*.html'))} pages into {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
