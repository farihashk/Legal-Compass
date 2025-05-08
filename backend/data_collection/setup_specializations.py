import mysql.connector
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
import json

# Paths
BASE_DIR = Path(r"C:\Users\farih\OneDrive\Desktop\560\finalproj")
MAPPING_PATH = BASE_DIR / "specialization_mapping.json"
OUTPUT_CSV_PATH = BASE_DIR / "specializations.csv"

# MySQL connection
db_config = {
    "host": "localhost",
    "user": "scraper",
    "password": "ScraperPass456!",
    "database": "lawyers_db"
}
engine = create_engine(f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}")

# Step 1: Create tables
def create_tables():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Create specializations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS specializations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) UNIQUE,
            category VARCHAR(50)
        );
    """)
    
    # Create junction table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lawyer_specializations (
            lawyer_id INT,
            specialization_id INT,
            PRIMARY KEY (lawyer_id, specialization_id),
            FOREIGN KEY (lawyer_id) REFERENCES lawyers(id),
            FOREIGN KEY (specialization_id) REFERENCES specializations(id)
        );
    """)
    
    conn.commit()
    cursor.close()
    conn.close()

# Step 2: Populate specializations
def populate_specializations():
    # Load mapping
    with open(MAPPING_PATH, "r") as f:
        mapping = json.load(f)
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Insert specializations
    for spec, cat in mapping.items():
        cursor.execute(
            "INSERT IGNORE INTO specializations (name, category) VALUES (%s, %s);",
            (spec, cat)
        )
    
    conn.commit()
    
    # Get lawyer data
    query = "SELECT id, specialization FROM lawyers;"
    df_lawyers = pd.read_sql(query, engine)
    
    # Link lawyers to specializations
    for _, row in df_lawyers.iterrows():
        if row["specialization"]:
            specs = [s.strip() for s in row["specialization"].split(", ")]
            lawyer_id = row["id"]
            for spec in specs:
                cursor.execute("SELECT id FROM specializations WHERE name = %s;", (spec,))
                result = cursor.fetchone()
                if result:
                    spec_id = result[0]
                    cursor.execute(
                        "INSERT IGNORE INTO lawyer_specializations (lawyer_id, specialization_id) VALUES (%s, %s);",
                        (lawyer_id, spec_id)
                    )
    
    conn.commit()
    cursor.close()
    conn.close()

# Step 3: Export to CSV
def export_to_csv():
    query = "SELECT * FROM specializations;"
    df = pd.read_sql(query, engine)
    df.to_csv(OUTPUT_CSV_PATH, index=False)

# Main
if __name__ == "__main__":
    try:
        create_tables()
        populate_specializations()
        export_to_csv()
        print(f"Specializations table created and populated.")
        print(f"CSV saved at {OUTPUT_CSV_PATH}")
    except Exception as e:
        print(f"Error: {e}")