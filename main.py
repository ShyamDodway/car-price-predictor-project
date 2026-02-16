import requests
import json
import pymysql
from datetime import datetime
import os
import subprocess


# ======================================
# DATABASE CONFIG
# ======================================
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "shyam"
DB_NAME = "vehicle_inventory"







# ======================================
import os
import subprocess

# create data folder
os.makedirs("data", exist_ok=True)

# file where backup will be saved
dump_file = "data/vehicle_inventory_dump.sql"

# full path of mysqldump
MYSQLDUMP_PATH = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"

print("Creating SQL backup...")

try:
    with open(dump_file, "w", encoding="utf-8") as f:
        subprocess.run(
            [
                MYSQLDUMP_PATH,
                "-u", DB_USER,
                f"-p{DB_PASSWORD}",
                DB_NAME
            ],
            stdout=f,
            check=True
        )

    print(f"Backup saved at {dump_file}")

except Exception as e:
    print("Backup failed:", e)


# ======================================
# CONNECT TO MYSQL SERVER (NO DB YET)
# ======================================
connection = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)

cursor = connection.cursor()

# ======================================
# CREATE DATABASE IF NOT EXISTS
# ======================================
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
cursor.execute(f"USE {DB_NAME}")

# ======================================
# CREATE TABLE IF NOT EXISTS
# ======================================
create_table_query = """
CREATE TABLE IF NOT EXISTS vehicles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id VARCHAR(50),
    listing_url TEXT,
    vin_num VARCHAR(50) UNIQUE,
    year VARCHAR(10),
    name VARCHAR(255),
    price VARCHAR(50),
    transmission VARCHAR(50),
    fuel_type VARCHAR(50),
    website_url TEXT,
    metadata JSON,
    milage_in_city VARCHAR(50),
    milage_in_highway VARCHAR(50),
    date_scrapped VARCHAR(20),
    scrape_time VARCHAR(20),
    status VARCHAR(20)
);
"""
cursor.execute(create_table_query)

# Turn off autocommit for sync operations
connection.autocommit(False)

# ======================================
# HEADERS & PARAMS
# ======================================
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en',
    'content-type': 'application/json;charset=UTF-8',
    'origin': 'https://www.repentignychevrolet.com',
    'priority': 'u=1, i',
    'referer': 'https://www.repentignychevrolet.com/',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
}

params = {
    'includeMetadata': 'true',
    'location': 'QC',
    'organizationId': '402',
    'organizationUnitId': '1053',
}

# ======================================
# INITIAL REQUEST TO GET TOTAL PAGES
# ======================================
json_data = {
    'pagination': {
        'pageNumber': 1,
        'pageSize': 12,
    },
    'paymentOptionRequest': {
        'cashDown': 0,
        'financePlan': None,
        'kmPerYearPlan': None,
        'lien': 0,
        'paymentFrequency': 52,
        'purchaseMethod': 'cash',
        'saleType': 'retail',
        'taxPlan': 'standard',
        'term': 96,
        'tradeIn': 0,
        'priceIncreaseRollCount': 0,
    },
    'makePriority': [
        41,
        42,
        44,
    ],
    'sortList': [
        {
            'direction': 'ASC',
            'vehicleSortParameter': 'SALE_PRICE',
        },
    ],
    'vehicle': {
        'makeIds': [],
        'modelIds': [],
        'catalogMakeIds': [],
        'catalogModelIds': [],
        'colanderSlug': 'used-not-certified-cadillac',
        'soldDaysShown': 0,
        'textSearch': '',
        'frameStyleIds': [],
        'transmissionIds': [],
        'driveTrainIds': [],
        'fuelIds': [],
        'exteriorColorIds': [],
        'vehicleInventoryStatuses': [
            'FOR_SALE',
            'SOLD',
            'VIRTUAL',
            'ON_HOLD',
        ],
    },
    'isMarketplaceRequest': False,
}

response = requests.post(
    'https://service.vehicles.sm360.ca/inventory/vehicles',
    params=params,
    headers=headers,
    json=json_data,
    verify=False
)

data = response.json()
total_pages = int(data['pagination']['numberOfPages'])

current_scraped_vins = set()

# ======================================
# LOOP THROUGH ALL PAGES
# ======================================
for page in range(1, total_pages + 1):

    json_data['pagination']['pageNumber'] = page

    response = requests.post(
        'https://service.vehicles.sm360.ca/inventory/vehicles',
        params=params,
        headers=headers,
        json=json_data,
        verify=False
    )

    data = response.json()
    vehicles = data.get('inventoryVehicles', [])

    for vehicle in vehicles:

        vin_num = vehicle.get('serialNo', "")
        if not vin_num:
            continue

        current_scraped_vins.add(vin_num)

        vehicle_id = vehicle.get('vehicleId', "")
        listing_url = f"https://www.repentignychevrolet.com/en/used-inventory/details/{vehicle_id}"
        year = vehicle.get('year', "")
        name = f"{vehicle.get('make', {}).get('name','')} {vehicle.get('model', {}).get('name','')}"
        price = vehicle.get('salePrice', "")
        transmission = vehicle.get('transmission', "")
        fuel_type = vehicle.get('fuel', {}).get('name', "")
        website_url = "https://www.repentignychevrolet.com/en/used-inventory"
        metadata = json.dumps(vehicle)

        milage_in_city = ""
        milage_in_highway = ""

        # Date & Time (updated every run)
        now = datetime.now()
        date_scrapped = now.strftime("%d-%m-%Y")
        current_time = now.strftime("%H:%M:%S")

        # INSERT OR UPDATE
        query = """
            INSERT INTO vehicles (
                vehicle_id, listing_url, vin_num, year, name,
                price, transmission, fuel_type, website_url,
                metadata, milage_in_city, milage_in_highway,
                date_scrapped, scrape_time, status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'active')
            ON DUPLICATE KEY UPDATE
                date_scrapped=VALUES(date_scrapped),
                scrape_time=VALUES(scrape_time),
                status='active'
        """

        cursor.execute(query, (
            vehicle_id, listing_url, vin_num, year, name,
            price, transmission, fuel_type, website_url,
            metadata, milage_in_city, milage_in_highway,
            date_scrapped, current_time
        ))

# ======================================
# MARK REMOVED VEHICLES
# ======================================
cursor.execute("SELECT vin_num FROM vehicles")
db_vins = {row['vin_num'] for row in cursor.fetchall()}

removed_vins = db_vins - current_scraped_vins

for vin in removed_vins:
    cursor.execute(
        "UPDATE vehicles SET status='removed' WHERE vin_num=%s",
        (vin,)
    )

# ======================================
# FINALIZE
# ======================================
connection.commit()
cursor.close()
connection.close()

print("Inventory sync completed successfully.")
