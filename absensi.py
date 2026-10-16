import os
from datetime import datetime
import pandas as pd
import streamlit as st

# Konfigurasi Halaman Web
st.set_page_config(
    page_title="Aplikasi Absensi Online", page_icon="📝", layout="wide"
)

# File untuk menyimpan data absensi secara permanen
DATA_FILE = "absensi_data.csv"


# Fungsi untuk memuat data
def load_data():
  if os.path.exists(DATA_FILE):
    return pd.read_csv(DATA_FILE)
  else:
    # Membuat DataFrame kosong jika file belum ada
    return pd.DataFrame(columns=["Waktu", "Nama", "Status", "Keterangan"])


# Fungsi untuk menyimpan data
def save_data(df):
  df.to_csv(DATA_FILE, index=False)


# Load data saat aplikasi dibuka
df_absensi = load_data()

# --- TAMPILAN ANTARMUKA (UI) ---
st.title("📝 Sistem Absensi Online")
st.markdown(
    "Silakan isi form di bawah ini untuk melakukan absensi kehadiran, izin,"
    " atau sakit."
)
st.markdown("---")

# Layout menjadi 2 kolom (Kolom Form & Kolom Rekap/Live Feed)
col1, col2 = st.columns([1, 2], gap="large")

with col1:
  st.subheader("✍️ Form Absen")
  with st.form("form_absensi", clear_on_submit=True):
    nama = st.text_input("Nama Lengkap", placeholder="Masukkan nama Anda...")
    status = st.selectbox(
        "Keterangan Kehadiran", ["Hadir", "Izin", "Sakit"], index=0
    )
    keterangan = st.text_area(
        "Catatan / Keterangan (Opsional)",
        placeholder="Contoh: Ada keperluan keluarga / Surat dokter terlampir",
    )

    submit_button = st.form_submit_button(
        label="Kirim Absen", use_container_width=True
    )

    if submit_button:
      if nama.strip() == "":
        st.warning("⚠️ Mohon masukkan nama lengkap Anda terlebih dahulu!")
      else:
        # Waktu saat ini (WITA/WIB sesuai sistem)
        waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Data baru
        new_row = pd.DataFrame({
            "Waktu": [waktu_sekarang],
            "Nama": [nama],
            "Status": [status],
            "Keterangan": [keterangan if keterangan else "-"],
        })

        # Gabungkan dan simpan
        df_absensi = pd.concat([df_absensi, new_row], ignore_index=True)
        save_data(df_absensi)

        st.success(f"✅ Terima kasih, {nama}! Absensi Anda berhasil dicatat.")
        st.rerun()

with col2:
  st.subheader("📊 Data & Progres Absensi Terkini")

  if df_absensi.empty:
    st.info(
        "Belum ada data absensi yang masuk. Jadilah yang pertama mengisi!"
    )
  else:
    # Filter Pencarian atau Status
    filter_status = st.selectbox(
        "Filter berdasarkan Status:", ["Semua", "Hadir", "Izin", "Sakit"]
    )

    if filter_status != "Semua":
      df_display = df_absensi[df_absensi["Status"] == filter_status]
    else:
      df_display = df_absensi

    # Statistik Ringkas
    total_hadir = len(df_absensi[df_absensi["Status"] == "Hadir"])
    total_izin = len(df_absensi[df_absensi["Status"] == "Izin"])
    total_sakit = len(df_absensi[df_absensi["Status"] == "Sakit"])
    total_semua = len(df_absensi)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Absen", total_semua)
    m2.metric("Hadir", total_hadir)
    m3.metric("Izin", total_izin)
    m4.metric("Sakit", total_sakit)

    st.markdown("---")

    # Tabel Data (Urut dari yang terbaru)
    st.dataframe(df_display.iloc[::-1], use_container_width=True, hide_index=True)

    # Tombol Refresh untuk melihat pembaruan dari perangkat lain
    if st.button("🔄 Refresh Data"):
      st.rerun()