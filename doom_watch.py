# Example risk indicator using simulated data.
# Not intended for real trading or investment decisions.

import datetime
import logging
import math
import random
import requests
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, Optional

from alerts import send_telegram
from market_watch import check_google_trends, check_bist_crash
from sentiment import get_public_sentiment
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
}

SCALER = "minmax"  # or 'zscore'

_CACHED_DATA: Optional[Dict[str, float]] = None
HISTORY: Dict[str, List[float]] = {k: [] for k in NORMALIZATION}

TE_API_KEY = "guest:guest"  # replace with your Trading Economics key
EVDS_API_KEY = "YOUR_EVDS_KEY"  # replace with your EVDS key

TE_BASE = "https://api.tradingeconomics.com/country/TUR/indicator"
CBRT_XML_URL = "https://www.tcmb.gov.tr/kurlar/today.xml"

TE_INTEREST_API = f"{TE_BASE}/interest-rate?c={TE_API_KEY}&format=json"
TE_INFLATION_API = f"{TE_BASE}/inflation-cpi?c={TE_API_KEY}&format=json"
TE_UNEMPLOY_API = f"{TE_BASE}/unemployment-rate?c={TE_API_KEY}&format=json"


def normalize_value(name: str, value: float) -> float:
    """Normalize a value using the configured scaler and rolling history."""
    params = NORMALIZATION[name]
    hist = HISTORY.get(name, [])
    if hist:
        mean = sum(hist) / len(hist)
        std = (sum((x - mean) ** 2 for x in hist) / len(hist)) ** 0.5
        params = {**params, "min": min(hist), "max": max(hist), "mean": mean, "std": std}
    if SCALER == "zscore":
        z = (value - params["mean"]) / params["std"]
        return 1 / (1 + math.exp(-z))
    norm = (value - params["min"]) / (params["max"] - params["min"])
    return max(0.0, min(norm, 1.0))


def fetch_json(url: str) -> Dict:
    """Fetch JSON data from an API, return empty dict on failure."""
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return {}


def fetch_xml(url: str) -> Optional[ET.Element]:
    """Fetch XML data and return the root element."""
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return ET.fromstring(resp.content)
    except Exception:
        pass
    return None


def fetch_evds_series(series: str) -> Optional[float]:
    """Fetch a single EVDS series value."""
    evds_url = (
        f"https://evds2.tcmb.gov.tr/service/evds/?series={series}&type=json&key={EVDS_API_KEY}&last=1"
    )
    data = fetch_json(evds_url)
    try:
        return float(data["items"][0][series])
    except Exception:
        return None


def get_live_data() -> Dict[str, float]:
    """Fetch live economic data from various sources."""
    global _CACHED_DATA
    data: Dict[str, float] = {}

    # Trading Economics indicators
    interest_json = fetch_json(TE_INTEREST_API)
    try:
        val = float(interest_json[0].get("LatestValue") or interest_json[0].get("Value"))
        data["faiz_orani"] = val / 100.0
    except Exception as exc:
        logging.warning("interest fetch failed: %s", exc)
        data["faiz_orani"] = (_CACHED_DATA or {}).get("faiz_orani", random.uniform(0.40, 0.60))

    cpi_json = fetch_json(TE_INFLATION_API)
    try:
        cpi = float(cpi_json[0].get("LatestValue") or cpi_json[0].get("Value"))
    except Exception as exc:
        logging.warning("cpi fetch failed: %s", exc)
        cpi = (_CACHED_DATA or {}).get("cpi", random.uniform(0.40, 0.70) * 100)

    unemp_json = fetch_json(TE_UNEMPLOY_API)
    try:
        val = float(unemp_json[0].get("LatestValue") or unemp_json[0].get("Value"))
        data["issizlik_orani"] = val / 100.0
    except Exception as exc:
        logging.warning("unemployment fetch failed: %s", exc)
        data["issizlik_orani"] = (_CACHED_DATA or {}).get("issizlik_orani", random.uniform(0.08, 0.12))

    # EVDS producer price index for inflation difference
    ppi = fetch_evds_series("WPPIYO")
    if ppi is None:
        logging.warning("ppi fetch failed")
        ppi = cpi * random.uniform(0.8, 1.2)
    data["enflasyon_farki"] = abs((cpi - ppi) / 100.0)

    # CBRT daily exchange rate volatility
    xml_root = fetch_xml(CBRT_XML_URL)
    try:
        usd = float(xml_root.find(".//Currency[@CurrencyCode='USD']/ForexSelling").text.replace(',', '.'))
        eur = float(xml_root.find(".//Currency[@CurrencyCode='EUR']/ForexSelling").text.replace(',', '.'))
        mean = (usd + eur) / 2
        data["doviz_kur_volatilite"] = abs(usd - eur) / mean
    except Exception as exc:
        logging.warning("cbrt fetch failed: %s", exc)
        data["doviz_kur_volatilite"] = (_CACHED_DATA or {}).get("doviz_kur_volatilite", random.uniform(0.01, 0.05))

    # Remaining simulated indicators
    data.setdefault("otomotiv_talep_degisimi", random.uniform(-0.15, 0.05))
    data.setdefault("global_ticaret_gerilimi_index", random.uniform(0.5, 1.0))
    data.setdefault("politik_belirsizlik_skoru", random.uniform(0.6, 1.0))
    data.setdefault("guven_endeksi_degisimi", random.uniform(-0.03, 0.02))

    # Public sentiment from online sources
    data["public_sentiment"] = get_public_sentiment(["enflasyon", "dolar"])

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
    if check_google_trends(["dolar ne olacak"]):
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
    plt.show()


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
        print("Tetkik Senaryoları:", ", ".join(scenarios))

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
