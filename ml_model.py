import pandas as pd
import pymysql
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
import joblib
connection = pymysql.connect(
    host="localhost",
    user="root",
    password="shyam",
    database="vehicle_inventory"
)

query = "SELECT * FROM vehicles WHERE status='active';"
df = pd.read_sql(query, connection)
connection.close()

print("Rows loaded:", len(df))

df = df[['name','year','price','fuel_type','transmission']]
df = df[df['price'].notna()]
df['price'] = df['price'].astype(str).str.replace(',', '').astype(float)

df['year'] = df['year'].astype(int)
le_name = LabelEncoder()
le_fuel = LabelEncoder()
le_trans = LabelEncoder()

df['name'] = le_name.fit_transform(df['name'])
df['fuel_type'] = le_fuel.fit_transform(df['fuel_type'])
df['transmission'] = le_trans.fit_transform(df['transmission'])
X = df.drop("price", axis=1)
y = df["price"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestRegressor(n_estimators=200)
model.fit(X_train, y_train)

# ==============================
# EVALUATE
# ==============================
preds = model.predict(X_test)

mae = mean_absolute_error(y_test, preds)
rmse = root_mean_squared_error(y_test, preds)
r2 = r2_score(y_test, preds)

print("\nMODEL PERFORMANCE")
print("MAE  :", round(mae,2))
print("RMSE :", round(rmse,2))
print("R2   :", round(r2,2))


# ==============================
# SAVE MODEL + ENCODERS
# ==============================
joblib.dump(model, "models/car_price_model.pkl")
joblib.dump(le_name, "models/le_name.pkl")
joblib.dump(le_fuel, "models/le_fuel.pkl")
joblib.dump(le_trans, "models/le_trans.pkl")

print("Model saved successfully")
