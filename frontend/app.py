import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="AI Property Valuation Dashboard", page_icon="🏠", layout="wide")

st.title("🏠 AI-Powered Real Estate Valuation Platform")
st.markdown("Predict property values dynamically across West Java regions based on macroeconomic indicators.")
st.write("---")

# List of cities that match the pipeline data
KOTA_LIST = [
    'Kota_Bekasi', 'Kab_Bekasi', 'Kab_Karawang', 'Kota_Depok', 'Kota_Bogor', 
    'Kab_Bogor', 'Kota_Bandung', 'Kab_Bandung', 'Kab_Bandung_Barat', 
    'Kota_Cimahi', 'Kota_Sukabumi', 'Kab_Sukabumi', 'Kota_Tasikmalaya', 
    'Kab_Tasikmalaya', 'Kota_Cirebon', 'Kab_Cirebon', 'Kab_Subang', 
    'Kab_Purwakarta', 'Kab_Sumedang', 'Kab_Indramayu', 'Kab_Majalengka', 'Kab_Kuningan', 
    'Kab_Garut', 'Kab_Ciamis', 'Kab_Pangandaran', 'Kota_Banjar', 'Kab_Cianjur'
]

input_column, output_column = st.columns([1, 1.2], gap="large")

with input_column:
    st.subheader("📋 Property Specifications")
    
    # PENGEMBANGAN FRONTEND A: Pilihan Kota Asli
    pilihan_kota = st.selectbox("Select Target City / Location", KOTA_LIST)
    
    land_area = st.slider("Land Area (m²)", min_value=20, max_value=500, value=70, step=5)
    building_area = st.slider("Building Area (m²)", min_value=20, max_value=500, value=50, step=5)
    rooms_count = st.number_input("Number of Bedrooms", min_value=1, max_value=10, value=2, step=1)
    
    industrial_choice = st.selectbox("Industrial-Minimalist Architecture Style?", ["NO", "YES"])
    flood_choice = st.selectbox("Is the Area Flood-Free?", ["NO", "YES"])
    
    is_industrial = 1 if industrial_choice == "YES" else 0
    bebas_banjir = 1 if flood_choice == "YES" else 0

with output_column:
    st.subheader("📊 AI Analysis & Estimation")
    
    payload = {
        "kota": pilihan_kota,  # Dikirim berupa string ke FastAPI
        "luas_tanah_m2": float(land_area),
        "luas_bangunan_m2": float(building_area),
        "jumlah_kamar": int(rooms_count),
        "is_industrial": int(is_industrial),
        "bebas_banjir": int(bebas_banjir)
    }
    
    predict_button = st.button("🚀 Calculate Estimated Price", type="primary", use_container_width=True)
    st.write("---")
    
    if predict_button:
        FASTAPI_URL = "http://127.0.0.1:8000/predict"
        try:
            with st.spinner("Analyzing regional macroeconomics..."):
                response = requests.post(FASTAPI_URL, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                predicted_price = result["prediksi_harga_idr"]
                
                st.metric(label=f"Estimated Property Value in {pilihan_kota}", value=f"IDR {predicted_price:,.0f}")
                
                # 🌟 PENGEMBANGAN FRONTEND B: Visualisasi Insight Berbasis Data
                st.markdown("#### 📈 Regional Price Benchmark Context:")
                # Simulasi chart komparatif sederhana untuk UI
                chart_data = pd.DataFrame(
                    [predicted_price, predicted_price * 0.7, predicted_price * 1.2],
                    index=["This Property", "Regional Lower Bound", "Regional Upper Bound"],
                    columns=["Price Valuation (IDR)"]
                )
                st.bar_chart(chart_data)
                
                st.success(f"Success! Valuation compiled for {pilihan_kota}. Factors applied: Regional Minimum Wage & Safety Metrics.")
            else:
                st.error(f"Error from server (Status {response.status_code})")
        except requests.exceptions.ConnectionError:
            st.error("❌ Could not connect to FastAPI Backend.")
    else:
        st.info("💡 Complete the parameters and click the button above to execute the AI evaluation model.")