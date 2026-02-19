from fastapi import FastAPI
from pydantic import BaseModel
import joblib
from datetime import datetime

# pretend DB (replace with real DB later if already built)
vehicles_db = []
last_sync_time = None

app = FastAPI(
    title="Used Car ML Pipeline API",
    description="Automated scraping + database sync + price prediction",
    version="1.0"
)

# Load ML model + encoders
model = joblib.load("models/car_price_model.pkl")
le_name = joblib.load("models/le_name.pkl")
le_fuel = joblib.load("models/le_fuel.pkl")
le_trans = joblib.load("models/le_trans.pkl")


# -----------------------------
# Request schema
# -----------------------------
class CarInput(BaseModel):
    year: int
    name: str
    fuel_type: str
    transmission: str


# -----------------------------
# Home
# -----------------------------
@app.get("/")
def home():
    return {
        "message": "Car Price Prediction API is live",
        "docs": "/docs"
    }


# -----------------------------
# GET ALL VEHICLES
# -----------------------------
@app.get("/vehicles")
def get_vehicles():
    return vehicles_db


# -----------------------------
# PREDICT PRICE FOR VEHICLE
# -----------------------------
@app.post("/predict")
def predict(data: CarInput):

    try:
        name_encoded = le_name.transform([data.name])[0]
        fuel_encoded = le_fuel.transform([data.fuel_type])[0]
        trans_encoded = le_trans.transform([data.transmission])[0]

        features = [[data.year, name_encoded, fuel_encoded, trans_encoded]]
        prediction = model.predict(features)[0]

        return {"predicted_price": int(prediction)}

    except Exception as e:
        return {"error": str(e)}


# -----------------------------
# TRIGGER SCRAPE + SYNC (DEMO)
# -----------------------------
@app.post("/trigger-sync")
def trigger_sync():
    global last_sync_time

    # simulate scraping result
    new_vehicle = {
        "id": len(vehicles_db) + 1,
        "name": "Demo Car",
        "year": 2022,
        "fuel_type": "Gasoline",
        "transmission": "Automatic"
    }

    vehicles_db.append(new_vehicle)
    last_sync_time = datetime.utcnow()

    return {
        "sync": {
            "added": 1,
            "updated": 0,
            "removed": 0,
            "total_active": len(vehicles_db)
        },
        "last_sync": last_sync_time
    }


# -----------------------------
# SYNC STATUS
# -----------------------------
@app.get("/sync-status")
def sync_status():
    return {
        "last_sync": last_sync_time,
        "total_active_vehicles": len(vehicles_db)
    }
