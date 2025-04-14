from selenium import webdriver
from bs4 import BeautifulSoup
import mysql.connector
import csv
import re
import json
import time

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="scraper",
    password="ScraperPass456!",
    database="lawyers_db"
)
cursor = db.cursor()

# Clear existing data (optional: comment out to keep old data)
cursor.execute("TRUNCATE TABLE lawyers")

# Open CSV file
csv_path = r'C:\Users\farih\OneDrive\Desktop\560\finalproj\lawyers_output.csv'
with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['name', 'profile_url', 'address', 'phone', 'rating', 'website', 'education', 'awards', 'specialization'])

    # Set up Selenium
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    # Scrape 90 pages
    url = "https://www.avvo.com/all-lawyers/ca/los_angeles.html"
    for page in range(90):
        print(f"Scraping page {page + 1}")
        driver.get(url)
        time.sleep(2)  # Extra wait for dynamic content
        driver.implicitly_wait(15)  # Increased wait
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Debug: Save page source for last page
        if page == 15:
            with open(r'C:\Users\farih\OneDrive\Desktop\560\finalproj\page_source.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)

        # Find lawyer cards
        cards = soup.find_all("div", class_="serp-card")
        print(f"Found {len(cards)} cards")
        for card in cards:
            try:
                # Get name from JSON-LD
                json_ld = card.find("script", type="application/ld+json")
                ld_data = json.loads(json_ld.text) if json_ld else {}
                name = ld_data.get("name", "Unknown")
                print(f"Processing: {name}")
                
                # Profile URL
                profile_url = ld_data.get("url", "") or card.find("a", href=True)["href"] if card.find("a", href=True) else ""
                
                # Address
                address = ld_data.get("worksFor", {}).get("address", {}).get("streetAddress", "") + ", " + \
                          ld_data.get("worksFor", {}).get("address", {}).get("addressLocality", "") + ", " + \
                          ld_data.get("worksFor", {}).get("address", {}).get("addressRegion", "") + " " + \
                          ld_data.get("worksFor", {}).get("address", {}).get("postalCode", "")
                
                # Other JSON-LD fields
                phone = ld_data.get("worksFor", {}).get("telephone", "")
                education = ", ".join([edu["name"] for edu in ld_data.get("alumniOf", [])])
                awards = ld_data.get("award", "")

                # Website
                website = card.find("a", class_="v-cta-organic-mobile-website")
                website = website["href"] if website else ""

                # Rating
                rating_tag = card.find("span", class_="review-score")
                rating = float(rating_tag.text) if rating_tag else None

                # Specialization: Clean up
                specialization_tag = card.find("div", class_=lambda x: x and "practice" in x.lower())
                specialization = specialization_tag.text.strip() if specialization_tag else ""
                specialization = re.sub(r'Practice Areas:|\n|and more', '', specialization).strip()
                specialization = re.sub(r'\s+', ' ', specialization)
                print(f"Specialization: {specialization}")

                # Insert into MySQL
                cursor.execute(
                    "INSERT INTO lawyers (name, profile_url, address, phone, rating, website, education, awards, specialization) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (name, profile_url, address, phone, rating or None, website, education, awards, specialization or None)
                )

                # Write to CSV
                writer.writerow([name, profile_url, address, phone, rating, website, education, awards, specialization])

            except Exception as e:
                print(f"Error on card: {e}")
                continue

        db.commit()

        # Next page: Broader selector
        next_link = soup.find("a", {"rel": "next"}) or soup.find("a", class_=lambda x: x and "next" in x.lower())
        if not next_link:
            print("No next page found, stopping.")
            break
        next_href = next_link.get("href", "")
        url = "https://www.avvo.com" + next_href if next_href.startswith("/") else next_href
        time.sleep(5)

# Cleanup
driver.quit()
db.close()
print("Done! Data saved to lawyers_output.csv and MySQL.")