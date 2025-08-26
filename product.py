class ProductExtractor:
    def extract_main_product(self, soup):
        return {
            'title': self.extract_title(soup),
            'brand': self.extract_brand(soup),
            'price': self.extract_price(soup),
            'rating': self.extract_rating(soup),
            'description': self.extract_description(soup),
        }

    def extract_title(self, soup):
        title_elem = soup.find("h1", class_="product-title")
        if title_elem:
            return title_elem.get_text(strip=True).split("-", 1)[0]
        return None

    def extract_brand(self, soup):
        brand_container = soup.find("div", class_="product-view-brand has-brand-store")
        if brand_container:
            brand_link = brand_container.find("a")
            if brand_link:
                return brand_link.get("title")
        return None

    def extract_price(self, soup):
        price_container = soup.find("div", class_="row-side")
        if price_container:
            price_elem = price_container.find("div", class_="price-current")
            if price_elem:
                return price_elem.get_text(strip=True)
        return None

    def extract_rating(self, soup):
        rating_elem = soup.find("span", class_="item-rating-num")
        if rating_elem:
            rating_text = rating_elem.get_text(" ", strip=True).split(" ", 1)
            if rating_text:
                return rating_text[0]
        return None

    def extract_description(self, soup):
        description_elem = soup.find("div", class_="product-bullets")
        if description_elem:
            return description_elem.get_text(" ", strip=True)
        return None
