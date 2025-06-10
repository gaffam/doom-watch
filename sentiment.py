# Sentiment analysis using a Turkish BERT model.
"""Sentiment analysis utilities."""

from typing import List
import logging
import random
import numpy as np
from transformers import pipeline
import feedparser

# Additional Turkish RSS feed URLs
RSS_FEEDS = [
    "https://tr.investing.com/rss/central_banks.rss",
    "https://www.bbc.com/turkce/ekonomi/index.xml",
    "https://www.bbc.com/turkce/basinozeti/index.xml",
    "https://www.ntv.com.tr/gundem.rss",
    "https://www.ntv.com.tr/ekonomi.rss",
    "https://www.haberler.com/rss/ekonomi.xml",
    "https://www.bloomberght.com/rss/",
    "https://search.worldbank.org/api/v2/news?format=atom&countrycode_exact=TR",
    "https://tr.investing.com/rss/news_1064.rss",
    "https://tr.investing.com/rss/stock_Indices.rss",
    "https://tr.investing.com/rss/news_95.rss",
]


def fetch_rss_texts(keywords: List[str] = None, limit: int = 50) -> List[str]:
    """Return news texts from all feeds with optional keyword filtering."""
    texts: List[str] = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            if feed.bozo:
                logging.warning("RSS error %s: %s", url, feed.bozo_exception)
                continue
            for entry in feed.entries:
                text = ""
                if hasattr(entry, "title"):
                    text += entry.title
                if hasattr(entry, "summary"):
                    text += " " + entry.summary
                elif hasattr(entry, "description"):
                    text += " " + entry.description
                if not text.strip() or text.strip() in texts:
                    continue
                if keywords and not any(kw.lower() in text.lower() for kw in keywords):
                    continue
                texts.append(text.strip())
                if len(texts) >= limit:
                    break
            if len(texts) >= limit:
                break
        except Exception as exc:
            logging.warning("feed parse failed for %s: %s", url, exc)
    if not texts:
        logging.warning("No RSS texts fetched; using fallback samples")
        samples = [
            "Ekonomi gündeminde önemli gelişmeler bekleniyor.",
            "Piyasalarda hafif bir iyimserlik hakim.",
            "Dolar kuru sakin seyrini sürdürüyor.",
            "Enflasyon rakamları merakla bekleniyor.",
        ]
        return random.sample(samples, k=min(len(samples), 3))
    return texts[:limit]


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
    except Exception as exc:
        logging.error("Sentiment analysis failed: %s", exc)
        return 0.0


def get_public_sentiment(keywords: List[str] = None) -> float:
    """Fetch texts from RSS feeds for keywords and compute sentiment score."""
    texts = fetch_rss_texts(keywords=keywords)
    if not texts:
        return 0.0
    return get_sentiment_score(texts)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Genel ekonomi haberleri için duygu analizi:")
    general_sentiment = get_public_sentiment()
    print(f"Genel Duygu Skoru: {general_sentiment:.2f}")

    print("\n'Dolar' anahtar kelimesiyle ilgili haberler için duygu analizi:")
    dolar_sentiment = get_public_sentiment(keywords=["dolar", "kur"])
    print(f"Dolar Duygu Skoru: {dolar_sentiment:.2f}")

    print("\n'Enflasyon' anahtar kelimesiyle ilgili haberler için duygu analizi:")
    enflasyon_sentiment = get_public_sentiment(keywords=["enflasyon", "fiyat"])
    print(f"Enflasyon Duygu Skoru: {enflasyon_sentiment:.2f}")

