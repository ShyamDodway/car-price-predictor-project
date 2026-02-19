import os
import time
from datetime import datetime


print("Auto Scheduler started...")

while True:
    print("Starting daily pipeline...")

    # 1️ Run scraper + SQL backup
    print("Running scraper...")
    os.system("python main.py")

    # 2️ Retrain ML model
    print("Training model...")
    os.system("python ml_model.py")

    print("Daily pipeline completed.")
    print("Sleeping for 24 hours...\n")

    # 24 hours sleep
    time.sleep(60 * 60 * 24)
