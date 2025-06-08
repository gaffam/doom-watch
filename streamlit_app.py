# Streamlit arayüzü.
# doom_watch modülündeki fonksiyonları kullanarak risk göstergesini günceller.

import datetime
import matplotlib
matplotlib.use("Agg")  # Arayüzde grafik gösterebilmek için
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

import doom_watch as dw

# Uygulama başlığı
st.title("Türkiye Ekonomisi Kıyamet Saati")

# Oturumda skor geçmişi tutulur
if "history" not in st.session_state:
    st.session_state.history = []

# Tarih seçici (simülasyon amaçlı)
selected_date = st.date_input("\U0001F4C5 Tarih Seç", value=datetime.date.today())

# Veriyi güncelleyen buton
if st.button("Veriyi Güncelle"):
    # Seçilen tarih bilgisi kullanılmıyor, veri rastgele üretiliyor
    data = dw.get_live_data()
    score, _ = dw.calculate_risk_score(data)

    # Güncel risk skorunu ekrana yaz
    st.subheader(f"Güncel Risk Skoru: {score:.2f}")
    if score > 0.75:
        st.error("UYARI: Risk Seviyesi Yüksek!")

    # Son 7 gün tablosu için skor kaydı
    st.session_state.history.append({"Tarih": selected_date, "Skor": round(score, 2)})
    st.session_state.history = st.session_state.history[-7:]

    # Grafiği çiz ve göster
    dw.plot_risk_indicator(score)
    fig = plt.gcf()
    st.pyplot(fig)
else:
    st.info("Verileri güncellemek için butona tıklayın.")

# Son 7 günün skor geçmişi
if st.session_state.history:
    st.subheader("Son 7 Günün Risk Skorları")
    df = pd.DataFrame(st.session_state.history)
    st.table(df)
