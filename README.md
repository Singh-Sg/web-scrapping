# Newegg Product Scraper

This Python script scrapes product details and similar product suggestions from a specific [Newegg](https://www.newegg.com/) product page using **Selenium**, **undetected-chromedriver**, and **BeautifulSoup**. The extracted data is saved into a local **SQLite** database.

---

# Features

- Extracts product details such as:
  - Title
  - Brand
  - Price
  - Rating
  - Description
- Bypasses bot detection with `undetected-chromedriver`.
- Handles CAPTCHAs with retry logic.
- Saves data into an `SQLite` database: `newegg_data.db`.

---

# Create Create a Virtual Environment
```bash
    python -m venv venv

-  python: This invokes the Python interpreter.
-  -m venv: This tells Python to run the venv module as a script.
-  venv: This is the name of the directory where your virtual environment will be created. You can choose a different name if desired.

# Requirements

All dependencies are listed in the `requirements.txt` file. To install them, run:

```bash
pip install -r requirements.txt



