import streamlit as st
import requests
import pandas as pd
import numpy as np  # ← Pastikan ada
from datetime import datetime, timedelta  # ← Pastikan ada timedelta
from sklearn.linear_model import LinearRegression  # ← Pastikan ada
import matplotlib.pyplot as plt  # ← Tambahkan baris ini

# ==== KUNCI API & PENGATURAN ====
API_KEY = "a4b9fe4c709c0c39576f8734d07160f7"
SATUAN = "metric"

# ==== NAMA FILE & KOLOM DATA KOTA ====
NAMA_FILE_EXCEL = "Data_Kota.xlsx"
NAMA_KOLOM_KOTA = "NamaKota"
# ======================================

# ==== BACA DAFTAR KOTA DARI FILE EXCEL ====
@st.cache_data
def ambil_daftar_kota(file_excel, nama_kolom_kota):
    try:
        df = pd.read_excel(file_excel)
        daftar_kota = sorted(df[nama_kolom_kota].dropna().drop_duplicates().tolist())
        return daftar_kota
    except Exception as e:
        st.error(f"❌ Gagal membaca file: {e}")
        st.info("ℹ️ Menggunakan daftar kota cadangan...")
        return [
            "Aceh" , "Ambon", "Balikpapan", "Bandung",
            "Batam", "Denpasar", "Jakarta", "Jayapura", "Kupang",
            "Makassar", "Malang", "Manado", "Medan", "Padang",
            "Semarang", "Surabaya", "Yogyakarta"
        ]

DAFTAR_KOTA = ambil_daftar_kota(NAMA_FILE_EXCEL, NAMA_KOLOM_KOTA)

#---- menu utama - tambahan -----

menu = st.sidebar.selectbox(
    "==== MENU GEDE ====",
    "📋 Menu Utama",
    ["☀️Cuaca Saat Ini & Ramalan", "🔮 Prediksi Suhu 7 Hari ke Depan"]
)

