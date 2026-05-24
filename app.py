import streamlit as st
import google.generativeai as genai
import pandas as pd
import pyreadstat

# ---------------------------------------------------------
# 1. SAYFA TASARIMI VE ARAYÜZ YAPILANDIRMASI
# ---------------------------------------------------------
st.set_page_config(page_title="SPSS AI Asistan", page_icon="📊", layout="wide")

# ÖZEL CSS ENJEKSİYONU (Kullanıcı Tema Seçimli)
premium_css = """
<style>
/* Sadece en alttaki Streamlit reklamını gizle, üst menüyü (Header) kullanıcılara bırak */
footer {visibility: hidden;}

/* Google Fonts'tan Inter fontunu çek ve tüm sayfaya uygula */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

/* Butonları profesyonel bir mavi tona çek ve gölge ekle */
.stButton>button {
    background-color: #3b82f6; 
    color: #ffffff;
    border-radius: 8px;
    border: none;
    padding: 10px 24px;
    font-weight: 600;
    transition: all 0.3s ease-in-out;
    width: 100%;
}

/* Butonun üzerine gelindiğinde (Hover) oluşacak animasyon */
.stButton>button:hover {
    background-color: #2563eb;
    box-shadow: 0 4px 10px rgba(59, 130, 246, 0.4);
    transform: translateY(-2px);
    color: #ffffff;
}

/* Girdi alanlarının köşelerini yumuşat */
.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    border-radius: 8px;
}
</style>
"""
st.markdown(premium_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. YAPAY ZEKA (GEMINI) AYARLARI
# ---------------------------------------------------------
# Kendi API anahtarını aşağıdaki tırnakların içine yapıştır:
API_KEY = "AIzaSyAtPREU20lwGOdAa6GyLrTcPOIIr_ftCdM"
genai.configure(api_key=API_KEY)

# Sihirli Model Bulucu (Hataları Önler)
try:
    uygun_modeller = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    model = genai.GenerativeModel(uygun_modeller[0])
except Exception as e:
    st.error("API Anahtarı hatalı veya model bulunamadı. Lütfen API anahtarınızı kontrol edin.")

# ---------------------------------------------------------
# 3. YAN MENÜ (SIDEBAR) TASARIMI
# ---------------------------------------------------------
st.sidebar.image("logo.png", width=150)
st.sidebar.title("Navigasyon")
st.sidebar.markdown("Hangi işlemi yapmak istiyorsunuz?")

secim = st.sidebar.radio("Modüller", [
    "💬 SPSS Rehberi & Soru-Cevap", 
    "📂 Veri Seti Analizi (.sav)", 
    "📈 Çıktı (Output) Yorumlayıcı"
])

st.sidebar.divider()
st.sidebar.markdown("**SPSS AI Asistan**")
st.sidebar.caption("Sürüm: 1.0.0")
st.sidebar.caption("Geliştirici: Şevin Baş")

# ---------------------------------------------------------
# 4. MODÜLLERİN İŞLEYİŞİ
# ---------------------------------------------------------

# MODÜL 1: Soru - Cevap Chatbot
if secim == "💬 SPSS Rehberi & Soru-Cevap":
    st.title("💬 SPSS Rehberi ve Soru-Cevap")
    st.markdown("SPSS menüleri, analiz yöntemleri, regresyon veya veri madenciliği algoritmaları hakkında her şeyi sorabilirsiniz.")
    
    soru = st.text_input("Sorunuzu buraya yazın (Örn: Çok değişkenli normallik testi nasıl yapılır?):")
    
    if st.button("Cevapla 🧠"):
        if soru:
            with st.spinner("Yapay zeka yanıtlıyor..."):
                talimat = f"Sen profesyonel bir SPSS eğitmeni ve veri bilimi uzmanısın. Kullanıcının şu sorusuna adım adım, anlaşılır ve akademik bir Türkçe ile cevap ver: {soru}"
                cevap = model.generate_content(talimat)
                st.info(cevap.text)
        else:
            st.warning("Lütfen bir soru yazın.")

# MODÜL 2: Veri Seti Yükleme
elif secim == "📂 Veri Seti Analizi (.sav)":
    st.title("📂 Veri Seti Analizi")
    st.markdown("`.sav` formatındaki SPSS dosyanızı yükleyin ve asistanın verilerinizi incelemesini sağlayın.")
    
    yuklenen_dosya = st.file_uploader("SPSS Dosyası Yükleyin (.sav)", type=["sav"])
    
    if yuklenen_dosya is not None:
        with open("gecici_veri.sav", "wb") as f:
            f.write(yuklenen_dosya.getbuffer())
        
        df, meta = pyreadstat.read_sav("gecici_veri.sav")
        st.success("Veri seti sisteme yüklendi!")
        
        st.write("**İlk 5 Satır Önizlemesi:**")
        st.dataframe(df.head(), use_container_width=True)
        
        komut = st.text_area("Bu veriyle ne yapalım? (Örn: Değişkenleri incele, normallik dağılımı hakkında yorum yap):")
        
        if st.button("Veriyi Analiz Et ✨"):
            if komut:
                with st.spinner("Veriler işleniyor..."):
                    veri_ozeti = df.describe().to_string()
                    sutunlar = ", ".join(df.columns.tolist())
                    
                    talimat = f"Uzman bir istatistikçisin. Değişkenler: {sutunlar}.\nİstatistiksel özet:\n{veri_ozeti}\nKullanıcı isteği: {komut}\nAkademik bir rapor sun."
                    cevap = model.generate_content(talimat)
                    st.success(cevap.text)
            else:
                st.warning("Lütfen bir komut girin.")

# MODÜL 3: Output Yorumlayıcı
elif secim == "📈 Çıktı (Output) Yorumlayıcı":
    st.title("📈 Çıktı ve Tablo Yorumlayıcı")
    st.markdown("SPSS'ten aldığınız ANOVA, T-Testi, Regresyon veya Normallik testi Output tablolarını buraya yapıştırın.")
    
    output_metni = st.text_area("SPSS Output kopyasını buraya yapıştırın:", height=250)
    
    if st.button("Tabloyu Yorumla 📊"):
        if output_metni:
            with st.spinner("Tablolar okunuyor ve yorumlanıyor..."):
                talimat = f"Sen akademik bir biyoistatistik uzmanısın. Aşağıdaki SPSS Output sonuçlarını incele, p değerlerini, F/t değerlerini ve anlamlılık düzeylerini belirterek detaylıca yorumla. Hipotezleri reddedip reddetmeyeceğimizi açıkla:\n\n{output_metni}"
                cevap = model.generate_content(talimat)
                st.success(cevap.text)
        else:
            st.warning("Lütfen yorumlanacak tabloyu yapıştırın.")
