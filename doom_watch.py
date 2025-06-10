# Example risk indicator using simulated data.
# Not intended for real trading or investment decisions.

import datetime
import logging
import math
import random
import requests
from typing import Dict, List, Tuple, Optional

from alerts import send_telegram
from market_watch import check_google_trends, check_bist_crash
from sentiment import get_public_sentiment, fetch_rss_texts
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from politika_scenarios import scenario_adjustment

# Normalization parameters for economic indicators
NORMALIZATION = {
    "faiz_orani": {"min": 0.0, "max": 1.0, "mean": 0.5, "std": 0.1},
    "doviz_kur_volatilite": {"min": 0.0, "max": 0.1, "mean": 0.03, "std": 0.02},
    "enflasyon_farki": {"min": 0.0, "max": 0.3, "mean": 0.1, "std": 0.05},
    "issizlik_orani": {"min": 0.0, "max": 0.2, "mean": 0.1, "std": 0.03},
    "otomotiv_talep_degisimi": {"min": -0.2, "max": 0.1, "mean": -0.05, "std": 0.07},
    "global_ticaret_gerilimi_index": {"min": 0.0, "max": 1.0, "mean": 0.5, "std": 0.2},
    "politik_belirsizlik_skoru": {"min": 0.0, "max": 1.0, "mean": 0.7, "std": 0.15},
    "guven_endeksi_degisimi": {"min": -0.05, "max": 0.05, "mean": -0.01, "std": 0.02},
    "public_sentiment": {"min": -1.0, "max": 1.0, "mean": 0.0, "std": 0.5},
}

SCALER = "minmax"  # or 'zscore'

_CACHED_DATA: Optional[Dict[str, float]] = None
HISTORY: Dict[str, List[float]] = {k: [] for k in NORMALIZATION}



def normalize_value(name: str, value: float) -> float:
    """Normalize a value using the configured scaler and rolling history."""
    params = NORMALIZATION[name]
    hist = HISTORY.get(name, [])
    if hist:
        mean = sum(hist) / len(hist)
        std = (sum((x - mean) ** 2 for x in hist) / len(hist)) ** 0.5
        params = {**params, "min": min(hist), "max": max(hist), "mean": mean, "std": std}
    if SCALER == "zscore":
        z = (value - params["mean"]) / params["std"] if params["std"] else 0.0
        return 1 / (1 + math.exp(-z))
    norm = (value - params["min"]) / (params["max"] - params["min"])
    return max(0.0, min(norm, 1.0))




def get_live_data() -> Dict[str, float]:
    """Fetch live economic data (simulated for now)."""
    global _CACHED_DATA
    data: Dict[str, float] = {}

    data["public_sentiment"] = get_public_sentiment()

    data["faiz_orani"] = (_CACHED_DATA or {}).get("faiz_orani", random.uniform(0.40, 0.60))

    cpi_sim = (_CACHED_DATA or {}).get("cpi", random.uniform(0.40, 0.70) * 100)
    ppi_sim = cpi_sim * random.uniform(0.8, 1.2)
    data["enflasyon_farki"] = abs((cpi_sim - ppi_sim) / 100.0)

    data["issizlik_orani"] = (_CACHED_DATA or {}).get("issizlik_orani", random.uniform(0.08, 0.12))

    data["doviz_kur_volatilite"] = (_CACHED_DATA or {}).get("doviz_kur_volatilite", random.uniform(0.01, 0.05))

    data.setdefault("otomotiv_talep_degisimi", random.uniform(-0.15, 0.05))
    data.setdefault("global_ticaret_gerilimi_index", random.uniform(0.5, 1.0))
    data.setdefault("politik_belirsizlik_skoru", random.uniform(0.6, 1.0))
    data.setdefault("guven_endeksi_degisimi", random.uniform(-0.03, 0.02))

    for key in HISTORY:
        if key in data:
            HISTORY[key].append(data[key])
            HISTORY[key] = HISTORY[key][-12:]

    _CACHED_DATA = data
    return data