if menu == "☀️Cuaca Saat Ini & Ramalan":  # ← BARIS INI DITAMBAHKAN! #-------- menu 1 -------

    #### ----- batas tambahan -----

    # ==== PILIHAN TEMA WARNA ====
    pilihan_tema = st.sidebar.selectbox(
        "🎨 Pilih Tema Warna",
        ["Terang", "Gelap", "Biru Laut", "Hijau Segar"]
    )

    warna_latar = "#FFFFFF"
    warna_teks = "#000000"
    warna_kartu = "#F0F2F6"

    if pilihan_tema == "Gelap":
        warna_latar = "#1E1E1E"
        warna_teks = "#FFFFFF"
        warna_kartu = "#2D2D2D"
    elif pilihan_tema == "Biru Laut":
        warna_latar = "#E6F2FF"
        warna_teks = "#003366"
        warna_kartu = "#CCE5FF"
    elif pilihan_tema == "Hijau Segar":
        warna_latar = "#F0FFF0"
        warna_teks = "#003300"
        warna_kartu = "#CCFFCC"

    st.markdown(f"""
    <style>
        .stApp {{ background-color: {warna_latar}; color: {warna_teks}; }}
        .stInfo {{ background-color: {warna_kartu}; color: {warna_teks}; }}
    </style>
    """, unsafe_allow_html=True)

    # ==== JUDUL & PILIHAN KOTA ====
    st.title("🌤️ Informasi Cuaca — @MatKoncar")
    kota_terpilih = st.sidebar.selectbox(
        "📍 Pilih Kota",
        DAFTAR_KOTA,
        index=0
    )
    st.markdown(f"### 📍 Cuaca di <u>{kota_terpilih}</u>", unsafe_allow_html=True)

    # ==== FUNGSI: CUACA SAAT INI ====
    def ambil_cuaca_sekarang(kota, kunci_api, satuan):
        url = f"https://api.openweathermap.org/data/2.5/weather?q={kota},ID&appid={kunci_api}&units={satuan}&lang=id"
        try:
            respon = requests.get(url, timeout=30)
            data = respon.json()
            if data["cod"] == 200:
                return {
                    "kota": kota,
                    "waktu": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "kondisi": data["weather"][0]["description"],
                    "suhu": round(data["main"]["temp"], 1),
                    "terasa": round(data["main"]["feels_like"], 1),
                    "kelembapan": data["main"]["humidity"],
                    "angin": round(data["wind"]["speed"], 2)
                }
            return None
        except:
            return None

    # ==== FUNGSI: RAMALAN CUACA 5 HARI ====
    def ambil_ramalan(kota, kunci_api, satuan):
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={kota},ID&appid={kunci_api}&units={satuan}&lang=id"
        try:
            respon = requests.get(url, timeout=30)
            data = respon.json()
            if data["cod"] == "200":
                daftar_ramalan = []
                for item in data["list"][::8]:
                    daftar_ramalan.append({
                        "tanggal": item["dt_txt"][:10],
                        "jam": item["dt_txt"][11:16],
                        "kondisi": item["weather"][0]["description"],
                        "suhu": round(item["main"]["temp"], 1)
                    })
                return daftar_ramalan
            return None
        except:
            return None

    # ==== FUNGSI: SIMPAN RIWAYAT ====
    def simpan_riwayat(data_cuaca):
        nama_file = "Riwayat_Cuaca.xlsx"
        baris_baru = pd.DataFrame([data_cuaca])
        try:
            df_lama = pd.read_excel(nama_file)
            df_gabung = pd.concat([df_lama, baris_baru], ignore_index=True)
        except:
            df_gabung = baris_baru
        df_gabung.to_excel(nama_file, index=False)
        return nama_file

    # =============================================================
    # ==== TAMPILAN UTAMA: CUACA SAAT INI + RAMALAN DULU ====
    # =============================================================
    cuaca = ambil_cuaca_sekarang(kota_terpilih, API_KEY, SATUAN)

    if cuaca:
        st.info(f"""
    ☀️ Kondisi      : **{cuaca['kondisi'].title()}**  
    🌡️ Suhu         : **{cuaca['suhu']} °C**  
    🥵 Terasa Seperti: **{cuaca['terasa']} °C**  
    💧 Kelembapan   : **{cuaca['kelembapan']} %**  
    🌬️ Kecepatan Angin: **{cuaca['angin']} m/s**
        """)

        # Simpan riwayat otomatis
        file_riwayat = simpan_riwayat(cuaca)

        # ==== GRAFIK SUHU & RAMALAN KOTA TERPILIH ====
        st.subheader("📊 Grafik Suhu & Ramalan 5 Hari Ke Depan")
        ramalan = ambil_ramalan(kota_terpilih, API_KEY, SATUAN)
        
        if ramalan:
            df_ramalan = pd.DataFrame(ramalan)
            df_ramalan["tanggal_tampil"] = pd.to_datetime(df_ramalan["tanggal"]).dt.strftime("%d-%b")
            df_ramalan[f"Suhu di {kota_terpilih} (°C)"] = df_ramalan["suhu"]

            # ==== GRAFIK DENGAN LABEL ANGKA SUHU ====
            fig, ax = plt.subplots(figsize=(10, 5))
            
            # Gambar garis suhu
            ax.plot(df_ramalan["tanggal_tampil"], df_ramalan["suhu"], marker='o', linewidth=2, color="#1f77b4")
            
            # Tambahkan label angka di atas setiap titik
            for i, baris in df_ramalan.iterrows():
                ax.text(i, baris["suhu"] + 0.3, f"{baris['suhu']}", 
                        ha="center", va="bottom", fontsize=11, fontweight="bold", color="#ff4444")
            
            # Atur tampilan grafik
            ax.set_title(f"Grafik Suhu — {kota_terpilih}", fontsize=14, pad=20)
            ax.set_xlabel("Tanggal", fontsize=12)
            ax.set_ylabel("Suhu (°C)", fontsize=12)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Tampilkan di Streamlit
            st.pyplot(fig, use_container_width=True)

            # Tabel data tetap sama
            st.table(df_ramalan[["tanggal", "tanggal_tampil", "jam", "kondisi", "suhu"]].rename(columns={
                "tanggal": "Tanggal Lengkap",
                "tanggal_tampil": "Tanggal",
                "jam": "Jam",
                "kondisi": "Kondisi Cuaca",
                "suhu": "Suhu (°C)"
            }))
        
        else:
            st.error(f"❌ Kota **{kota_terpilih}** tidak ditemukan di layanan cuaca.")

    # =============================================================
    # ==== GRAFIK PERBANDINGAN SUHU — DIPINDAH KE BAWAH ====
    # =============================================================
    st.divider()  # Garis pemisah agar rapi
    st.subheader("📊 Informasi Suhu di beberapa Kota-Kota Besar Indonesia")

    KOTA_BESAR_DARI_CADANGAN = [
        "Surabaya", "Jakarta", "Bandung", "Semarang",
        "Medan", "Makassar", "Denpasar", "Palembang",
        "Balikpapan", "Malang"
    ]

    data_perbandingan = []
    kemajuan = st.progress(0)

    with st.spinner("🔄 Mengambil data suhu dari berbagai kota..."):
        for indeks, kota in enumerate(KOTA_BESAR_DARI_CADANGAN):
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?q={kota},ID&appid={API_KEY}&units={SATUAN}"
                respon = requests.get(url, timeout=30)
                data = respon.json()
                
                if data["cod"] == 200:
                    data_perbandingan.append({
                        "Kota": kota,
                        "Suhu (°C)": round(data["main"]["temp"], 1),
                        "Terasa Seperti (°C)": round(data["main"]["feels_like"], 1),
                        "Kelembapan (%)": data["main"]["humidity"]
                    })
            except:
                pass
            
            kemajuan.progress((indeks + 1) / len(KOTA_BESAR_DARI_CADANGAN))

    kemajuan.empty()

    if data_perbandingan:
        df_besar = pd.DataFrame(data_perbandingan)
        
        st.line_chart(
            df_besar,
            x="Kota",
            y="Suhu (°C)",
            use_container_width=True,
            height=400,
            color="#FF6B6B"
        )
        
        st.subheader("📋 Data Lengkap")
        st.dataframe(df_besar, use_container_width=True, hide_index=True)
        
    else:
        st.warning("⚠️ Tidak dapat mengambil data perbandingan kota-kota besar.")


