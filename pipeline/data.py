"""Load the files under data/. Shared by the pipeline, site build, and PDF build."""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"


def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_tiers(data_dir: Path = DATA_DIR) -> list[dict]:
    return load_json(data_dir / "tiers.json")


def load_roster(data_dir: Path = DATA_DIR) -> list[dict]:
    return load_json(data_dir / "roster.json")


def load_schema(data_dir: Path = DATA_DIR) -> dict:
    return load_json(data_dir / "schema" / "component.schema.json")


def component_paths(data_dir: Path = DATA_DIR) -> list[Path]:
    return sorted((data_dir / "components").glob("*.json"))


def load_components(data_dir: Path = DATA_DIR) -> dict[str, dict]:
    """Return {component_id: card}, keyed by file name (without .json)."""
    return {path.stem: load_json(path) for path in component_paths(data_dir)}
