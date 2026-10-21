import hashlib
import json
import numpy as np
from src.common import ROOT, load_cards
from src.index import INDEX, encoder


def patient_query(patient):
    # No disease field or expected-case file is read here.
    return "; ".join(f"{k}: {v}" for k,v in patient.items() if v is not None and k not in {"case_id","modification_note","expected_behaviour","disease","diagnosis"})


def retrieve(patient, k=8):
    metadata = json.loads((INDEX / "metadata.json").read_text("utf-8"))
    digest = hashlib.sha256((ROOT / "data/cards/cards.jsonl").read_bytes()).hexdigest()
    if digest != metadata["cards_sha256"]:
        raise RuntimeError("Cards changed. Rebuild with python -m src.index before running.")
    cards = {c["card_id"]:c for c in load_cards()}
    vectors = np.load(INDEX / "vectors.npy")
    query = encoder().encode([patient_query(patient)], normalize_embeddings=True)[0]
    scores = vectors @ query
    order = np.argsort(-scores,kind="stable")[:k]
    return [{"card":cards[metadata["card_ids"][i]],"score":float(scores[i])} for i in order]
