from database import setup_database, get_connection
from scraper import scrape_inventory

def run_sync():
    setup_database()
    connection = get_connection()
    cursor = connection.cursor()

    scraped_vehicles, current_scraped_vins = scrape_inventory()

    for v in scraped_vehicles:
        query = """
        INSERT INTO vehicles (
            vehicle_id, listing_url, vin_num, year, name,
            price, transmission, fuel_type, website_url,
            metadata, milage_in_city, milage_in_highway,
            date_scrapped, scraped_time, status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'active')
        ON DUPLICATE KEY UPDATE
            date_scrapped=VALUES(date_scrapped),
            scraped_time=VALUES(scraped_time),
            status='active'
        """
        cursor.execute(query, v)

    cursor.execute("SELECT vin_num FROM vehicles")
    db_vins = {row['vin_num'] for row in cursor.fetchall()}

    removed_vins = db_vins - current_scraped_vins

    for vin in removed_vins:
        cursor.execute(
            "UPDATE vehicles SET status='removed' WHERE vin_num=%s",
            (vin,)
        )

    connection.commit()
    cursor.close()
    connection.close()
    print("Inventory sync completed successfully.")

if __name__ == "__main__":
    run_sync()
