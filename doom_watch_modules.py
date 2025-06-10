from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from transformers import pipeline


def detect_anomalies(
    data: Dict[str, float],
    normal_params: Dict[str, Dict[str, float]],
    method: str = "zscore",
) -> Dict[str, bool]:
    """Return anomaly flags for data using z-score or IQR."""
    anomalies: Dict[str, bool] = {}
    for key, value in data.items():
        params = normal_params.get(key, {})
        mean = params.get("mean", 0.0)
        std = params.get("std", 1.0)
        if method == "zscore":
            z = abs((value - mean) / std) if std else 0.0
            anomalies[key] = z > 2
        else:
            q1 = params.get("q1", 0.0)
            q3 = params.get("q3", 0.0)
            iqr = q3 - q1
            anomalies[key] = value < (q1 - 1.5 * iqr) or value > (q3 + 1.5 * iqr)
    return anomalies


def calculate_momentum(gecmis_values: Dict[str, List[float]]) -> Dict[str, float]:
    """Compute simple momentum metrics from historical values."""
    momentums: Dict[str, float] = {}
    for key, values in gecmis_values.items():
        if len(values) >= 2:
            momentum = values[-1] - values[-2]
        else:
            momentum = 0.0
        momentums[key] = momentum
    return momentums


def analyze_sentiment(texts: List[str]) -> float:
    """Analyze sentiment of provided texts using a Turkish BERT model."""
    if not texts:
        return 0.0

    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model="savasy/bert-base-turkish-sentiment-cased",
        tokenizer="savasy/bert-base-turkish-sentiment-cased",
    )

    scores = []
    for text in texts:
        result = sentiment_pipeline(text)[0]
        label = result.get("label", "")
        score = result.get("score", 0.0)
        scores.append(score if "POS" in label.upper() else -score)

    return float(np.mean(scores)) if scores else 0.0


def train_risk_rules(X: pd.DataFrame, y: List[int]):
    """Train a decision tree and return model with feature importances."""
    model = DecisionTreeClassifier(max_depth=3)
    model.fit(X, y)
    feature_importances = dict(zip(X.columns, model.feature_importances_))
    return model, feature_importances
