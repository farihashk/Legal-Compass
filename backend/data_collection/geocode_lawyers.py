import mysql.connector
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
import requests
import time
import urllib.parse

# Paths
BASE_DIR = Path(r"C:\Users\farih\OneDrive\Desktop\560\finalproj")
CSV_PATH = BASE_DIR / "lawyers_updated.csv"
OUTPUT_CSV_PATH = BASE_DIR / "lawyers_geocoded.csv"

# MySQL connection
db_config = {
    "host": "localhost",
    "user": "scraper",
    "password": "ScraperPass456!",
    "database": "lawyers_db"
}
engine = create_engine(f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}")

# Geocod.io setup
GEOCODIO_API_KEY = "e7ee16733763fcf5ef66d6767ff3fd315dd7513"  # Replace with new key from https://dash.geocod.io/

# Step 1: Ensure columns exist
def ensure_columns():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SHOW COLUMNS FROM lawyers LIKE 'latitude';")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE lawyers ADD COLUMN latitude FLOAT, ADD COLUMN longitude FLOAT;")
    conn.commit()
    cursor.close()
    conn.close()

# Step 2: Clean address
def clean_address(address):
    if not address:
        return None
    address = address.replace("Aveune", "Avenue").replace("#", "").strip()
    return address

# Step 3: Geocode addresses
def geocode_addresses():
    query = "SELECT name, address FROM lawyers;"
    df = pd.read_sql(query, engine)
    
    df["latitude"] = None
    df["longitude"] = None
    
    for idx, row in df.iterrows():
        address = clean_address(row["address"])
        if not address:
            print(f"Skipping empty address for {row['name']}")
            continue
        try:
            encoded_address = urllib.parse.quote(address)
            url = f"https://api.geocod.io/v1.7/geocode?q={encoded_address}&api_key={GEOCODIO_API_KEY}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data.get("results"):
                loc = data["results"][0]["location"]
                df.at[idx, "latitude"] = loc["lat"]
                df.at[idx, "longitude"] = loc["lng"]
                print(f"Geocoded {address}: ({loc['lat']}, {loc['lng']})")
            else:
                print(f"No results for {address}")
            time.sleep(0.1)  # Rate limit
        except requests.RequestException as e:
            print(f"Failed to geocode {address}: {e}")
    
    return df

# Step 4: Update MySQL and CSV
def update_dataset(df):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Update rows
    for _, row in df.iterrows():
        if pd.notnull(row["latitude"]) and pd.notnull(row["longitude"]):
            cursor.execute(
                "UPDATE lawyers SET latitude = %s, longitude = %s WHERE name = %s AND address = %s;",
                (row["latitude"], row["longitude"], row["name"], row["address"])
            )
    
    conn.commit()
    
    # Save full table to CSV
    query = "SELECT * FROM lawyers;"
    df_full = pd.read_sql(query, engine)
    df_full.to_csv(OUTPUT_CSV_PATH, index=False)
    
    cursor.close()
    conn.close()

# Main
if __name__ == "__main__":
    try:
        ensure_columns()
        df = geocode_addresses()
        update_dataset(df)
        print(f"Geocoded CSV saved at {OUTPUT_CSV_PATH}")
    except Exception as e:
        print(f"Error: {e}")