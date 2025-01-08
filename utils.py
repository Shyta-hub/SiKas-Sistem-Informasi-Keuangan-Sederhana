import matplotlib.pyplot as plt

def plot_data(data):
    # Contoh fungsi untuk visualisasi data
    data.plot(kind='bar', x='kategori', y='jumlah', title='Pendapatan vs Pengeluaran')
    plt.show()