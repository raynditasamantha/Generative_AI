import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Membuat data dummy untuk simulasi laporan perusahaan
def generate_data(num_rows=100):
    products = ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headset']
    regions = ['Jakarta', 'Bandung', 'Surabaya', 'Medan', 'Bali']
    
    data = []
    start_date = datetime(2025, 1, 1)
    
    for _ in range(num_rows):
        date = start_date + timedelta(days=random.randint(0, 365))
        product = random.choice(products)
        region = random.choice(regions)
        units_sold = random.randint(1, 50)
        price_per_unit = {
            'Laptop': 15000000, 'Mouse': 150000, 'Keyboard': 350000, 
            'Monitor': 2000000, 'Headset': 500000
        }[product]
        total_sales = units_sold * price_per_unit
        
        data.append([date.strftime('%Y-%m-%d'), region, product, units_sold, price_per_unit, total_sales])
    
    df = pd.DataFrame(data, columns=['Tanggal', 'Wilayah', 'Produk', 'Unit_Terjual', 'Harga_Satuan', 'Total_Penjualan'])
    df.to_csv('laporan_penjualan.csv', index=False)
    print("Dataset 'laporan_penjualan.csv' berhasil dibuat!")

if __name__ == "__main__":
    generate_data()