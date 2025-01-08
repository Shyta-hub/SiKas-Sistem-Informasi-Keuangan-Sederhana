import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

# Fungsi untuk menghitung ringkasan tahunan
def calculate_yearly_summary(year, transaksi):
    pemasukan = [
        entry for entry in transaksi
        if entry['kategori'] == 'Pendapatan' and entry['tanggal'].year == year
    ]
    pengeluaran = [
        entry for entry in transaksi
        if entry['kategori'] == 'Pengeluaran' and entry['tanggal'].year == year
    ]
    return pemasukan, pengeluaran

# Fungsi untuk prediksi saldo berdasarkan tren
def predict_balance(transaksi, period_months):
    pemasukan_total = sum(entry['jumlah'] for entry in transaksi if entry['kategori'] == 'Pendapatan')
    pengeluaran_total = sum(entry['jumlah'] for entry in transaksi if entry['kategori'] == 'Pengeluaran')

    pemasukan_avg = pemasukan_total / 12
    pengeluaran_avg = pengeluaran_total / 12

    current_balance = pemasukan_total - pengeluaran_total
    prediksi_saldo = [current_balance + (pemasukan_avg - pengeluaran_avg) * (i + 1) for i in range(period_months)]
    pemasukan_prediksi = [pemasukan_avg] * period_months
    pengeluaran_prediksi = [pengeluaran_avg] * period_months

    return prediksi_saldo, pemasukan_prediksi, pengeluaran_prediksi, pemasukan_avg, pengeluaran_avg

# Autentikasi login
users = {
    "admin": "admin123",
    "user": "user123",
}

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state['authenticated'] = True
            st.success("Login berhasil")
        else:
            st.error("Username atau password salah")
else:
    st.sidebar.image("assets/logo_sikas.png", width=100)
    st.sidebar.title("SiKas | Sistem Informasi Keuangan Sederhana")
    menu = ["Dashboard", "Transaksi", "Laporan", "Prediksi Saldo", "Logout"]
    choice = st.sidebar.selectbox("Pilih Menu", menu)

    # Load data transaksi
    try:
        transaksi = pd.read_csv("data/transaksi.csv")
        transaksi['tanggal'] = pd.to_datetime(transaksi['tanggal'])
    except Exception as e:
        st.error(f"Gagal memuat data transaksi: {e}")
        transaksi = []

    # Halaman Dashboard
    if choice == "Dashboard":
        st.title("Dashboard SiKas")
        st.write("Selamat datang di SiKas - Sistem Informasi Keuangan Sederhana.")
        st.write("Aplikasi ini membantu untuk mengelola dan memantau transaksi keuangan Anda.")

    # Halaman Transaksi
    elif choice == "Transaksi":
        st.title("Manajemen Transaksi Kas")
        st.write("Masukkan transaksi keuangan.")
        
        # Input data transaksi
        tanggal = st.date_input("Tanggal Transaksi")
        kategori = st.selectbox("Kategori Transaksi", ["Pendapatan", "Pengeluaran"])
        jumlah = st.number_input("Jumlah Uang", min_value=0.0, format="%.2f")
        deskripsi = st.text_input("Deskripsi Transaksi")
        
        # Tombol untuk menambah transaksi
        if st.button("Tambah Transaksi"):
            new_data = pd.DataFrame({
                'tanggal': [tanggal],
                'kategori': [kategori],
                'jumlah': [jumlah],
                'deskripsi': [deskripsi]
            })
            new_data.to_csv("data/transaksi.csv", mode='a', header=False, index=False)
            st.success(f"Transaksi berhasil ditambahkan: {deskripsi} - {jumlah} IDR")

    # Halaman Laporan
    elif choice == "Laporan":
        st.title("Laporan Keuangan")
        st.write("Menampilkan laporan transaksi keuangan.")
        
        # Filter data berdasarkan tanggal
        start_date = st.date_input("Dari Tanggal", min_value=pd.to_datetime(transaksi['tanggal'].min()))
        end_date = st.date_input("Sampai Tanggal", max_value=pd.to_datetime(transaksi['tanggal'].max()))
        
        filtered_data = transaksi[(transaksi['tanggal'] >= pd.to_datetime(start_date)) &
                                  (transaksi['tanggal'] <= pd.to_datetime(end_date))]
        st.write(filtered_data)

        # Visualisasi laporan pendapatan dan pengeluaran
        grouped_data = filtered_data.groupby('kategori')['jumlah'].sum().reset_index()
        st.bar_chart(grouped_data.set_index('kategori')['jumlah'])

        # Menampilkan total pendapatan dan pengeluaran
        total_income = grouped_data[grouped_data['kategori'] == 'Pendapatan']['jumlah'].sum()
        total_expense = grouped_data[grouped_data['kategori'] == 'Pengeluaran']['jumlah'].sum()
        st.write(f"Total Pendapatan: {total_income} IDR")
        st.write(f"Total Pengeluaran: {total_expense} IDR")
        st.write(f"Sisa Kas: {total_income - total_expense} IDR")

    # Halaman Prediksi Saldo
    elif choice == "Prediksi Saldo":
        st.title("Prediksi Saldo")
        period_months = st.slider("Periode Proyeksi (bulan)", min_value=1, max_value=24, value=12)
        prediksi, pemasukan_prediksi, pengeluaran_prediksi, pemasukan_avg, pengeluaran_avg = predict_balance(transaksi.to_dict(orient='records'), period_months)

        months = [f"Bulan {i}" for i in range(1, period_months + 1)]
        x = range(1, period_months + 1)
        width = 0.4
        plt.figure(figsize=(10, 5))
        plt.bar([i - width / 2 for i in x], pemasukan_prediksi, width=width, label="Pemasukan", color='green', alpha=0.7)
        plt.bar([i + width / 2 for i in x], pengeluaran_prediksi, width=width, label="Pengeluaran", color='red', alpha=0.7)
        plt.xticks(x, months, rotation=45)
        plt.title(f"Prediksi Pemasukan dan Pengeluaran untuk {period_months} Bulan ke Depan")
        plt.ylabel("Jumlah (Rp)")
        plt.xlabel("Periode (Bulan)")
        plt.legend()
        st.pyplot(plt)

        st.write(f"Rata-rata pemasukan per bulan: Rp {pemasukan_avg:,.2f}")
        st.write(f"Rata-rata pengeluaran per bulan: Rp {pengeluaran_avg:,.2f}")

    # Halaman Logout
    elif choice == "Logout":
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state['authenticated'] = False
        st.success("Logout berhasil")
        st.experimental_rerun()