def calculate_risk_score(data: Dict[str, float]) -> Tuple[float, List[str]]:
    """Calculate a risk score from live data."""
    weights = {
        "faiz_orani": 0.15,
        "doviz_kur_volatilite": 0.20,
        "enflasyon_farki": 0.20,
        "issizlik_orani": 0.10,
        "otomotiv_talep_degisimi": 0.08,
        "global_ticaret_gerilimi_index": 0.05,
        "politik_belirsizlik_skoru": 0.07,
        "guven_endeksi_degisimi": 0.05,
        "public_sentiment": 0.10,
    }

    risk_contributions = {
        "faiz_orani": normalize_value("faiz_orani", data["faiz_orani"]),
        "doviz_kur_volatilite": normalize_value("doviz_kur_volatilite", data["doviz_kur_volatilite"]),
        "enflasyon_farki": normalize_value("enflasyon_farki", data["enflasyon_farki"]),
        "issizlik_orani": normalize_value("issizlik_orani", data["issizlik_orani"]),
        "otomotiv_talep_degisimi": 1 - normalize_value("otomotiv_talep_degisimi", data["otomotiv_talep_degisimi"]),
        "global_ticaret_gerilimi_index": normalize_value("global_ticaret_gerilimi_index", data["global_ticaret_gerilimi_index"]),
        "politik_belirsizlik_skoru": normalize_value("politik_belirsizlik_skoru", data["politik_belirsizlik_skoru"]),
        "guven_endeksi_degisimi": 1 - normalize_value("guven_endeksi_degisimi", data["guven_endeksi_degisimi"]),
        "public_sentiment": 1 - ((data.get("public_sentiment", 0) + 1) / 2),
    }

    base_score = sum(risk_contributions[f] * weights[f] for f in weights)
    if check_google_trends(["dolar ne olacak", "ekonomi kötü mü"]):
        base_score += 0.05
    adjustment, triggered = scenario_adjustment(data)
    total = min(1.0, max(0.0, base_score + adjustment))
    return total, triggered


def plot_risk_indicator(current_risk_score: float) -> None:
    """Visualize the risk level over time as a line chart."""
    today = datetime.date.today()
    dates = [today - datetime.timedelta(days=i * 30) for i in range(3, 0, -1)] + [
        today + datetime.timedelta(days=i * 30) for i in range(7)
    ]
    risk_values = [
        max(0.6, current_risk_score - random.uniform(0.1, 0.2) + random.uniform(-0.02, 0.02))
        for _ in range(3)
    ] + [current_risk_score] + [
        min(0.99, current_risk_score + random.uniform(-0.01, 0.03)) for _ in range(6)
    ]

    plt.figure(figsize=(12, 6))
    plt.plot(dates, risk_values[: len(dates)], marker="o", linestyle="-", color="blue", alpha=0.7)
    plt.plot(today, current_risk_score, marker="X", markersize=12, color="red", label=f"Bugünkü Risk: {current_risk_score:.2f}")
    plt.axhspan(0, 0.4, color="green", alpha=0.1, label="Düşük Risk")
    plt.axhspan(0.4, 0.7, color="orange", alpha=0.1, label="Orta Risk")
    plt.axhspan(0.7, 1.0, color="red", alpha=0.1, label="Yüksek Risk")
    plt.title("Türkiye Ekonomisi Kıyamet Saati - Risk Göstergesi")
    plt.xlabel("Tarih")
    plt.ylabel("Risk Skoru (0-1)")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.gcf().autofmt_xdate()
    plt.ylim(0, 1.0)
    plt.legend()
    plt.tight_layout()
    # plt.show()  # Streamlit uses st.pyplot() instead


def main() -> None:
    """Run a single update of the risk indicator."""
    print("Türkiye Ekonomisi Kıyamet Saatini Başlatıyorum Kanka!")
    current_data = get_live_data()
    print("\nGüncel Veri Seti:")
    for key, value in current_data.items():
        print(f"  {key}: {value:.2f}")

    risk_score, scenarios = calculate_risk_score(current_data)
    print(f"\nHesaplanan Güncel Risk Skoru: {risk_score:.2f}")
    if scenarios:
        print("Tetiklenen Senaryolar:", ", ".join(scenarios))

    plot_risk_indicator(risk_score)

    print("\nKıyamet Saati göstergesi güncellendi.")
    if risk_score > 0.75:
        print("UYARI: Risk Seviyesi Yüksek! Piyasalar alarm veriyor.")
        send_telegram("\u26a0\ufe0f Yüksek ekonomik risk tespit edildi!")
    elif risk_score > 0.55:
        print("DİKKAT: Risk Seviyesi Orta! Gelişmeler takip edilmeli.")
    else:
        print("NORMAL: Risk Seviyesi Düşük. Piyasalar sakin seyrediyor.")

    check_bist_crash()


if __name__ == "__main__":
    main()
