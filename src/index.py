"""Rebuild a tiny exact cosine vector index of canonical cards only."""
import hashlib
import json
import os
from functools import lru_cache
import numpy as np
from src.common import ROOT, load_cards, write_json

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
INDEX = ROOT / "data/index"


@lru_cache(maxsize=1)
def encoder():
    from sentence_transformers import SentenceTransformer
    import torch
    torch.set_num_threads(2)
    local = ROOT / "models/embeddings"
    if not local.exists():
        from src.setup_embeddings import main
        main()
    return SentenceTransformer(str(local), device="cpu", local_files_only=True)


def card_text(card):
    return " ".join([card["disease"], card["category"], card["retrieval_cues"], card["recommended_action"]])


def build_index():
    cards = load_cards()
    model = encoder()
    vectors = model.encode([card_text(c) for c in cards], normalize_embeddings=True, show_progress_bar=True)
    INDEX.mkdir(parents=True,exist_ok=True)
    np.save(INDEX / "vectors.npy",vectors)
    write_json(INDEX / "metadata.json", {"model":EMBEDDING_MODEL,
        "card_ids":[c["card_id"] for c in cards],
        "cards_sha256":hashlib.sha256((ROOT / "data/cards/cards.jsonl").read_bytes()).hexdigest(),
        "method":"Exact cosine similarity over normalized embeddings; no approximate index needed for this corpus."})
    print(f"Indexed {len(cards)} cards locally")


if __name__ == "__main__":
    build_index()
