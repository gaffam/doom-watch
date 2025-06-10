#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Example risk indicator using real data when available.
# Not intended for real trading or investment decisions.

import datetime
import logging
import math
import random
import requests
from typing import Dict, List, Tuple, Optional

import plotly.graph_objects as go

from alerts import send_telegram
from market_watch import check_google_trends, check_bist_crash
from sentiment import get_public_sentiment
from politika_scenarios import scenario_adjustment
from config import TRADING_ECON_KEY, EVDS_KEY

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


def fetch_json(url: str) -> List[Dict[str, float]]:
    """Helper to load JSON with timeout."""
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()


def fetch_xml(url: str) -> Optional[str]:
    """Fetch XML string from URL."""
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.text
    except Exception as exc:
        logging.warning("xml fetch failed: %s", exc)
        return None


def get_live_data() -> Dict[str, float]:
    """Fetch live economic data with API fallbacks to random."""
    global _CACHED_DATA
    data: Dict[str, float] = {}

    data["public_sentiment"] = get_public_sentiment()

    # Interest rate
    try:
        url = f"https://api.tradingeconomics.com/country/TUR/indicator/interest-rate?c={TRADING_ECON_KEY}&format=json"
        resp = fetch_json(url)
        data["faiz_orani"] = float(resp[0]["Value"]) / 100
    except Exception as exc:
        logging.warning("interest rate fetch failed: %s", exc)
        data["faiz_orani"] = random.uniform(0.40, 0.60)

    # Inflation and PPI difference
    try:
        cpi_url = f"https://api.tradingeconomics.com/country/TUR/indicator/inflation-cpi?c={TRADING_ECON_KEY}&format=json"
        unemp_url = f"https://api.tradingeconomics.com/country/TUR/indicator/unemployment-rate?c={TRADING_ECON_KEY}&format=json"
        cpi = fetch_json(cpi_url)[0]["Value"]
        ppi = fetch_json(unemp_url)[0]["Value"]  # placeholder; not real ppi
        data["enflasyon_farki"] = abs(float(cpi) - float(ppi)) / 100
    except Exception as exc:
        logging.warning("inflation fetch failed: %s", exc)
        cpi_sim = (_CACHED_DATA or {}).get("cpi", random.uniform(0.40, 0.70) * 100)
        ppi_sim = cpi_sim * random.uniform(0.8, 1.2)
        data["enflasyon_farki"] = abs((cpi_sim - ppi_sim) / 100.0)

    # Unemployment
    try:
        url = f"https://api.tradingeconomics.com/country/TUR/indicator/unemployment-rate?c={TRADING_ECON_KEY}&format=json"
        resp = fetch_json(url)
        data["issizlik_orani"] = float(resp[0]["Value"]) / 100
    except Exception as exc:
        logging.warning("unemployment fetch failed: %s", exc)
        data["issizlik_orani"] = random.uniform(0.08, 0.12)

    # Exchange rate volatility from CBRT XML
    xml_text = fetch_xml("https://www.tcmb.gov.tr/kurlar/today.xml")
    try:
        if xml_text:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_text)
            usd = float(root.findtext('.//Currency[@CurrencyCode="USD"]/ForexSelling'))
            eur = float(root.findtext('.//Currency[@CurrencyCode="EUR"]/ForexSelling'))
            vol = abs(usd - eur) / ((usd + eur) / 2)
            data["doviz_kur_volatilite"] = vol
        else:
            raise ValueError("no xml")
    except Exception as exc:
        logging.warning("exchange rate parse failed: %s", exc)
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


def plot_risk_indicator(current_risk_score: float):
    """Return a Plotly Figure showing the risk level."""
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

    fig = go.Figure()
    fig.add_scatter(x=dates, y=risk_values[: len(dates)], mode="lines+markers", name="Risk")
    fig.add_hline(y=0.4, line_color="green", opacity=0.2)
    fig.add_hline(y=0.7, line_color="orange", opacity=0.2)
    fig.update_yaxes(range=[0, 1])
    fig.update_layout(title="Türkiye Ekonomisi Kıyamet Saati - Risk Göstergesi", xaxis_title="Tarih", yaxis_title="Risk Skoru (0-1)")
    return fig


def main() -> None:
    """Run a single update of the risk indicator."""
    logging.basicConfig(level=logging.INFO)
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
