import requests
from bs4 import BeautifulSoup
import random
import re

class FlipkartScraper:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]

    def _get_random_user_agent(self):
        return random.choice(self.user_agents)

    def search_product(self, keyword):
        base_url = f"https://www.flipkart.com/search?q={keyword.replace(' ', '+')}"
        headers = {"User-Agent": self._get_random_user_agent()}

        try:
            response = requests.get(base_url, headers=headers)
            if response.status_code == 200:
                return self._parse_search_results(response.text)
            else:
                return {"error": f"Failed to fetch page. Status code: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def _parse_search_results(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        products = []

        for item in soup.select('._1AtVbE'):
            product = self._extract_product_info(item)
            if product:
                products.append(product)

        if products:
            return min(products, key=lambda x: x["price"])  # Return the lowest price product
        return {"error": "No products found"}

    def _extract_product_info(self, item):
        title_element = item.select_one('._4rR01T') or item.select_one('.s1Q9rs')
        title = title_element.text.strip() if title_element else None

        price_element = item.select_one('._30jeq3')
        if price_element:
            price_text = price_element.text.strip().replace('₹', '').replace(',', '')
            try:
                price = float(re.sub(r'[^\d.]', '', price_text))
            except ValueError:
                price = None
        else:
            price = None

        return {"title": title, "price": price} if price else None
