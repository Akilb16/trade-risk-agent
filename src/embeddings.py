import hashlib
import numpy as np

def embed_text(text: str, dimension: int = 64) -> list[float]:
    vector = np.zeros(dimension, dtype=float)
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode()).digest(); vector[int.from_bytes(digest[:4], "big") % dimension] += 1.0
    norm = np.linalg.norm(vector)
    return (vector / norm if norm else vector).tolist()

