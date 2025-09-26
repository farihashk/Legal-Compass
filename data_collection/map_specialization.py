import mysql.connector
import pandas as pd
import json
from pathlib import Path
from collections import Counter
from sqlalchemy import create_engine

# Paths
BASE_DIR = Path(r"C:\Users\farih\OneDrive\Desktop\560\finalproj")
CSV_PATH = BASE_DIR / "lawyers_output.csv"
OUTPUT_CSV_PATH = BASE_DIR / "lawyers_updated.csv"
MAPPING_PATH = BASE_DIR / "specialization_mapping.json"

# MySQL connection (SQLAlchemy)
db_config = {
    "host": "localhost",
    "user": "scraper",
    "password": "ScraperPass456!",
    "database": "lawyers_db"
}
engine = create_engine(f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}")

# MySQL connector for updates
conn_config = {
    "host": "localhost",
    "user": "scraper",
    "password": "ScraperPass456!",
    "database": "lawyers_db"
}

# Step 1: Export specializations
def export_specializations():
    query = "SELECT specialization FROM lawyers;"
    df = pd.read_sql(query, engine)
    all_specs = set()
    for specs in df["specialization"]:
        if specs:  # Check for None/NULL
            for spec in specs.split(", "):
                all_specs.add(spec.strip())
    return list(all_specs)

# Step 2: Create manual mapping
def create_mapping(specializations):
    # Manual mapping dictionary (edit this)
    manual_mapping = {
            "Administrative Law": "Government",
    "Admiralty & Maritime": "Transportation",
    "Adoption": "Family Law",
    "Advertising": "Media Law",
    "Agriculture": "Environmental and Natural Resources",
    "Alimony": "Family Law",
    "Animal & Dog Bites": "Personal Injury",
    "Animal Law": "Environmental and Natural Resources",
    "Antitrust & Trade Law": "Business Law",
    "Appeals": "Litigation",
    "Arbitration": "Dispute Resolution",
    "Asylum": "Immigration Law",
    "Aviation": "Transportation",
    
    "Banking": "Financial Law",
    "Bankruptcy & Debt": "Bankruptcy Law",
    "Birth Injury": "Personal Injury",
    "Brain Injury": "Personal Injury",
    "Business": "Business Law",
    
    "Cannabis Law": "Regulatory Law",
    "Car Accidents": "Personal Injury",
    "Chapter 11 Bankruptcy": "Bankruptcy Law",
    "Chapter 13 Bankruptcy": "Bankruptcy Law",
    "Chapter 7 Bankruptcy": "Bankruptcy Law",
    "Child Abuse": "Family Law",
    "Child Custody": "Family Law",
    "Child Support": "Family Law",
    "Civil Rights": "Civil Rights Law",
    "Class Action": "Litigation",
    "Commercial": "Business Law",
    "Communications & Media": "Media Law",
    "Computer Fraud": "Cyber Law",
    "Constitutional": "Constitutional Law",
    "Construction & Development": "Real Estate Law",
    "Consumer Protection": "Consumer Law",
    "Contracts & Agreements": "Business Law",
    "Copyright Application": "Intellectual Property",
    "Copyright Infringement": "Intellectual Property",
    "Corporate & Incorporation": "Business Law",
    "Credit Card Fraud": "Criminal Law",
    "Credit Repair": "Consumer Law",
    "Criminal Defense": "Criminal Law",
    
    "DUI & DWI": "Criminal Law",
    "Debt & Lending Agreements": "Banking Law",
    "Debt Collection": "Consumer Law",
    "Debt Settlement": "Bankruptcy Law",
    "Defective and Dangerous Products": "Personal Injury",
    "Discrimination": "Employment Law",
    "Divorce & Separation": "Family Law",
    "Domestic Violence": "Family Law",
    "Drug Crime": "Criminal Law",
    
    "Education": "Education Law",
    "Elder Law": "Family Law",
    "Election Campaigns & Political Law": "Government",
    "Employee Benefits": "Employment Law",
    "Employment & Labor": "Employment Law",
    "Energy & Utilities": "Environmental and Natural Resources",
    "Entertainment": "Media Law",
    "Environmental and Natural Resources": "Environmental and Natural Resources",
    "Equipment Finance and Leasing": "Financial Law",
    "Estate Planning": "Wills, Trusts & Estates",
    "Ethics & Professional Responsibility": "Legal Ethics",
    "Expungement": "Criminal Law",
    
    "Family": "Family Law",
    "Federal Crime": "Criminal Law",
    "Federal Regulation": "Administrative Law",
    "Financial Markets and Services": "Financial Law",
    "Foreclosure": "Real Estate Law",
    "Franchising": "Business Law",
    
    "Gaming": "Entertainment Law",
    "General Practice": "General Practice",
    "Government": "Government",
    "Government Contracts": "Government",
    "Guardianship": "Family Law",
    "Gun Law": "Criminal Law",
    
    "Health Care": "Health Law",
    "Health Insurance": "Insurance Law",
    
    "Identity Theft": "Cyber Law",
    "Immigration": "Immigration Law",
    "Insurance": "Insurance Law",
    "Insurance Fraud": "Criminal Law",
    "Intellectual Property": "Intellectual Property",
    "International Law": "International Law",
    "Internet": "Cyber Law",
    
    "Juvenile": "Criminal Law",
    
    "LGBT+ Law": "Civil Rights Law",
    "Land Use & Zoning": "Real Estate Law",
    "Landlord & Tenant": "Real Estate Law",
    "Lawsuits & Disputes": "Litigation",
    "Lemon Law": "Consumer Law",
    "Libel & Slander": "Media Law",
    "Licensing": "Business Law",
    "Life Insurance": "Insurance Law",
    "Life Sciences & Biotechnology": "Health Law",
    "Limited Liability Company (LLC)": "Business Law",
    "Litigation": "Litigation",
    
    "Marriage & Prenuptials": "Family Law",
    "Mediation": "Alternative Dispute Resolution",
    "Medicaid & Medicare": "Health Law",
    "Medical Malpractice": "Personal Injury",
    "Mergers & Acquisitions": "Business Law",
    "Mesothelioma & Asbestos": "Personal Injury",
    "Military Law": "Government",
    "Motorcycle Accident": "Personal Injury",
    
    "Native Peoples Law": "Civil Rights Law",
    "Nursing Home Abuse and Neglect": "Personal Injury",
    
    "Oil & Gas": "Environmental and Natural Resources",
    
    "Partnership": "Business Law",
    "Patent Application": "Intellectual Property",
    "Patent Infringement": "Intellectual Property",
    "Personal Injury": "Personal Injury",
    "Power Of Attorney": "Wills, Trusts & Estates",
    "Privacy": "Cyber Law",
    "Probate": "Wills, Trusts & Estates",
    "Project Finance": "Financial Law",
    "Public Finance & Tax Exempt Finance": "Financial Law",
    
    "Real Estate": "Real Estate Law",
    "Residential": "Real Estate Law",
    
    "Securities & Investment Fraud": "Financial Law",
    "Securities Offerings": "Financial Law",
    "Sex Crime": "Criminal Law",
    "Sexual Harassment": "Employment Law",
    "Slip and Fall Accident": "Personal Injury",
    "Social Security": "Government Benefits Law",
    "Speeding & Traffic Ticket": "Criminal Law",
    "Spinal Cord Injury": "Personal Injury",
    "State, Local And Municipal Law": "Government",
    
    "Tax": "Tax Law",
    "Tax Fraud & Tax Evasion": "Criminal Law",
    "Telecommunications": "Media Law",
    "Trademark Application": "Intellectual Property",
    "Trademark Infringement": "Intellectual Property",
    "Transportation": "Transportation",
    "Trucking Accident": "Personal Injury",
    "Trusts": "Wills, Trusts & Estates",
    
    "Uncontested Divorce": "Family Law",
    
    "Venture Capital": "Business Law",
    "Violent Crime": "Criminal Law",
    
    "White Collar Crime": "Criminal Law",
    "Wills & Living Wills": "Wills, Trusts & Estates",
    "Workers Compensation": "Employment Law",
    "Wrongful Death": "Personal Injury",
    "Wrongful Termination": "Employment Law",
    "Legal Malpractice": "Legal Ethics",
    "Technology Transactions": "Intellectual Property",
    "Artificial Intelligence Law": "Cyber Law",
    "E-commerce": "Cyber Law",
    "Biotech Law": "Health Law",
    "Elections Law": "Government",
    "Payday Loan Regulation": "Consumer Law",
    "Data Protection": "Cyber Law",
    "Aviation": "Transportation Law",
    "Admiralty & Maritime": "Transportation Law"
    }
    
    mapping = {}
    for spec in specializations:
        mapping[spec] = manual_mapping.get(spec, "Other")
    
    # Save mapping
    with open(MAPPING_PATH, "w") as f:
        json.dump(mapping, f, indent=2)
    
    return mapping

