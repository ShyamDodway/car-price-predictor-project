from fastapi import FastAPI
import pymysql
import joblib
import pandas as pd
import os
from datetime import datetime

app = FastAPI(title="Vehicle Inventory ML API")

# ==============================
# LOAD MODEL FILES
# ==============================
model = joblib.load("models/car_price_model.pkl")
le_name = joblib.load("models/le_name.pkl")
le_fuel = joblib.load("models/le_fuel.pkl")
le_trans = joblib.load("models/le_trans.pkl")

# ==============================
# DB CONNECTION
# ==============================
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="shyam",
        database="vehicle_inventory",
        cursorclass=pymysql.cursors.DictCursor
    )

# ====================================================
# 1️⃣ GET /vehicles  (Assignment requirement)
# ====================================================
@app.get("/vehicles")
def get_vehicles():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, year, fuel_type, transmission, price 
        FROM vehicles
        WHERE status='active'
        LIMIT 50
    """)

    data = cursor.fetchall()
    conn.close()

    return {"vehicles": data}

# ====================================================
# 2️⃣ GET /vehicles/{id}/predict  ⭐ VERY IMPORTANT
# ====================================================
@app.get("/vehicles/{vehicle_id}/predict")
def predict_vehicle_price(vehicle_id:int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, year, fuel_type, transmission, price 
        FROM vehicles
        WHERE id=%s
    """, (vehicle_id,))

    car = cursor.fetchone()
    conn.close()

    if not car:
        return {"error": "Vehicle not found"}

    try:
        df = pd.DataFrame([{
            "name": le_name.transform([car["name"]])[0],
            "year": car["year"],
            "fuel_type": le_fuel.transform([car["fuel_type"]])[0],
            "transmission": le_trans.transform([car["transmission"]])[0]
        }])

        predicted_price = model.predict(df)[0]

        return {
            "vehicle": car,
            "predicted_price": int(predicted_price)
        }

    except:
        return {"error": "Model could not predict this vehicle"}

# ====================================================
# 3️⃣ GET /sync-status
# ====================================================
@app.get("/sync-status")
def sync_status():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(date_scrapped) as last_sync FROM vehicles")
    result = cursor.fetchone()
    conn.close()

    return {
        "last_sync_date": result["last_sync"],
        "status": "successful"
    }

# ====================================================
# 4️⃣ POST /trigger-sync
# ====================================================
@app.post("/trigger-sync")
def trigger_sync():

    # run scraper manually
    os.system("python main.py")

    # retrain model after sync
    os.system("python ml_model.py")

    return {"message": "Manual sync + retraining triggered"}
