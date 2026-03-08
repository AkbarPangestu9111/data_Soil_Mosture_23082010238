import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Konfigurasi halaman
st.set_page_config(page_title="Dashboard Soil Moisture", layout="wide")
st.title("🌱 Dashboard Analisis Kelembaban Tanah (Soil Moisture)")

# ============================================
# Fungsi untuk membaca data dengan path yang aman
# ============================================
@st.cache_data
def load_data():
    """
    Membaca file CSV yang berada di folder yang sama dengan script ini.
    Menggunakan path absolut relatif terhadap lokasi script.
    """
    # Ambil direktori tempat file script ini berada
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Nama file CSV
    file_name = 'soil_moisture_1_cleaned.csv'
    # Gabungkan menjadi path lengkap
    file_path = os.path.join(script_dir, file_name)

    # Cek apakah file benar-benar ada (untuk debugging)
    if not os.path.exists(file_path):
        st.error(f"❌ File tidak ditemukan: {file_path}")
        st.stop()

    # Baca file CSV
    df = pd.read_csv(file_path, index_col=0, parse_dates=True)
    return df

# ============================================
# Memuat data
# ============================================
try:
    df = load_data()
    st.success("✅ Data berhasil dimuat!")
except Exception as e:
    st.error(f"Gagal memuat data: {e}")
    st.stop()

# Daftar kolom moisture
moisture_cols = [col for col in df.columns if 'moisture' in col]

# Sidebar informasi
st.sidebar.header("📋 Informasi Data")
st.sidebar.write(f"**Jumlah baris:** {df.shape[0]}")
st.sidebar.write(f"**Jumlah kolom:** {df.shape[1]}")
st.sidebar.write(f"**Rentang waktu:**")
st.sidebar.write(f"{df.index.min()} s/d {df.index.max()}")

# ============================================
# 1. Statistik Deskriptif
# ============================================
st.header("📊 Statistik Deskriptif")
st.dataframe(df[moisture_cols].describe())

# ============================================
# 2. Korelasi Antar Sensor
# ============================================
st.header("🔗 Korelasi Antar Sensor")
fig, ax = plt.subplots(figsize=(8, 6))
corr = df[moisture_cols].corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5, ax=ax)
ax.set_title('Matriks Korelasi')
st.pyplot(fig)

# ============================================
# 3. Tren Time Series
# ============================================
st.header("📈 Tren Kelembaban dari Waktu ke Waktu")

# Pilihan sensor
selected_sensors = st.multiselect(
    "Pilih sensor yang akan ditampilkan",
    options=moisture_cols,
    default=moisture_cols
)

if selected_sensors:
    fig, ax = plt.subplots(figsize=(12, 6))
    for col in selected_sensors:
        ax.plot(df.index, df[col], label=col, linewidth=1)
    ax.set_xlabel('Waktu')
    ax.set_ylabel('Nilai Kelembaban')
    ax.set_title('Time Series Semua Data')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # Filter rentang waktu
    st.subheader("🔍 Filter Rentang Waktu")
    min_date = df.index.min().date()
    max_date = df.index.max().date()
    start_date = st.date_input("Tanggal mulai", min_date)
    end_date = st.date_input("Tanggal selesai", max_date)

    if start_date <= end_date:
        mask = (df.index.date >= start_date) & (df.index.date <= end_date)
        df_filtered = df.loc[mask]
        if not df_filtered.empty:
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
            st.warning("Tidak ada data pada rentang tanggal tersebut.")
    else:
        st.error("Tanggal akhir harus setelah tanggal mulai.")
else:
    st.warning("Pilih setidaknya satu sensor.")

# ============================================
# 4. Distribusi Data
# ============================================
st.header("📊 Distribusi Nilai Kelembaban")

# Histogram
st.subheader("Histogram")
fig_hist, axes_hist = plt.subplots(nrows=3, ncols=2, figsize=(15, 10))
axes_hist = axes_hist.flatten()
for i, col in enumerate(moisture_cols):
    axes_hist[i].hist(df[col], bins=30, edgecolor='black')
    axes_hist[i].set_title(col)
# Hapus subplot yang tidak terpakai
for j in range(len(moisture_cols), len(axes_hist)):
    fig_hist.delaxes(axes_hist[j])
fig_hist.suptitle('Histogram Nilai Kelembaban', fontsize=16)
plt.tight_layout()
st.pyplot(fig_hist)

# Boxplot
st.subheader("Boxplot")
fig_box, ax_box = plt.subplots(figsize=(10, 6))
sns.boxplot(data=df[moisture_cols], ax=ax_box)
ax_box.set_title('Boxplot Sensor Kelembaban')
ax_box.set_ylabel('Nilai Kelembaban')
ax_box.grid(True)
st.pyplot(fig_box)

# ============================================
# 5. Tampilkan Data Mentah (opsional)
# ============================================
if st.checkbox("Tampilkan data mentah"):
    st.subheader("Data Cleaned")
    st.dataframe(df)

# Footer
st.markdown("---")
st.markdown("Dashboard dibuat dengan ❤️ menggunakan Streamlit")