import os
import pandas as pd
from sqlalchemy import create_engine
from pymongo import MongoClient
from prefect import task, flow

# ==========================================
#   TASKS: SMALL PIPELINE STEPS
# ==========================================

@task(retries=2, retry_delay_seconds=10, name="Extract Data")
def extract_multi_source():
    print("Mengekstraksi data dari 4 sumber berbeda...")
    
    # PostgreSQL
    pg_engine = create_engine('postgresql://admin_properti:password123@localhost:5432/db_properti_internal')
    df_sql = pd.read_sql('SELECT * FROM t_transaksi_properti', pg_engine)
    
    # MongoDB
    mongo_client = MongoClient('mongodb://admin_properti:password123@localhost:27017/')
    mongo_db = mongo_client['db_properti_unstructured']
    mongo_collection = mongo_db['detail_interior']
    mongo_data = list(mongo_collection.find({}, {'_id': 0}))
    df_mongo = pd.DataFrame(mongo_data)
    
    # CSV & Excel
    primary_path = os.path.join('..','data_source')
    df_csv = pd.read_csv(os.path.join(primary_path, 'tren_ekonomi_kota.csv'))
    df_excel = pd.read_excel(os.path.join(primary_path, 'zonasi_wilayah_pemda.xlsx'))
    
    return df_sql, df_mongo, df_csv, df_excel, pg_engine


@task(name="Transform & Feature Engineering")
def transform_data(df_sql, df_mongo, df_csv, df_excel):
    print("Menjalankan transformasi data & Feature Engineering untuk AI...")
    
    # 1. Merge PostgreSQL and MongoDB based on property_id
    df_transformed = pd.merge(df_sql, df_mongo, on='id_properti', how='inner')
    
    # 2. Merge with Excel based on 'id_property'
    df_transformed = pd.merge(df_transformed, df_excel, on='id_properti', how='left')
    
    # 3. Merge with CSV of economic trends by city name (since CSV only contains 11 unique rows of cities)
    df_transformed = pd.merge(df_transformed, df_csv, left_on='kota', right_on='nama_kota', how='left')
    
    # 4. Create New Features for AI (Use columns from Excel that are already 1-to-1 synced)
    df_transformed['is_industrial'] = df_transformed['gaya_arsitektur'].str.contains('Industrial', case=False).astype(int)
    df_transformed['bebas_banjir'] = df_transformed['Zona_Bebas_Banjir'].apply(lambda x: 1 if x == 'YA' else 0)
    
    # 5. Clear columns that are no longer needed
    df_transformed = df_transformed.drop(columns=['nama_kota', 'Kota_Administrasi_y', 'Kota_Administrasi_x', 'Zona_Bebas_Banjir'], errors='ignore')
    df_transformed['tingkat_inflasi_lokal_persen'] = df_transformed['tingkat_inflasi_lokal_persen'].fillna(df_transformed['tingkat_inflasi_lokal_persen'].mean())
    
    return df_transformed


@task(name="Load into Feature Store", cache_policy=None)
def load_data(df_clean, pg_engine):
    print("Memuat data bersih ke Target Warehouse...")
    df_clean.to_sql('t_fitur_properti_siap_ai', pg_engine, if_exists='replace', index=False)


# ==========================================
# 🔀 FLOW: MAIN ORCHESTRATION (DIRECTOR)
# ==========================================

@flow(name="Properti ETL Pipeline Engine")
def main_etl_flow():
    # 1. Extract
    df_sql, df_mongo, df_csv, df_excel, pg_engine = extract_multi_source()
    
    # 2. Transform
    df_clean = transform_data(df_sql, df_mongo, df_csv, df_excel)
    
    # 3. Load
    load_data(df_clean, pg_engine)


if __name__ == "__main__":
    # Run Orchestration Flow
    main_etl_flow()