from datetime import datetime
import pandas as pd
import requests
import streamlit as st

# Konfigurasi Halaman Web
st.set_page_config(
    page_title="Aplikasi Absensi Online", page_icon="📝", layout="wide"
)

# ==========================================
# GANTI DENGAN URL WEB APP GOOGLE APPS SCRIPT ANDA
# ==========================================
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwHQwaK0QXObIin7fLTZX097gOkE68k7uYUqroQETxnI3MNX7ETvemeymvJBh_yw-xzDw/exec"


# Fungsi untuk mengambil data dari Google Sheets
def load_data_from_sheet():
  if WEB_APP_URL == "MASUKKAN_URL_WEB_APP_ANDA_DI_SINI":
    return pd.DataFrame(columns=["Waktu", "Nama", "Status", "Keterangan"])
  try:
    response = requests.get(WEB_APP_URL)
    if response.status_code == 200:
      data = response.json()
      if data:
        return pd.DataFrame(data)
    return pd.DataFrame(columns=["Waktu", "Nama", "Status", "Keterangan"])
  except Exception:
    return pd.DataFrame(columns=["Waktu", "Nama", "Status", "Keterangan"])


# Load data saat aplikasi dibuka
df_absensi = load_data_from_sheet()

# --- TAMPILAN ANTARMUKA (UI) ---
st.title("📝 Sistem Absensi Online (Google Sheets)")
st.markdown(
    "Silakan isi form di bawah ini untuk melakukan absensi kehadiran, izin,"
    " atau sakit."
)
st.markdown("---")

if WEB_APP_URL == "MASUKKAN_URL_WEB_APP_ANDA_DI_SINI":
  st.error(
      "⚠️ Perhatian: URL Google Apps Script belum dimasukkan di dalam kodenya!"
      " Harap isi variabel `WEB_APP_URL` terlebih dahulu."
  )

# Layout menjadi 2 kolom
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
      elif WEB_APP_URL == "MASUKKAN_URL_WEB_APP_ANDA_DI_SINI":
        st.error("⚠️ URL Google Sheets belum dikonfigurasi!")
      else:
        waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        payload = {
            "waktu": waktu_sekarang,
            "nama": nama,
            "status": status,
            "keterangan": keterangan if keterangan else "-",
        }

        try:
          # Kirim data ke Google Sheets via Web App
          response = requests.post(WEB_APP_URL, json=payload)
          if response.status_code == 200:
            st.success(
                f"✅ Terima kasih, {nama}! Absensi Anda berhasil disimpan ke"
                " Google Sheets."
            )
            st.rerun()
          else:
            st.error("❌ Gagal menyimpan ke Google Sheets. Coba lagi.")
        except Exception as e:
          st.error(f"Terjadi kesalahan koneksi: {e}")

with col2:
  st.subheader("📊 Data & Progres Absensi Terkini")

  if df_absensi.empty:
    st.info(
        "Belum ada data absensi yang masuk atau sedang memuat dari Google"
        " Sheets."
    )
  else:
    # Filter Status
    filter_status = st.selectbox(
        "Filter berdasarkan Status:", ["Semua", "Hadir", "Izin", "Sakit"]
    )

    if filter_status != "Semua" and "Status" in df_absensi.columns:
      df_display = df_absensi[df_absensi["Status"] == filter_status]
    else:
      df_display = df_absensi

    # Statistik Ringkas
    total_semua = len(df_absensi)
    total_hadir = (
        len(df_absensi[df_absensi["Status"] == "Hadir"])
        if "Status" in df_absensi.columns
        else 0
    )
    total_izin = (
        len(df_absensi[df_absensi["Status"] == "Izin"])
        if "Status" in df_absensi.columns
        else 0
    )
    total_sakit = (
        len(df_absensi[df_absensi["Status"] == "Sakit"])
        if "Status" in df_absensi.columns
        else 0
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Absen", total_semua)
    m2.metric("Hadir", total_hadir)
    m3.metric("Izin", total_izin)
    m4.metric("Sakit", total_sakit)

    st.markdown("---")

    # Tabel Data
    st.dataframe(df_display.iloc[::-1], use_container_width=True, hide_index=True)

    # Tombol Refresh
    if st.button("🔄 Refresh Data"):
      st.rerun()
