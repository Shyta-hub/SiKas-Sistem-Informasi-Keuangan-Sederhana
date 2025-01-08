import pandas as pd

def preprocess_data(data):
    # Contoh fungsi untuk membersihkan atau memformat data
    data['tanggal'] = pd.to_datetime(data['tanggal'])
    return data