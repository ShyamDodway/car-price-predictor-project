#  Automotive Inventory Scraper & Price Prediction System

##  Overview
This project implements a complete end-to-end data pipeline to scrape used vehicle inventory, store and sync records in a database, and apply machine learning to predict vehicle prices. The system is deployed on Render and runs on an automated schedule.

##  Architecture
Scraper → Database Sync → ML Model → API → Deployment

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

##  Live Deployment
[https://your-render-url.onrender.com](https://car-price-predictor-project-2.onrender.com)

##  API Endpoints
- GET /vehicles  
- GET /vehicles/{id}/predict  
- GET /sync-status  
- POST /trigger-sync  

##  ML Model
- Model: Random Forest Regressor  
- Features: Year, Mileage, Fuel Type, Transmission  
- Metrics: MAE, RMSE, R² Score  

## 🛠 Setup (Local)
```bash
pip install -r requirements.txt
python app.py

