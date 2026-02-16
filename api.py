from fastapi import FastAPI
from pydantic import BaseModel
import joblib

app = FastAPI(title="Car Price Prediction API")

# Load trained model + encoders
model = joblib.load("models/car_price_model.pkl")
le_name = joblib.load("models/le_name.pkl")
le_fuel = joblib.load("models/le_fuel.pkl")
le_trans = joblib.load("models/le_trans.pkl")

# Request body schema
class CarInput(BaseModel):
    year: int
    name: str
    fuel_type: str
    transmission: str


@app.get("/")
def home():
    return {"message": "Car Price Prediction API is live"}


@app.post("/predict")
def predict(data: CarInput):

    try:
        # Encode categorical values
        name_encoded = le_name.transform([data.name])[0]
        fuel_encoded = le_fuel.transform([data.fuel_type])[0]
        trans_encoded = le_trans.transform([data.transmission])[0]

        # Model expects numeric features
        features = [[
            data.year,
            name_encoded,
            fuel_encoded,
            trans_encoded
        ]]

        prediction = model.predict(features)[0]

        return {"predicted_price": int(prediction)}

    except Exception as e:
        return {"error": str(e)}
