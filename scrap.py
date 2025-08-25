import undetected_chromedriver as uc
import time
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


# Target product URL on Newegg
URL = "https://www.newegg.com/amd-ryzen-7-9000-series-ryzen-7-9800x3d-granite-ridge-zen-5-socket-am5-desktop-cpu-processor/p/N82E16819113877"
# SQLite database file name
DB_FILE = "newegg_data.db"

# Set up Chrome options to reduce bot detection
options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Launch undetected Chrome driver with forced version 138
driver = uc.Chrome(version_main=138, options=options)

# Function to load the page and return parsed HTML (BeautifulSoup object)
def page_source(URL, retries=3):
    for attempt in range(retries):
        driver.get(URL)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Check if Newegg presents a CAPTCHA
        title = soup.find("title").text if soup.find("title") else ""
        if title == "Are you a human?":
            print(f"CAPTCHA detected on attempt {attempt+1}, retrying...")
            time.sleep(5)  # wait before retry
            continue
        
        # Wait extra time for page to fully load
        time.sleep(10)
        if soup:
            return soup
    raise Exception(
        "Failed to load page after retries (CAPTCHA still present)")
    
    
# Function to scrape product details and save to SQLite
def scrape_newegg(URL):
    soup = page_source(URL) # Get page content
    all_products = []
    product = {}
    
    # --- Main Product Info Extraction ---
    try:
        # Extract product title (cut off after first hyphen to remove extra detail)
        product['title'] = soup.find(
            "h1", class_="product-title").get_text(strip=True).split("-", 1)[0]
    except:
        product['title'] = None
    try:
        # Extract product brand from brand element
        product['brand'] = soup.find(
            "div", class_="product-view-brand has-brand-store").find("a").get("title")
    except:
        product['brand'] = None
    try:
        # Extract product price
        product['price'] = soup.find(
            "div", class_="row-side").find("div", class_="price-current").get_text(strip=True)
    except:
        product['price'] = None
    try:
        # Extract star rating
        product['rating'] = soup.find(
            "span", class_="item-rating-num").get_text(" ", strip=True).split(" ", 1)[0]
    except:
        product['rating'] = None
    try:
        # Extract short product description
        product['description'] = soup.find(
            "div", class_="product-bullets").get_text(" ", strip=True)
    except:
        product['description'] = None
    all_products.append(product)
    
    # --- Extract Similar Products ---
    try:
        # Locate the similar products container using XPath (Selenium required here)
        sim_container = driver.find_element(
            By.XPATH, '//*[@id="newProductPageContent"]/div/div/div/div[2]/div[2]/div/div[1]/div[4]')
        # sim_container = soup.find_all("div", class_="product-similar-box")
        
        # Find all similar product slides within the carousel
        items = sim_container.find_all("div", class_="swiper-slide")
        for item in items:
            sim = {}
            try:
                # Extract title and trim after first hyphen
                sim['title'] = item.find(
                    "a", class_="item-title").get_text(strip=True).split("-", 1)[0]
            except:
                sim['title'] = None
            try:
                # Extract brand by grabbing the first few words from the title (brand not listed separately)
                full_text = item.find(
                    "a", class_="item-title").get_text(strip=True)
                first_four_words = ' '.join(full_text.split()[:4])
                sim['brand'] = first_four_words
            except:
                sim['brand'] = None
            try:
                # Extract price
                sim['price'] = item.find(
                    "ul", class_="price").find("li", class_="price-current").get_text(strip=True)
            except:
                sim['price'] = None
            try:
                # Extract rating if available
                sim['rating'] = item.find(
                    "span", class_="item-rating-num").get_text(strip=True)
            except:
                sim['rating'] = None
            sim['description'] = None 
            all_products.append(sim)
    except:
        # pass
        print("product not found")
        
    # Save to SQLite 
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    cur.execute("""
    DROP TABLE IF EXISTS product
""")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS product (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, brand TEXT, price TEXT,
            rating TEXT, description TEXT
        )
    """)
    
    # Insert all product data into the table
    for p in all_products:
        cur.execute("""
            INSERT INTO product (title, brand, price, rating, description)
            VALUES (?, ?, ?, ?, ?)
        """, (p['title'], p['brand'], p['price'], p['rating'], p['description']))
    conn.commit()
    conn.close()
    return product

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    product_info = scrape_newegg(URL)
    print("Extracted Product Info:")
    for k, v in product_info.items():
        print(f"{k}: {v}")
        
    # Close browser when done
    try:
        driver.close()
    except:
        pass