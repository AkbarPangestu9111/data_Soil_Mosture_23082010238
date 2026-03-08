# -*- coding: utf-8 -*-

# 1. Import library yang diperlukan
import streamlit as st          # library utama untuk dashboard
import pandas as pd             # untuk manipulasi data
import matplotlib.pyplot as plt # untuk membuat grafik
import seaborn as sns           # untuk visualisasi yang lebih cantik

# 2. Konfigurasi halaman dashboard
st.set_page_config(
    page_title="Dashboard Soil Moisture",  # judul yang muncul di tab browser
    layout="wide"                          # tata letak lebar
)

# 3. Judul utama dashboard
st.title("🌱 Dashboard Analisis Kelembaban Tanah (Soil Moisture)")

# 4. Fungsi untuk membaca data (dengan cache agar cepat)
@st.cache_data
def load_data():
    # Membaca file CSV, kolom pertama sebagai index (datetime)
    df = pd.read_csv('soil_moisture_1_cleaned.csv', index_col=0, parse_dates=True)
    return df

# 5. Panggil fungsi untuk memuat data
df = load_data()

# 6. Ambil kolom-kolom yang berisi data kelembaban (moisture)
moisture_cols = [col for col in df.columns if 'moisture' in col]

# 7. Sidebar (panel samping) untuk informasi data
st.sidebar.header("Pengaturan")  # judul sidebar
st.sidebar.write(f"**Data shape:** {df.shape}")  # jumlah baris dan kolom
st.sidebar.write(f"**Rentang waktu:** {df.index.min().date()} s/d {df.index.max().date()}")

# ============================================
# 8. Statistik Deskriptif
# ============================================
st.header("📊 Statistik Deskriptif")
# Menampilkan tabel statistik (mean, std, min, dll)
st.dataframe(df[moisture_cols].describe())

# ============================================
# 9. Korelasi Antar Sensor (Heatmap)
# ============================================
st.header("🔗 Korelasi Antar Sensor")
# Buat figure dan axes untuk plot
fig, ax = plt.subplots(figsize=(8, 6))
# Hitung matriks korelasi
corr = df[moisture_cols].corr()
# Gambar heatmap
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5, ax=ax)
ax.set_title('Matriks Korelasi')
# Tampilkan plot di dashboard
st.pyplot(fig)

# ============================================
# 10. Time Series (Tren Waktu)
# ============================================
st.header("📈 Tren Kelembaban dari Waktu ke Waktu")

# Membuat multiselect untuk memilih sensor yang ingin ditampilkan
selected_sensors = st.multiselect(
    "Pilih sensor yang akan ditampilkan",
    options=moisture_cols,          # pilihan yang tersedia
    default=moisture_cols            # pilihan default (semua sensor)
)

# Jika pengguna memilih setidaknya satu sensor
if selected_sensors:
    # Plot time series untuk semua sensor yang dipilih
    fig, ax = plt.subplots(figsize=(12, 6))
    for col in selected_sensors:
        ax.plot(df.index, df[col], label=col, linewidth=1)
    ax.set_xlabel('Waktu')
    ax.set_ylabel('Nilai Kelembaban')
    ax.set_title('Time Series')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # ============================================
    # 11. Filter Rentang Waktu
    # ============================================
    st.subheader("Filter Rentang Waktu")
    # Ambil tanggal minimum dan maksimum dari data
    min_date = df.index.min().date()
    max_date = df.index.max().date()
    
    # Buat input date picker
    start_date = st.date_input("Mulai", min_date)
    end_date = st.date_input("Selesai", max_date)
    
    # Validasi: tanggal mulai harus <= tanggal akhir
    if start_date <= end_date:
        # Filter data berdasarkan tanggal
        mask = (df.index.date >= start_date) & (df.index.date <= end_date)
        df_filtered = df.loc[mask]
        
        if not df_filtered.empty:
            # Plot data yang sudah difilter
            fig2, ax2 = plt.subplots(figsize=(12, 4))
            for col in selected_sensors:
                ax2.plot(df_filtered.index, df_filtered[col], label=col, linewidth=1)
            ax2.set_xlabel('Waktu')
            ax2.set_ylabel('Kelembaban')
            ax2.set_title(f'Time Series ({start_date} s/d {end_date})')
            ax2.legend()
            ax2.grid(True)
            st.pyplot(fig2)
        else:
            st.warning("Tidak ada data pada rentang tersebut.")
    else:
        st.error("Tanggal akhir harus setelah tanggal mulai.")
else:
    st.warning("Pilih setidaknya satu sensor.")

# ============================================
# 12. Distribusi Data
# ============================================
st.header("📊 Distribusi Nilai Kelembaban")

# ---- Histogram ----
st.subheader("Histogram")
# Buat figure dengan subplot 3 baris 2 kolom (karena ada 5 sensor)
fig_hist, axes_hist = plt.subplots(nrows=3, ncols=2, figsize=(15, 10))
# Ratakan array axes agar mudah diakses
axes_hist = axes_hist.flatten()

# Loop untuk setiap sensor
for i, col in enumerate(moisture_cols):
    axes_hist[i].hist(df[col], bins=30, edgecolor='black')
    axes_hist[i].set_title(col)

# Sembunyikan subplot yang tidak terpakai (karena hanya 5 sensor)
for j in range(len(moisture_cols), len(axes_hist)):
    fig_hist.delaxes(axes_hist[j])

# Beri judul keseluruhan
fig_hist.suptitle('Histogram Nilai Kelembaban', fontsize=16)
plt.tight_layout()
st.pyplot(fig_hist)

# ---- Boxplot ----
st.subheader("Boxplot")
fig_box, ax_box = plt.subplots(figsize=(10, 6))
sns.boxplot(data=df[moisture_cols], ax=ax_box)
ax_box.set_title('Boxplot Sensor')
ax_box.set_ylabel('Nilai Kelembaban')
ax_box.grid(True)
st.pyplot(fig_box)

# ============================================
# 13. Opsi Tampilkan Data Mentah
# ============================================
if st.checkbox("Tampilkan data mentah"):
    st.subheader("Data Cleaned")
    st.dataframe(df)

# ============================================
# 14. Footer
# ============================================
st.markdown("---")  # garis pemisah
st.markdown("Dashboard dibuat dengan ❤️ menggunakan Streamlit")