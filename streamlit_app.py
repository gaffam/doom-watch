# Streamlit arayüzü.
# doom_watch modülündeki fonksiyonları kullanarak risk göstergesini günceller.

import datetime
import matplotlib
matplotlib.use("Agg")  # Arayüzde grafik gösterebilmek için
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

import doom_watch as dw
import random  # Otomotiv verisi için geçici olarak random da kullanılabilir
from sentiment import get_sentiment_score  # <-- Bu satırı ekledim!

# Uygulama başlığı
st.title("Türkiye Ekonomisi Kıyamet Saati \U0001F570\ufe0f")

# Oturumda skor geçmişi tutulur
if "history" not in st.session_state:
    st.session_state.history = []
if "otomotiv_data" not in st.session_state:
    st.session_state.otomotiv_data = random.uniform(-0.15, 0.05)

# Tarih seçici (simülasyon amaçlı)
selected_date = st.date_input("\U0001F4C5 Tarih Seç", value=datetime.date.today())

st.markdown("---")  # Ayırıcı

# Otomotiv Talep Değişimi için manuel giriş alanı
st.subheader("Manuel Veri Girişi")
otomotiv_input = st.number_input(
    "Otomotiv Talep Değişimi (Örn: -0.05 için -%5)",
    min_value=-0.5,
    max_value=0.5,
    value=st.session_state.otomotiv_data,
    step=0.01,
    format="%.2f",
    help=(
        "Son 3 aylık otomotiv talebindeki değişimi ifade eder. "
        "Pozitif değer artış, negatif değer düşüş anlamına gelir. "
        "(Örn: 0.05 veya -0.10)"
    ),
)
st.session_state.otomotiv_data = otomotiv_input

# Kullanıcının duyduğu negatif haberi girmesi için metin kutusu
user_news = st.text_area(
    "Bugün duyduğun herhangi bir negatif gelişmeyi buraya gir (isteğe bağlı)",
    "",
)

st.markdown("---")  # Ayırıcı

# Veriyi güncelleyen buton
if st.button("Veriyi Güncelle ve Risk Skorunu Hesapla \U0001F4B8"):
    st.write("Veriler çekiliyor ve analiz ediliyor, lütfen bekleyin...")

    # Mevcut veriyi çek (API yerine simüle ve RSS destekli)
    data = dw.get_live_data()

    # Manuel girilen otomotiv verisini entegre et
    data["otomotiv_talep_degisimi"] = st.session_state.otomotiv_data

    # Kullanıcının girdiği haber varsa mevcut duygu skoruyla harmanla
    if user_news.strip():
        user_sent = get_sentiment_score([user_news])
        data["public_sentiment"] = (
            data.get("public_sentiment", 0.0) + user_sent
        ) / 2

    # Risk skorunu hesapla
    score, scenarios = dw.calculate_risk_score(data)

    # Güncel risk skorunu ekrana yaz
    st.subheader(f"Güncel Risk Skoru: **{score:.2f}**")

    if score > 0.75:
        st.error(
            "\U0001F6A8 UYARI: Risk Seviyesi Yüksek! Piyasalar alarm veriyor. "
            "Kıyamet Saati yaklaşıyor!"
        )
    elif score > 0.55:
        st.warning(
            "\U0001F6A7 DİKKAT: Risk Seviyesi Orta! Gelişmeler yakından takip edilmeli."
        )
    else:
        st.success(
            "\U0001F7E2 NORMAL: Risk Seviyesi Düşük. Piyasalar sakin seyrediyor."
        )

    if scenarios:
        st.info(f"**Tetiklenen Senaryolar:** {', '.join(scenarios)}")

    # Son 7 gün tablosu için skor kaydı
    st.session_state.history.append({"Tarih": selected_date, "Skor": round(score, 2)})
    st.session_state.history = st.session_state.history[-7:]

    # Grafiği çiz ve göster
    st.subheader("Risk Göstergesi Grafiği")
    dw.plot_risk_indicator(score)
    fig = plt.gcf()
    st.pyplot(fig)

    # BIST Crash kontrolü
    if dw.check_bist_crash():
        st.warning("\U0001F6A8 BIST'te ani düşüş tespit edildi!")
else:
    st.info(
        "Verileri güncellemek ve risk skorunu görmek için yukarıdaki butona tıklayın."
    )

st.markdown("---")  # Ayırıcı

# Son 7 günün skor geçmişi
if st.session_state.history:
    st.subheader("Son 7 Günün Risk Skorları")
    df = pd.DataFrame(st.session_state.history)
    df["Tarih"] = pd.to_datetime(df["Tarih"]).dt.strftime("%Y-%m-%d")
    st.table(df.set_index("Tarih"))
