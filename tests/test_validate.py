"""Tests for pipeline/validate.py. Each test builds a small throwaway data/ folder."""

import copy
import json
import shutil

import pytest

from pipeline.data import DATA_DIR
from pipeline.validate import expected_label, validate


def blank_sv(unit="share"):
    return {"value": None, "unit": unit, "source": None, "confidence": None, "verified": None}


def make_card(cid, tier, inputs=(), customers=()):
    return {
        "id": cid, "tier": tier, "name": cid, "summary": "", "what_it_does": "",
        "makers": [{"company": "Acme", "country": "US", "market_share": blank_sv()}],
        "concentration": {"label": None, "hhi": blank_sv("index"), "note": ""},
        "cost": {"unit": None, "price_band": {"low": None, "high": None, "currency": "USD",
                 "source": None, "confidence": None, "verified": None}, "note": ""},
        "lead_time": blank_sv("weeks"),
        "inputs": list(inputs), "customers": list(customers),
        "chokepoint_notes": "", "sources": [],
        "meta": {"status": "draft"},
    }


SOURCE = {"id": "src-001", "title": "T", "publisher": "P", "url": "https://example.com",
          "date": "2026-09-01", "accessed": "2026-10-19", "type": "news"}


@pytest.fixture
def data_dir(tmp_path):
    """A copy of the real tiers/roster/schema with an empty components folder."""
    d = tmp_path / "data"
    (d / "components").mkdir(parents=True)
    shutil.copy(DATA_DIR / "tiers.json", d)
    shutil.copy(DATA_DIR / "roster.json", d)
    shutil.copytree(DATA_DIR / "schema", d / "schema")
    return d


def write(data_dir, card):
    (data_dir / "components" / f"{card['id']}.json").write_text(json.dumps(card))


def test_real_data_passes():
    assert validate().ok


def test_matching_edges_pass(data_dir):
    write(data_dir, make_card("euv-lithography", "T1", customers=["leading-edge-fab"]))
    write(data_dir, make_card("leading-edge-fab", "T2", inputs=["euv-lithography"]))
    report = validate(data_dir)
    assert report.ok, report.errors


def test_one_sided_edge_fails(data_dir):
    write(data_dir, make_card("euv-lithography", "T1", customers=["leading-edge-fab"]))
    write(data_dir, make_card("leading-edge-fab", "T2"))
    report = validate(data_dir)
    assert any("does not list euv-lithography in 'inputs'" in e for e in report.errors)


def test_unknown_id_fails(data_dir):
    write(data_dir, make_card("euv-lithography", "T1", customers=["made-up-thing"]))
    assert any("no such component ID" in e for e in validate(data_dir).errors)


def test_missing_roster_card_is_warning_then_error_in_strict(data_dir):
    write(data_dir, make_card("euv-lithography", "T1", customers=["leading-edge-fab"]))
    assert validate(data_dir).ok
    assert not validate(data_dir, strict=True).ok


def test_self_reference_fails(data_dir):
    write(data_dir, make_card("hbm", "T4", inputs=["hbm"]))
    assert any("lists itself" in e for e in validate(data_dir).errors)


def test_filename_must_match_id(data_dir):
    card = make_card("hbm", "T4")
    (data_dir / "components" / "wrong-name.json").write_text(json.dumps(card))
    assert not validate(data_dir).ok


def test_tier_must_match_roster(data_dir):
    write(data_dir, make_card("hbm", "T5"))
    assert any("does not match roster tier" in e for e in validate(data_dir).errors)


def test_bare_number_fails_schema(data_dir):
    card = make_card("hbm", "T4")
    card["lead_time"] = 12
    write(data_dir, card)
    assert any("schema" in e for e in validate(data_dir).errors)


def test_citing_missing_source_fails(data_dir):
    card = make_card("hbm", "T4")
    card["lead_time"] = {"value": 12, "unit": "weeks", "source": "src-009", "confidence": "low", "verified": None}
    write(data_dir, card)
    assert any("not in 'sources'" in e for e in validate(data_dir).errors)


def test_approved_card_needs_source_and_verified(data_dir):
    card = make_card("hbm", "T4")
    card["meta"] = {"status": "approved", "approved_by": "dan", "approved_on": "2026-10-19"}
    write(data_dir, card)
    errors = validate(data_dir).errors
    assert any("has no source" in e for e in errors)
    assert any("has no verified date" in e for e in errors)


def test_fully_sourced_approved_card_passes(data_dir):
    card = make_card("hbm", "T4")
    full = {"value": 1, "unit": "x", "source": "src-001", "confidence": "high", "verified": "2026-10-19"}
    card["makers"][0]["market_share"] = {**full, "value": 0.95, "unit": "share"}
    card["concentration"]["label"] = "monopoly"
    card["concentration"]["hhi"] = {**full, "value": 9025, "unit": "index"}
    card["cost"]["price_band"] = {"low": 1, "high": 2, "currency": "USD", "source": "src-001",
                                  "confidence": "low", "verified": "2026-10-19"}
    card["lead_time"] = copy.deepcopy(full)
    card["sources"] = [SOURCE]
    card["meta"] = {"status": "approved", "approved_by": "dan", "approved_on": "2026-10-19"}
    write(data_dir, card)
    report = validate(data_dir)
    assert report.ok, report.errors
    assert not report.warnings


@pytest.mark.parametrize("shares, label", [
    ([0.95], "monopoly"),
    ([0.60, 0.30], "duopoly"),
    ([0.50, 0.20, 0.10], "oligopoly"),
    ([0.20, 0.20, 0.10, 0.10], "competitive"),
])
def test_expected_label(shares, label):
    assert expected_label(shares) == label


def test_equipment_may_feed_memory_fabs(data_dir):
    write(data_dir, make_card("euv-lithography", "T1", customers=["hbm"]))
    write(data_dir, make_card("hbm", "T4", inputs=["euv-lithography"]))
    report = validate(data_dir)
    assert report.ok, report.errors


def test_tier_distance_too_far_fails(data_dir):
    write(data_dir, make_card("leading-edge-fab", "T2", customers=["gpu-servers-oem"]))
    write(data_dir, make_card("gpu-servers-oem", "T6", inputs=["leading-edge-fab"]))
    assert any("tiers apart" in e for e in validate(data_dir).errors)


def test_planned_link_to_unknown_id_fails(data_dir):
    roster = json.loads((data_dir / "roster.json").read_text())
    roster[0]["planned_customers"] = ["no-such-thing"]
    (data_dir / "roster.json").write_text(json.dumps(roster))
    assert any("no-such-thing" in e for e in validate(data_dir).errors)


def test_planned_link_too_far_fails(data_dir):
    roster = json.loads((data_dir / "roster.json").read_text())
    euv = next(r for r in roster if r["id"] == "euv-lithography")
    euv["planned_customers"] = ["inference-providers"]
    (data_dir / "roster.json").write_text(json.dumps(roster))
    assert any("tiers apart" in e for e in validate(data_dir).errors)
