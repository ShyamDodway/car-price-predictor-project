#  Automotive Inventory Scraper & Price Prediction System

##  Overview
This project implements a complete end-to-end data pipeline to scrape used vehicle inventory, store and sync records in a database, and apply machine learning to predict vehicle prices. The system is deployed on Render and runs on an automated schedule.

## Problem Statement
Used car prices change frequently.
Businesses need an automated system that can:
- Continuously collect new vehicle data
- Requests
- Retrain ML models with fresh data
- Serve predictions via API
- Keep system updated automatically
  
This project simulates a production ML pipeline that solves this.


##  Architecture
Scraper → Dataset → Model Training → Model Saving → FastAPI → Deployment → Automation



##  Tech Stack
- Python
- Requests
- MySQL
- FastAPI
- Scikit-learn
- Render (Deployment)

##  Features
- Automated web scraping with pagination handling
- Database sync (add, update, mark removed)
- 24-hour scheduled sync
- ML-based price prediction (Random Forest)
- REST APIs for inventory and predictions
- Deployed live

##  Project Structure

```
car_price_project/
│
├── data/                        # Scraped dataset & backups
│   ├── vehicle_inventory_data.sql
│   
│
├── models/                      # Trained ML models & encoders
│   ├── car_price_model.pkl
│   ├── le_name.pkl
│   ├── le_fuel.pkl
│   └── le_trans.pkl
├── venv311 
├── api.py                       # FastAPI application (prediction + sync APIs)
├── main.py                      # Scraper + database pipeline
├── ml_model.py                  # Model training & saving script
├── database_sync.py              # real DB sync logic
├── scheduler.py                  # 24-hour automation scheduler
│
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker configuration
├── .gitignore
├── .dockerignore
└── README.md                    # Project documentation
```


##  ML Model
- Model: Random Forest Regressor  
- Features: Name, Year, Fuel Type, Transmission  
- Metrics: MAE, RMSE, R² Score  



##  API Deployment
### Interactive API Documentation (Swagger UI)
https://car-price-predictor-project-2.onrender.com/docs

This page provides an interactive interface to:

Trigger data sync

View vehicles

Predict vehicle prices

Check sync status

##  API Endpoints
- GET /vehicles  
- GET /vehicles/{price}/predict  
- GET /sync-status  
- POST /trigger-sync  

## 🛠 Setup (Local)
```bash
pip install -r requirements.txt
python app.py

##  Docker Support

This project supports containerized deployment using Docker.

###  Build Docker Image

```
docker build -t car-price-api .
```

###  Run Docker Container

```
docker run -p 8000:8000 car-price-api
```

After running the container, open:

```
http://localhost:8000/docs
```

This will open the interactive FastAPI Swagger documentation.


