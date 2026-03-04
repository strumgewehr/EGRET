"""
Article similarity detection (sentence embeddings). Detects similar/copied content.
"""
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)
_model = None


def _get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            logger.warning("SentenceTransformer load failed: %s. Similarity disabled.", e)
            _model = "unavailable"
    return _model


def compute_similarity(text1: str, text2: str) -> float:
    """Cosine similarity 0-1 between two texts."""
    model = _get_model()
    if model == "unavailable" or not text1 or not text2:
        return 0.0
    try:
        from sentence_transformers import util
        e1 = model.encode(text1[:512], convert_to_tensor=False)
        e2 = model.encode(text2[:512], convert_to_tensor=False)
        return float(util.cos_sim(e1, e2).item())
    except Exception as e:
        logger.warning("Similarity compute error: %s", e)
        return 0.0


def batch_similarity_pairs(texts: List[str], threshold: float = 0.85) -> List[Tuple[int, int, float]]:
    """
    For a list of texts, return pairs (i, j, score) where similarity >= threshold.
    """
    model = _get_model()
    if model == "unavailable" or len(texts) < 2:
        return []
    try:
        from sentence_transformers import util
        embeddings = model.encode([t[:512] for t in texts], convert_to_tensor=False)
        pairs = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                sim = float(util.cos_sim(embeddings[i], embeddings[j]).item())
                if sim >= threshold:
                    pairs.append((i, j, round(sim, 4)))
        return pairs
    except Exception as e:
        logger.warning("Batch similarity error: %s", e)
        return []
