# 🏠 AI-Powered Real Estate Valuation Platform (End-to-End Pipeline)

Welcome to the **AI-Powered Real Estate Valuation Platform**! This project is a production-grade, end-to-end data intelligence system built entirely using **100% free, open-source technology**. 

The application pulls real estate data from heterogeneous storage engines (Relational & NoSQL), orchestrates it through an ETL pipeline, trains a robust Machine Learning model using advanced feature engineering, and serves dynamic price estimations via a clean web interface.

> 💡 *“Don’t let budget constraints kill your engineering curiosity.”* — This project is a living proof that you can simulate industrial-scale architecture right on a local machine using zero-cost tools.

---

## 🧬 System Architecture & Flow

The system is engineered using a **Decoupled Architecture**, splitting the core responsibilities into independent layers:

```
[ PostgreSQL ] (Structural Data) ──┐

├──> [ Prefect ETL Pipeline ] ──> [ Feature Store (PostgreSQL) ]

[ MongoDB ] (Interior Semi-Struct) ┘

▼

[ Streamlit Web UI ] <── (JSON API) ──> [ FastAPI Backend ] <─── [ Random Forest Model (.pkl) ]
```

1. **Data Layer:** Simulates real-world multi-source ingestion by fetching transaction records from **PostgreSQL** and interior specifications from **MongoDB**.
2. **ETL & Pipe Pipeline:** Automatically cleans, validates, and transforms raw structures, merging streams into a consolidated AI-ready schema.
3. **Serving Layer (FastAPI):** A high-performance REST API endpoints serving inference models instantly.
4. **Presentation Layer (Streamlit):** A clean, highly responsive reactive dashboard for users to adjust inputs and view asset values dynamically.

---

## 🛠️ Key Technical Features & Lessons Learned

* **Anti-Leakage Target Encoding:** To handle categorical string variables (`city`), the pipeline splits data *before* mapping weights, computing historical averages strictly out of the training subset to avoid the classic data leakage illusion.
* **Resilience to Market Noise:** The custom-built synthetic dataset was intentionally corrupted with a $\pm15\%$ random noise variance to simulate erratic real-world markets. The Random Forest model handles this smoothly without overfitting, capturing a robust **96.89% R² Score**.
* **Decoupled Infrastructure:** Separating the application frontend from the AI backend keeps the codebase modular, fast, and scalable.

---

## 🚀 Step-by-Step Installation & Setup

This guide is designed to help anyone—including beginners—get the full platform running locally from scratch.

### 📋 Prerequisites
Make sure you have the following installed on your machine:
* [Python 3.10+](https://www.python.org/downloads/)
* [PostgreSQL](https://www.postgresql.org/download/)
* [MongoDB Community Server](https://www.mongodb.com/try/download/community)

---

### ⚙️ Local Deployment Guide

#### 1. Clone the Repository
Open your terminal or Git Bash and run:
```bash
git clone [https://github.com/YOUR_USERNAME/properti-etl-pipeline.git](https://github.com/YOUR_USERNAME/properti-etl-pipeline.git)
cd properti-etl-pipeline
```

#### 2. Create and Activate Virtual Environment
```bash
# Create environment
python -m venv etl_venv

# Activate environment (Windows)
etl_venv\Scripts\activate

# Activate environment (Mac/Linux)
source etl_venv/bin/activate
```

#### 3. Install Required Packages
```bash
pip install -r requirements.txt
```

#### 4. Run the ETL Pipeline & Train the Model
Ensure your PostgreSQL and MongoDB instances are active locally, then execute:
```bash
# Step A: Run ETL to extract, clean, and store features
python pipeline/etl_pipeline.py

# Step B: Train the Random Forest AI model
python pipeline/train_model.py
```
*Upon completion, your terminal will print the finalized robust performance metrics ($R^2$ and MAE), saving the serialized .pkl files inside your project directory.*

#### 5. Launch the Application Servers
To see the full stack in action, you need to spin up both servers simultaneously in two separate terminal windows (ensure your virtual environment is active in both):

Terminal 1: Start the FastAPI Backend

```bash
uvicorn backend.main:app --reload
```
*The API will be live at http://127.0.0.1:8000*

Terminal 2: Start the Streamlit Frontend Dashboard

```bash
streamlit run frontend/app.py
```
*Your default web browser should automatically open the interface at http://localhost:8501.*

## 📊 Model Performance Analytics
* Model Type: Random Forest Regressor (Ensemble Tree-based)
* Hyperparameters Applied: {'max_depth': 14, 'min_samples_split': 10, 'n_estimators': 100}
* 📈 R-Squared Score (Honest Accuracy): 96.89%📉 
* Mean Absolute Error (MAE): ~IDR 135,555,065 (highly realistic evaluation margin under simulated $\pm15\%$ market chaos).

## 🛠️ Built With (Technologies Used)
* Python - Core Programming Language
* PostgreSQL - Relational Transaction Datastore
* MongoDB - Semi-structured Document Datastore
* Scikit-Learn - Machine Learning Modeling & Cross-Validation
* FastAPI - High-performance REST API Endpoint
* Streamlit - Interactive UI Frontend Components
* Joblib - Object Serialization for Machine Learning artifacts

## 📝 License
Distributed under the MIT License. See LICENSE for more information.

Developed with 💻 and ☕. Keep experimenting!
