import streamlit as st
import pandas as pd
import pickle
import os
from androguard.core.apk import APK

# Konfigurasi Halaman Streamlit
st.set_page_config(page_title="Deteksi Malware Android", page_icon="🛡️")

st.title("🛡️ Deteksi Malware Android (TA)")
st.write("Unggah file APK untuk mendeteksi apakah aplikasi tersebut Aman atau Malware.")

# 1. Load Model dan Daftar Kolom Fitur
try:
    with open("model_malware_rf.pkl", "rb") as file:
        model = pickle.load(file)
    with open("fitur_kolom.pkl", "rb") as file:
        fitur_asli = pickle.load(file)
except Exception as e:
    st.error(f"Gagal memuat model atau fitur: {e}")
    st.stop()

# 2. Area Upload File APK (Bukan CSV lagi)
uploaded_file = st.file_uploader("Unggah File .apk", type=["apk"])

if uploaded_file is not None:
    st.success(f"File {uploaded_file.name} berhasil diunggah!")
    
    if st.button("🔍 Analisis Aplikasi"):
        with st.spinner("Membedah APK dan menganalisis permission..."):
            try:
                # Simpan sementara file APK yang diupload agar Androguard bisa membacanya
                temp_apk_path = os.path.join("temp", uploaded_file.name)
                os.makedirs("temp", exist_ok=True)
                with open(temp_apk_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # 3. PROSES EKSTRAKSI (Androguard di dalam Web)
                a = APK(temp_apk_path)
                permissions_ditemukan = a.get_permissions()
                
                # 4. PENYELARASAN DATA
                # Bikin DataFrame 1 baris berisi nilai 0 untuk ke-439 fitur
                df_uji = pd.DataFrame(0, index=[0], columns=fitur_asli)
                
                # Ubah nilai menjadi 1 jika permission ditemukan di APK tersebut
                for perm in permissions_ditemukan:
                    if perm in fitur_asli:
                        df_uji.at[0, perm] = 1

                # 5. PREDIKSI MACHINE LEARNING
                prediksi = model.predict(df_uji)
                
                # 6. TAMPILKAN HASIL
                st.markdown("---")
                if prediksi[0] == 1:
                    st.error("🚨 **BAHAYA!** Aplikasi ini terdeteksi sebagai **MALWARE**.")
                else:
                    st.success("✅ **AMAN!** Aplikasi ini terdeteksi sebagai aplikasi **BENIGN**.")
                
                # Tampilkan rincian permission (Opsional, bagus buat pamer ke dosen)
                with st.expander("Lihat Rincian Permission yang Ditemukan"):
                    if permissions_ditemukan:
                        for p in permissions_ditemukan:
                            st.write(f"- {p}")
                    else:
                        st.write("Aplikasi ini tidak meminta permission apapun.")

            except Exception as e:
                st.error(f"Terjadi kesalahan saat menganalisis APK: {e}")
            
            finally:
                # Bersihkan file APK sementara setelah selesai dianalisis
                if os.path.exists(temp_apk_path):
                    os.remove(temp_apk_path)