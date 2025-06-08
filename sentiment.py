# Sentiment analysis using a Turkish BERT model.
"""Sentiment analysis utilities."""

from typing import List

import logging
import random
import numpy as np
import requests
from transformers import pipeline


def fetch_public_texts(keywords: List[str], limit: int = 20) -> List[str]:
    """Return a list of recent tweets or news headlines matching keywords."""
    query = " ".join(keywords)
    try:
        # Placeholder implementation – real code would call APIs such as Twitter
        # or news feeds. Here we simply return an empty list on failure.
        resp = requests.get(
            f"https://api.example.com/search?q={query}&n={limit}", timeout=5
        )
        if resp.status_code == 200:
            return resp.json().get("texts", [])
    except Exception as exc:
        logging.warning("public text fetch failed: %s", exc)
    # fallback to synthetic texts
    samples = [
        "Enflasyon yükseliyor", "Dolar ne olacak", "Piyasalarda belirsizlik",
        "Yatırımcı güveni düşük",
    ]
    return random.sample(samples, k=min(len(samples), 3))


def get_sentiment_score(texts: List[str]) -> float:
    """Return mean sentiment score for the provided texts."""
    if not texts:
        return 0.0
    try:
        nlp = pipeline(
            "sentiment-analysis",
            model="savasy/bert-base-turkish-sentiment-cased",
            tokenizer="savasy/bert-base-turkish-sentiment-cased",
        )
        results = nlp(texts)
        scores = [r["score"] * (1 if "POS" in r["label"] else -1) for r in results]
        return float(np.clip(np.mean(scores), -1.0, 1.0))
    except Exception:
        return 0.0


def get_public_sentiment(keywords: List[str]) -> float:
    """Fetch texts for keywords and compute sentiment score."""
    texts = fetch_public_texts(keywords)
    if not texts:
        return 0.0
    return get_sentiment_score(texts)
