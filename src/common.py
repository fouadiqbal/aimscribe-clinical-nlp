import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def normalise(text):
    return re.sub(r"\s+", " ", text).strip()


def load_cards():
    return [json.loads(line) for line in (ROOT / "data/cards/cards.jsonl").read_text("utf-8").splitlines() if line.strip()]


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), "utf-8")
