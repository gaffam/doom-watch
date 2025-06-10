# Policy scenario definitions for the doom-watch project.
from typing import Dict, Tuple, List

# Each scenario checks the incoming data and returns an extra risk amount
SCENARIOS = [
    {
        "name": "high_interest_low_confidence",
        "impact": 0.05,
        "check": lambda d: d.get("faiz_orani", 0) > 0.5 and d.get("guven_endeksi_degisimi", 0) < -0.01,
    },
    {
        "name": "political_uncertainty",
        "impact": 0.03,
        "check": lambda d: d.get("politik_belirsizlik_skoru", 0) > 0.8,
    },
    {
        "name": "inflation_unemployment",
        "impact": 0.07,
        "check": lambda d: d.get("enflasyon_farki", 0) > 0.15 and d.get("issizlik_orani", 0) > 0.11,
    },
    {
        "name": "currency_volatility",
        "impact": 0.05,
        "check": lambda d: d.get("doviz_kur_volatilite", 0) > 0.04,
    },
    {
        "name": "low_sentiment_and_politics",
        "impact": 0.04,
        "check": lambda d: d.get("public_sentiment", 0) < -0.5 and d.get("politik_belirsizlik_skoru", 0) > 0.8,
    },
]


def scenario_adjustment(data: Dict[str, float]) -> Tuple[float, List[str]]:
    """Return extra risk and triggered scenario names."""
    total_adjustment = 0.0
    triggered: List[str] = []
    for scen in SCENARIOS:
        try:
            if scen["check"](data):
                total_adjustment += scen["impact"]
                triggered.append(scen["name"])
        except Exception:
            continue
    return total_adjustment, triggered
