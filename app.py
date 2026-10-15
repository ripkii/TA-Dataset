import streamlit as st
import pandas as pd
import joblib

st.set_page_config(page_title="Deteksi Malware Android", page_icon="🛡️", layout="centered")

st.markdown('''
    <style>
    .main {background-color: #f8fafc;}
    .stButton>button {width: 100%; border-radius: 8px; background-color: #3b82f6; color: white;}
    </style>
''', unsafe_allow_html=True)

st.title("🛡️ Sistem Deteksi Malware Android")
st.write("Unggah file CSV hasil ekstraksi Androguard untuk mendeteksi apakah aplikasi tersebut Aman atau Malware.")

@st.cache_resource
def load_model():
    model = joblib.load('model_malware_rf.pkl')
    fitur_asli = joblib.load('fitur_kolom.pkl')
    return model, fitur_asli

try:
    model, fitur_asli = load_model()
except Exception as e:
    st.warning("Menunggu Model AI. Pastikan file model_malware_rf.pkl dan fitur_kolom.pkl ada di folder yang sama dengan app.py!")
    st.stop()

uploaded_file = st.file_uploader("Upload File CSV Aplikasi Baru", type=["csv"])

if uploaded_file is not None:
    df_upload = pd.read_csv(uploaded_file)
    st.write("Preview Data:", df_upload.head())
    
    if st.button("🔍 Analisis Aplikasi"):
        with st.spinner("Memproses deteksi malware..."):
            
            # 1. Bikin kerangka data 1 baris berisi angka 0 semua, dengan 439 kolom standar AI
            df_uji = pd.DataFrame(0, index=[0], columns=fitur_asli)
            
            # 2. Cocokkan dan timpa nilai 0 dengan data dari CSV lu (jika permission-nya ada)
            for col in df_upload.columns:
                if col in fitur_asli:
                    df_uji.at[0, col] = df_upload.at[0, col]
            
            # 3. Lakukan Prediksi
            prediksi = model.predict(df_uji) 
            
            # 4. Tampilkan Hasil
            st.markdown("---")
            if prediksi[0] == 1:
                st.error("🚨 **BAHAYA!** Aplikasi ini terdeteksi sebagai **MALWARE**.")
            else:
                st.success("✅ **AMAN!** Aplikasi ini terdeteksi sebagai aplikasi **BENIGN**.")