if menu == "🔮 Prediksi Suhu 7 Hari ke Depan": # ------ Menu ke-2 ---------

    ##===== program tambahan ======

    # =============================================================
    # ==== JIKA PILIHAN: PREDIKSI 7 HARI KE DEPAN ====
    # =============================================================
    if menu == "🔮 Prediksi Suhu 7 Hari ke Depan":
        st.divider()
        st.title("🔮 Prediksi Suhu 7 Hari ke Depan")
        st.markdown("Mempelajari riwayat suhu → memprediksi suhu untuk setiap kota")

        # Baca data riwayat
        @st.cache_data
        def baca_data_riwayat():
            nama_file = "Riwayat_Cuaca.xlsx"
            try:
                df = pd.read_excel(nama_file)
                df["waktu"] = pd.to_datetime(df["waktu"], dayfirst=True)
                df["tanggal"] = df["waktu"].dt.date
                return df
            except FileNotFoundError:
                st.error("❌ Berkas Riwayat_Cuaca.xlsx TIDAK DITEMUKAN!")
                st.info("💡 Silakan lihat cuaca beberapa kota terlebih dahulu agar berkas riwayat dibuat.")
                return None
            except Exception as e:
                st.error(f"❌ Gagal membaca berkas: {e}")
                return None

        df = baca_data_riwayat()

        if df is not None and len(df) >= 5:
            # Daftar kota
            daftar_kota = sorted(df["kota"].dropna().unique().tolist())
            st.subheader(f"📋 Kota yang Dipelajari: {', '.join(daftar_kota)}")

            # Tanggal prediksi
            tanggal_terakhir = df["tanggal"].max()
            tanggal_prediksi = [tanggal_terakhir + timedelta(days=i+1) for i in range(7)]
            tanggal_label = [t.strftime("%d-%b") for t in tanggal_prediksi]

            # Prediksi per kota
            hasil_prediksi = []
            for kota in daftar_kota:
                df_kota = df[df["kota"] == kota].sort_values("tanggal").copy()
                if len(df_kota) < 3:
                    st.info(f"ℹ️ {kota}: Data belum cukup (minimal 3 hari)")
                    continue

                df_kota["Hari"] = np.arange(1, len(df_kota) + 1)
                X = df_kota[["Hari"]]
                y = df_kota["suhu"]
                model = LinearRegression()
                model.fit(X, y)

                hari_terakhir = len(df_kota)
                suhu_7_hari = []
                for hari_ke in range(hari_terakhir + 1, hari_terakhir + 8):
                    suhu = model.predict([[hari_ke]])[0]
                    suhu_7_hari.append(round(suhu, 1))

                hasil_prediksi.append({
                    "Kota": kota,
                    **{tanggal_label[i]: suhu_7_hari[i] for i in range(7)}
                })

            # Tampilkan hasil
            if hasil_prediksi:
                st.subheader("🎯 Tabel Prediksi Suhu")
                df_hasil = pd.DataFrame(hasil_prediksi).set_index("Kota")
                st.dataframe(df_hasil, use_container_width=True)

                # Grafik
                st.subheader("📊 Grafik Prediksi")
                fig, ax = plt.subplots(figsize=(12, 6))
                warna = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"]
                for idx, baris in enumerate(hasil_prediksi):
                    kota = baris["Kota"]
                    suhu = [baris[tgl] for tgl in tanggal_label]
                    ax.plot(tanggal_label, suhu, marker="o", linewidth=2, color=warna[idx % len(warna)], label=kota)
                ax.set_xlabel("Tanggal")
                ax.set_ylabel("Suhu (°C)")
                ax.grid(True, alpha=0.3)
                ax.legend(title="Kota")
                plt.xticks(rotation=0)
                st.pyplot(fig, use_container_width=True)

                st.subheader("📝 Ringkasan")
                st.info(f"📅 Periode: {tanggal_label[0]} s.d. {tanggal_label[-1]} | 🏙️ {len(hasil_prediksi)} kota diprediksi")
            else:
                st.warning("⚠️ Belum ada data yang cukup untuk prediksi.")
        else:
            st.warning("⚠️ Data riwayat belum cukup — silakan lihat cuaca beberapa hari terlebih dahulu.")