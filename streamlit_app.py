"""Streamlit interface for the doom-watch application."""

import datetime
import random
import pandas as pd
import streamlit as st

import doom_watch as dw
from sentiment import get_sentiment_score

# Simple localization dictionary
TXT = {
    "tr": {
        "title": "Türkiye Ekonomisi Kıyamet Saati \U0001F570\ufe0f",
        "date": "\U0001F4C5 Tarih Seç",
        "manual": "Manuel Veri Girişi",
        "auto_demand": "Otomotiv Talep Değişimi (Örn: -0.05 için -%5)",
        "news_box": "Bugün duyduğun herhangi bir negatif gelişmeyi buraya gir (isteğe bağlı)",
        "update": "Veriyi Güncelle ve Risk Skorunu Hesapla \U0001F4B8",
        "high": "\U0001F6A8 UYARI: Risk Seviyesi Yüksek! Piyasalar alarm veriyor. Kıyamet Saati yaklaşıyor!",
        "mid": "\U0001F6A7 DİKKAT: Risk Seviyesi Orta! Gelişmeler yakından takip edilmeli.",
        "low": "\U0001F7E2 NORMAL: Risk Seviyesi Düşük. Piyasalar sakin seyrediyor.",
        "history": "Son 7 Günün Risk Skorları",
        "update_hint": "Verileri güncellemek ve risk skorunu görmek için yukarıdaki butona tıklayın.",
        "trigger": "Tetiklenen Senaryolar",
        "graph": "Risk Göstergesi Grafiği",
    },
    "en": {
        "title": "Turkey Economy Doomsday Clock \U0001F570\ufe0f",
        "date": "\U0001F4C5 Select Date",
        "manual": "Manual Data Entry",
        "auto_demand": "Automotive Demand Change (e.g. -0.05 for -5%)",
        "news_box": "Enter any negative news you heard today (optional)",
        "update": "Update Data and Calculate Risk \U0001F4B8",
        "high": "\U0001F6A8 WARNING: High Risk! Markets are alarming.",
        "mid": "\U0001F6A7 CAUTION: Moderate Risk. Monitor developments.",
        "low": "\U0001F7E2 NORMAL: Low Risk. Markets are calm.",
        "history": "Last 7 Days' Risk Scores",
        "update_hint": "Click the button above to refresh data and see the score.",
        "trigger": "Triggered Scenarios",
        "graph": "Risk Indicator Graph",
    },
}

lang = st.sidebar.selectbox("Language / Dil", ["tr", "en"], index=0)
T = TXT[lang]

st.title(T["title"])

# session state for history and manual data
if "history" not in st.session_state:
    st.session_state.history = []
if "otomotiv_data" not in st.session_state:
    st.session_state.otomotiv_data = random.uniform(-0.15, 0.05)

selected_date = st.date_input(T["date"], value=datetime.date.today())

st.markdown("---")

st.subheader(T["manual"])
otomotiv_input = st.number_input(
    T["auto_demand"],
    min_value=-0.5,
    max_value=0.5,
    value=st.session_state.otomotiv_data,
    step=0.01,
    format="%.2f",
)
st.session_state.otomotiv_data = otomotiv_input

user_news = st.text_area(T["news_box"], "")

st.markdown("---")

if st.button(T["update"]):
    st.write("...")
    data = dw.get_live_data()
    data["otomotiv_talep_degisimi"] = st.session_state.otomotiv_data
    if user_news.strip():
        user_sent = get_sentiment_score([user_news])
        data["public_sentiment"] = (data.get("public_sentiment", 0.0) + user_sent) / 2

    score, scenarios = dw.calculate_risk_score(data)
    st.subheader(f"Güncel Risk Skoru: **{score:.2f}**")

    if score > 0.75:
        st.error(T["high"])
    elif score > 0.55:
        st.warning(T["mid"])
    else:
        st.success(T["low"])

    if scenarios:
        st.info(f"**{T['trigger']}:** {', '.join(scenarios)}")

    st.session_state.history.append({"Tarih": selected_date, "Skor": round(score, 2)})
    st.session_state.history = st.session_state.history[-7:]

    st.subheader(T["graph"])
    fig = dw.plot_risk_indicator(score)
    st.plotly_chart(fig, use_container_width=True)

    if dw.check_bist_crash():
        st.warning("\U0001F6A8 BIST'te ani düşüş tespit edildi!")
else:
    st.info(T["update_hint"])

st.markdown("---")

if st.session_state.history:
    st.subheader(T["history"])
    df = pd.DataFrame(st.session_state.history)
    df["Tarih"] = pd.to_datetime(df["Tarih"]).dt.strftime("%Y-%m-%d")
    st.table(df.set_index("Tarih"))
