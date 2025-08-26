from db_connection import DatabaseManager
from scrap import NeweggScraper

if __name__ == "__main__":
    URL = "https://www.newegg.com/amd-ryzen-7-9000-series-ryzen-7-9800x3d-granite-ridge-zen-5-socket-am5-desktop-cpu-processor/p/N82E16819113877"
    db = DatabaseManager("newegg_data.db")
    scraper = NeweggScraper(URL, db)
    scraper.run()
    db.close()
