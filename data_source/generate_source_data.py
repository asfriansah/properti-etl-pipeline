import pandas as pd
import numpy as np
import random
from sqlalchemy import create_engine
from pymongo import MongoClient

print("=== STARTING SOURCE DATA GENERATION (FIXED SYNCHRONOUS - 50000 ROWS) ===")

TOTAL_DATA = 50000
KOTA_LIST = [
    'Kota_Bekasi', 'Kab_Bekasi', 'Kab_Karawang', 'Kota_Depok', 'Kota_Bogor', 
    'Kab_Bogor', 'Kota_Bandung', 'Kab_Bandung', 'Kab_Bandung_Barat', 
    'Kota_Cimahi', 'Kota_Sukabumi', 'Kab_Sukabumi', 'Kota_Tasikmalaya', 
    'Kab_Tasikmalaya', 'Kota_Cirebon', 'Kab_Cirebon', 'Kab_Subang', 
    'Kab_Purwakarta', 'Kab_Sumedang', 'Kab_Indramayu', 'Kab_Majalengka', 'Kab_Kuningan', 
    'Kab_Garut', 'Kab_Ciamis', 'Kab_Pangandaran', 'Kota_Banjar', 'Kab_Cianjur'
]

UMR_MAPPING = {
    'Kota_Bekasi': 5_999_443, 
    'Kab_Bekasi': 5_938_885,
    'Kab_Karawang': 5_886_853, 
    'Kota_Depok': 5_522_662, 
    'Kota_Bogor': 5_437_203,
    'Kab_Bogor': 5_161_769,
    'Kota_Bandung': 4_737_678,
    'Kab_Bandung': 3_972_202,
    'Kab_Bandung_Barat': 3_984_711,
    'Kota_Cimahi': 4_090_568, 
    'Kota_Sukabumi': 3_192_807,
    'Kab_Sukabumi': 3_831_926,
    'Kota_Tasikmalaya': 2_980_336,
    'Kab_Tasikmalaya': 2_871_874,
    'Kota_Cirebon': 2_878_646,
    'Kab_Cirebon': 2_880_798,
    'Kab_Subang': 3_737_482, 
    'Kab_Purwakarta': 5_052_856,
    'Kab_Sumedang': 3_949_856,
    'Kab_Indramayu': 2_910_254,
    'Kab_Majalengka': 2_595_368,
    'Kab_Kuningan': 2_369_380,
    'Kab_Garut': 2_472_227,
    'Kab_Ciamis': 2_373_644,
    'Kab_Pangandaran': 2_351_250,
    'Kota_Banjar': 2_361_241,
    'Kab_Cianjur': 3_316_191
}


data_properti = []
data_interior = []
data_zonasi_excel = []  # Storage for Local Government Excel

random.seed(42)  # Locking coordinates globally

for i in range(1, TOTAL_DATA + 1):
    id_properti = f"PROP_{str(i).zfill(4)}"
    kota = random.choice(KOTA_LIST)
    
    luas_tanah = random.randint(30, 350)
    luas_bangunan = random.randint(25, min(luas_tanah, 280))
    jumlah_kamar = random.randint(1, 5)
    
    gaya_arsitektur = random.choice(['Industrial-Minimalist', 'Classic', 'Scandinavian', 'Modern Tropical'])
    
    # Specify flood status here once for all sources!
    zona_bebas_banjir = random.choice(['YA', 'TIDAK'])
    
    # Base Price Calculation based on UMR
    pengali_umr = UMR_MAPPING[kota] / 3_000_000
    base_price = (luas_bangunan * 6_500_000 * pengali_umr) + (luas_tanah * 4_000_000 * pengali_umr) + (jumlah_kamar * 25_000_000)
    
    if gaya_arsitektur == 'Industrial-Minimalist':
        base_price *= 1.05
        
    if zona_bebas_banjir == 'TIDAK':
        base_price *= 0.80

    # Create random market factors to increase property price variation
    faktor_acak_pasar = random.uniform(0.85, 1.15)
    base_price *= faktor_acak_pasar

    harga_idr = round(base_price, -6)
    
    # 1. Save to PostgreSQL array
    data_properti.append({
        'id_properti': id_properti, 'kota': kota, 'luas_tanah_m2': luas_tanah,
        'luas_bangunan_m2': luas_bangunan, 'harga_idr': harga_idr
    })
    
    # 2. Save to MongoDB array
    data_interior.append({
        'id_properti': id_properti, 'jumlah_kamar': jumlah_kamar, 'gaya_arsitektur': gaya_arsitektur
    })
    
    # 3. Save to Excel array (Value 'zona_bebas_banjir' is guaranteed to be 100% the same as the price formula)
    data_zonasi_excel.append({
        'id_properti': id_properti, 'Kota_Administrasi': kota, 'Zona_Bebas_Banjir': zona_bebas_banjir
    })

# --- UPLOAD PROCESS TO STORAGE ---

# A. PostgreSQL
pg_engine = create_engine('postgresql://admin_properti:password123@localhost:5432/db_properti_internal')
pd.DataFrame(data_properti).to_sql('t_transaksi_properti', pg_engine, if_exists='replace', index=False)
print(f"✔ PostgreSQL Updated ({TOTAL_DATA} rows)")

# B. MongoDB
mongo_client = MongoClient('mongodb://admin_properti:password123@localhost:27017/')
mongo_db = mongo_client['db_properti_unstructured']
mongo_collection = mongo_db['detail_interior']
mongo_collection.drop()
mongo_collection.insert_many(data_interior)
print(f"✔ MongoDB Updated ({TOTAL_DATA} documents)")

# C. CSV Economic Trend (Randomized Inflation Rate for Each City)
data_csv = [{'nama_kota': k, 'umr_2026': umr, 'tingkat_inflasi_lokal_persen': round(random.uniform(2.1, 4.5), 2)} for k, umr in UMR_MAPPING.items()]
pd.DataFrame(data_csv).to_csv('tren_ekonomi_kota.csv', index=False)
print("✔ CSV Created")

# D. Excel Government Zoning (Randomized Flood Zone for Each Property)
pd.DataFrame(data_zonasi_excel).to_excel('zonasi_wilayah_pemda.xlsx', index=False)
print("✔ Excel Created")

print("\n=== Re-Generation Successful and Synchronized! ===")