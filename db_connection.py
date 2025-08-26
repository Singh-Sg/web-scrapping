import sqlite3
import logging


# ------------------ Logging Setup ------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("newegg_scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
# ---------------------------------------------------


# ---------- Database Manager ----------
class DatabaseManager:
    def __init__(self, db_file="newegg_data.db"):
        self.db_file = db_file
        self.conn = None
        self.cursor = None
        self._connect()

    def _connect(self):
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.cursor = self.conn.cursor()
            logger.info("Connected to SQLite database.")
        except sqlite3.Error as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def create_table(self):
        try:
            self.cursor.execute("DROP TABLE IF EXISTS product")
            self.cursor.execute("""
                CREATE TABLE product (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT, brand TEXT, price TEXT,
                    rating TEXT, description TEXT
                )
            """)
            logger.info("Database table created.")
        except sqlite3.Error as e:
            logger.error(f"Failed to create table: {e}")
            raise

    def insert_products(self, products):
        try:
            for p in products:
                self.cursor.execute("""
                    INSERT INTO product (title, brand, price, rating, description)
                    VALUES (?, ?, ?, ?, ?)
                """, (p['title'], p['brand'], p['price'], p['rating'], p['description']))
            self.conn.commit()
            logger.info(f"{len(products)} products inserted into database.")
        except sqlite3.Error as e:
            logger.error(f"Error inserting products: {e}")
            raise

    def close(self):
        try:
            if self.conn:
                self.conn.close()
                logger.info("Database connection closed.")
        except sqlite3.Error as e:
            logger.warning(f"Error closing database: {e}")
