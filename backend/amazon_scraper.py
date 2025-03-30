import requests
from bs4 import BeautifulSoup
import random
import time

class AmazonScraper:
    def __init__(self, api_key):
        self.api_key = api_key
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
    
    def _get_random_user_agent(self):
        """Returns a random user agent."""
        return random.choice(self.user_agents)

    def _get_scraperapi_url(self, amazon_url):
        """
        Build ScraperAPI URL with key, rendering, and session rotation.
        """
        return f"https://api.scraperapi.com/?api_key={self.api_key}&url={amazon_url}&render=true"

    def search_products(self, keyword, retries=3):
        """Search Amazon.in for products based on keyword, using ScraperAPI"""
        base_url = f"https://www.amazon.in/s?k={keyword.replace(' ', '+')}&page=1"
        scraperapi_url = self._get_scraperapi_url(base_url)

        headers = {"User-Agent": self._get_random_user_agent()}
        
        for attempt in range(retries):
            try:
                response = requests.get(scraperapi_url, headers=headers, timeout=20)  # Increased timeout
                if response.status_code == 200:
                    return self._parse_search_results(response.text)
                else:
                    print(f"Attempt {attempt + 1}: Failed with status {response.status_code}")
            except requests.exceptions.Timeout:
                print(f"Attempt {attempt + 1}: ScraperAPI timeout error. Retrying...")
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1}: Error: {e}")
        
        return {"error": "Failed to fetch data from Amazon after multiple attempts"}

    def _parse_search_results(self, html):
        """Parse the search results and limit to 15 products."""
        soup = BeautifulSoup(html, 'html.parser')
        products = []

        # Find all product containers
        for item in soup.select('div[data-asin]:not([data-asin=""])'):
            product = self._extract_product_info(item)
            if product and all(product.values()):
                products.append(product)
            
            # Stop scraping after 15 products
            if len(products) >= 15:
                break

        return products

    def _extract_product_info(self, item):
        """Extract individual product information."""
        # Skip sponsored ads
        if item.find('span', {'class': 's-sponsored-label-info-icon'}):
            return None

        asin = item.get('data-asin')
        if not asin:
            return None
        
        image_element = item.find('img', {'class': 's-image'})
        image_url = image_element.get('src', 'No Image') if image_element else "No Image"

        title_element = item.select_one('h2 span')
        title = title_element.text.strip() if title_element else None

        price_element = item.select_one('.a-price .a-offscreen')
        price = price_element.text.strip() if price_element else None

        rating_element = item.select_one('i[class*="a-star"] span')
        rating = rating_element.text.strip() if rating_element else None

        return {
            "asin": asin,
            "title": title,
            "price": price,
            "rating": rating,
            "image_url": image_url
        }

# Example Usage
if __name__ == "__main__":
    api_key = "YOUR_SCRAPERAPI_KEY"  # Replace with your ScraperAPI key
    scraper = AmazonScraper(api_key)
    results = scraper.search_products("laptop")
    
    # Print only 15 products
    for i, product in enumerate(results, 1):
        print(f"{i}. {product['title']} - ₹{product['price']} | Rating: {product['rating']} | {product['image_url']}")
