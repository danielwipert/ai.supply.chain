"""Tests for site/build.py: every page is built, every internal link works, and sourced numbers render."""

import importlib.util
import json
import re
import shutil
from datetime import date
from pathlib import Path

import pytest

from pipeline.data import DATA_DIR, load_roster, load_tiers

REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("site_build", REPO / "site" / "build.py")
site_build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site_build)


@pytest.fixture(scope="module")
def dist(tmp_path_factory):
    return site_build.build(tmp_path_factory.mktemp("dist"))


def test_every_page_is_built(dist):
    assert (dist / "index.html").exists()
    assert (dist / "about" / "index.html").exists()
    for tier in load_tiers():
        assert (dist / "t" / tier["id"] / "index.html").exists()
    for entry in load_roster():
        assert (dist / "c" / entry["id"] / "index.html").exists()


def test_internal_links_resolve(dist):
    broken = []
    for page in dist.rglob("*.html"):
        if page.name == "404.html":  # uses links from the domain root on purpose
            continue
        for link in re.findall(r'(?:href|src)="([^"#]+)', page.read_text(encoding="utf-8")):
            if link.startswith(("http:", "https:", "mailto:")):
                continue
            target = (page.parent / link).resolve()
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                broken.append(f"{page.relative_to(dist)} -> {link}")
    assert not broken, broken


def test_map_bundle_has_every_component(dist):
    bundle = json.loads((dist / "components.json").read_text())
    assert {n["id"] for n in bundle["nodes"]} == {r["id"] for r in load_roster()}
    ids = {n["id"] for n in bundle["nodes"]}
    assert all(e["from"] in ids and e["to"] in ids for e in bundle["edges"])


def test_filled_card_renders_numbers_and_sources(tmp_path):
    data = tmp_path / "data"
    shutil.copytree(DATA_DIR, data)
    card = json.loads((data / "components" / "hbm.json").read_text())
    card["makers"][0]["market_share"].update(value=0.5, source="src-001", confidence="medium", verified="2026-10-01")
    card["concentration"]["label"] = "oligopoly"
    card["sources"] = [{"id": "src-001", "title": "HBM market report", "publisher": "Example Research",
                        "url": "https://example.com/hbm", "date": "2026-09-15", "accessed": "2026-10-01", "type": "analyst"}]
    (data / "components" / "hbm.json").write_text(json.dumps(card))

    out = site_build.build(tmp_path / "dist", data_dir=data, today=date(2026, 10, 21))
    html = (out / "c" / "hbm" / "index.html").read_text()
    assert "50%" in html
    assert "conf-medium" in html and "fresh-green" in html
    assert "HBM market report" in html
    assert "badge-oligopoly" in html


@pytest.mark.parametrize("verified, expected", [
    (None, "none"), ("2026-10-01", "green"), ("2026-06-01", "amber"), ("2026-01-01", "red"),
])
def test_freshness(verified, expected):
    assert site_build.freshness(verified, date(2026, 10, 21)) == expected