# Step 3: Update MySQL and CSV
def update_dataset(mapping):
    conn = mysql.connector.connect(**conn_config)
    cursor = conn.cursor()
    
    # Add category column if not exists
    cursor.execute("ALTER TABLE lawyers ADD COLUMN category VARCHAR(50);")
    
    # Update rows
    cursor.execute("SELECT specialization FROM lawyers;")
    rows = cursor.fetchall()
    for row in rows:
        specs_str = row[0]
        if specs_str:  # Check for None/NULL
            specs = [s.strip() for s in specs_str.split(", ")]
            categories = [mapping.get(spec, "Other") for spec in specs]
            category = Counter(categories).most_common(1)[0][0] if categories else "Other"
        else:
            category = "Other"
        cursor.execute("UPDATE lawyers SET category = %s WHERE specialization <=> %s;", (category, specs_str))
    
    conn.commit()
    
    # Export to CSV
    query = "SELECT * FROM lawyers;"
    df = pd.read_sql(query, engine)
    df.to_csv(OUTPUT_CSV_PATH, index=False)
    
    cursor.close()
    conn.close()

# Step 4: Prepare for Reddit/documents
def prepare_for_other_datasets(mapping):
    print(f"Mapping saved at {MAPPING_PATH}. Use for Reddit/documents.")

# Main
if __name__ == "__main__":
    specializations = export_specializations()
    print(f"Found {len(specializations)} unique specializations")
    
    mapping = create_mapping(specializations)
    update_dataset(mapping)
    prepare_for_other_datasets(mapping)
    
    print(f"Updated CSV: {OUTPUT_CSV_PATH}")
    print(f"Review mapping: {MAPPING_PATH}")