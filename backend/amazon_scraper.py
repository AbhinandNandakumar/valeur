import requests
from bs4 import BeautifulSoup 
import random
import re
import time

class AmazonScraper:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
    
    def _get_random_user_agent(self):
        return random.choice(self.user_agents)

    def search_products(self, keyword):
        """Search Amazon.in for products based on keyword"""
        products = []
        base_url = f"https://www.amazon.in/s?k={keyword.replace(' ', '+')}"
        
        url = f"{base_url}&page=1"
        print(f"Scraping URL: {url}")

        headers = {"User-Agent": self._get_random_user_agent()}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return self._parse_search_results(response.text)
            else:
                return {"error": f"Failed to fetch page. Status code: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def _parse_search_results(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        for item in soup.select('div[data-asin]:not([data-asin=""])'):
            product = self._extract_product_info(item)
            if product:
                products.append(product)
                
        return products

    def _extract_product_info(self, item):
        if item.find('span', {'class': 's-sponsored-label-info-icon'}):
            return None

        asin = item.get('data-asin')
        if not asin:
            return None

        title_element = item.select_one('h2 a span')
        title = title_element.text.strip() if title_element else None

        price_element = item.select_one('.a-price .a-offscreen')
        price = price_element.text.strip() if price_element else None

        rating_element = item.select_one('i[class*="a-star"] span')
        rating = rating_element.text.strip() if rating_element else None

        return {"asin": asin, "title": title, "price": price, "rating": rating}

