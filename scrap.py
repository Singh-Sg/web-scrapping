import time
import logging as logger
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.common.exceptions import WebDriverException
from db_connection import DatabaseManager
from product import ProductExtractor

class NeweggScraper:
    def __init__(self, url: str, db_manager: DatabaseManager):
        self.url = url
        self.driver = self._init_driver()
        self.db = db_manager
        self.extractor = ProductExtractor()

    def _init_driver(self):
        try:
            options = uc.ChromeOptions()
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            driver = uc.Chrome(version_main=138, options=options)
            logger.info("Chrome driver initialized.")
            return driver
        except WebDriverException as e:
            logger.critical(f"Failed to initialize Chrome driver: {e}")
            raise

    def load_page(self, retries=3):
        for attempt in range(retries):
            try:
                self.driver.get(self.url)
                time.sleep(5)
                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                title = soup.find("title").text if soup.find("title") else ""

                if title == "Are you a human?":
                    logger.warning(f"CAPTCHA detected (attempt {attempt + 1}), retrying...")
                    time.sleep(5)
                    continue

                time.sleep(10)
                logger.info("Page loaded successfully.")
                return soup
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(3)
        raise Exception("Failed to load page after retries.")
    
    def extract_similar_products(self, soup):
        products = []
        try:
            # Find the section containing similar products
            sim_section = soup.find("div", class_="product-similar-box")
            if not sim_section:
                logger.warning("Similar products section not found.")
                return products

            # Look for individual product slides
            items = sim_section.find_all("div", class_="swiper-slide")

            for item in items:
                sim = {}

                # Title
                title_tag = item.find("a", class_="item-title")
                if title_tag:
                    title_text = title_tag.get_text(strip=True)
                    sim['title'] = title_text.split("-", 1)[0]
                    sim['brand'] = ' '.join(title_text.split()[:4])
                else:
                    sim['title'] = sim['brand'] = None

                # Price
                price_tag = item.find("li", class_="price-current")
                sim['price'] = price_tag.get_text(strip=True) if price_tag else None

                # Rating
                rating_tag = item.find("span", class_="item-rating-num")
                sim['rating'] = rating_tag.get_text(strip=True) if rating_tag else None

                sim['description'] = None
                products.append(sim)

        except Exception as e:
            logger.error(f"Error while extracting similar products: {e}")

        return products


    def run(self):
        try:
            logger.info("Scraping started.")
            soup = self.load_page()
            # main_product = self.extract_main_product(soup)
            main_product =  self.extractor.extract_main_product(soup)
            similar_products = self.extract_similar_products(soup)
            all_products = [main_product] + similar_products

            self.db.create_table()
            self.db.insert_products(all_products)

            logger.info("Main product extracted:")
            for k, v in main_product.items():
                logger.info(f"{k}: {v}")

        except Exception as e:
            logger.critical(f"Scraping failed: {e}")
        finally:
            logger.info("Browser closed.")
            self.driver.quit()
