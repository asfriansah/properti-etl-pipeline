import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd

# 1. FastAPI App Initialization
primary_path = os.path.join('..', 'models')
app = FastAPI(
    title="Real Estate Property AI Predictor API",
    description="API untuk memprediksi harga properti berdasarkan fitur arsitektur hasil ETL",
    version="1.0.0"
)

# 2. load the trained model and city encoding map
try:
    model = joblib.load(os.path.join(primary_path, 'model_prediksi_harga.pkl'))
    peta_harga_kota = joblib.load(os.path.join(primary_path, 'peta_harga_kota.pkl')) # Muat peta encoding kota
except FileNotFoundError:
    raise RuntimeError("Model files are missing.")

# 3. Define the input data model for prediction
class PropertyInput(BaseModel):
    kota: str  # Parameter baru berupa nama kota (string)
    luas_tanah_m2: float
    luas_bangunan_m2: float
    jumlah_kamar: int
    is_industrial: int
    bebas_banjir: int

# 4. Primary Endpoint (Checks API status)
@app.get("/")
def home():
    return {"status": "Online", "message": "Welcome to Real Estate AI Prediction API"}

# 5. Endpoint Primary for Price Prediction
@app.post("/predict")
def predict_price(data: PropertyInput):
    try:
        # Get the encoded value for the city; if not found, use the average of all cities
        kota_encoded = peta_harga_kota.get(data.kota, sum(peta_harga_kota.values()) / len(peta_harga_kota))
        
        # Arrange the input features in the same order as the model expects
        input_features = [[
            data.luas_tanah_m2,
            data.luas_bangunan_m2,
            data.jumlah_kamar,
            data.is_industrial,
            data.bebas_banjir,
            kota_encoded  # Fitur ke-6
        ]]
        
        prediction_raw = model.predict(input_features)[0]
        prediction_clean = float(prediction_raw.item()) if hasattr(prediction_raw, "item") else float(prediction_raw)
        
        return {
            "status": "Success",
            "prediksi_harga_idr": round(prediction_clean, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))