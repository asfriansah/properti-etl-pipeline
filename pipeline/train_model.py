import os
import pandas as pd
import joblib
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

print("=== TRAINING AI STARTED ===")

# 1. GET DATA FROM FEATURE STORE
engine = create_engine('postgresql://admin_properti:password123@localhost:5432/db_properti_internal')
df = pd.read_sql('SELECT * FROM t_fitur_properti_siap_ai', engine)
print(f"-> Loading Successful: {len(df):,} columns.")

# Split data di awal sebelum melakukan pembobotan kota
X_raw = df[['kota', 'luas_tanah_m2', 'luas_bangunan_m2', 'jumlah_kamar', 'is_industrial', 'bebas_banjir']]
y = df['harga_idr']

X_train_raw, X_test_raw, y_train, y_test = train_test_split(X_raw, y, test_size=0.2, random_state=42)

# Cleaning and encoding kota for model training (Target Encoding)
# Temporary DataFrame for calculating mean price per city
df_train_temp = X_train_raw.copy()
df_train_temp['harga_idr'] = y_train

peta_harga_kota = df_train_temp.groupby('kota')['harga_idr'].mean().to_dict()
# Save the city encoding map for later use in FastAPI
model_dir = os.path.join('..', 'models')
joblib.dump(peta_harga_kota, os.path.join(model_dir, 'peta_harga_kota.pkl'))

# Apply the encoding to both training and testing sets
X_train = X_train_raw.copy()
X_test = X_test_raw.copy()

X_train['kota_encoded'] = X_train['kota'].map(peta_harga_kota)
X_test['kota_encoded'] = X_test['kota'].map(peta_harga_kota)

# Delete the original 'kota' column as we now have the encoded version
X_train = X_train.drop(columns=['kota'])
X_test = X_test.drop(columns=['kota'])

# 2. HYPERPARAMETER RANDOM FOREST TUNING
print("\n[Tuning Process] Training Random Forest Regressor with GridSearchCV...")
rf_base = RandomForestRegressor(random_state=42, n_jobs=-1)
param_grid = {
    'n_estimators': [100],
    'max_depth': [10, 14, 18], # Limiting the depth of the tree to avoid memorizing noise
    'min_samples_split': [5, 10] # Forces the tree leaves to contain more data sample
}

grid_search = GridSearchCV(estimator=rf_base, param_grid=param_grid, cv=3, scoring='r2', n_jobs=-1)
grid_search.fit(X_train, y_train)

best_rf_model = grid_search.best_estimator_

# 3. EVALUASI AKHIR
predictions = best_rf_model.predict(X_test)
r2 = r2_score(y_test, predictions)
mae = mean_absolute_error(y_test, predictions)

print("\n=== REALISTIC MODEL EVALUATION  ===")
print(f"🏆 Best Parameters: {grid_search.best_params_}")
print(f"📈 R-Squared Score (Honest Accuracy): {r2 * 100:.2f}%")
print(f"📉 Mean Absolute Error (MAE Honest): Rp {mae:,.0f}")

joblib.dump(best_rf_model, os.path.join(model_dir, 'model_prediksi_harga.pkl'))
print("✔ Robust AI Model & City Encoding Map Saved to Disk.")