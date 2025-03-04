import requests
from bs4 import BeautifulSoup
import random
import time
from urllib.parse import quote  # Importing quote for URL encoding

class CromaScraper:
    def __init__(self, api_key):
        self.api_key = api_key
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]

    def _get_random_user_agent(self):
        return random.choice(self.user_agents)

    def _get_scraperapi_url(self, croma_url):
        """Build ScraperAPI URL"""
        return f"https://api.scraperapi.com/?api_key={self.api_key}&url={croma_url}&keep_headers=true"

    def search_products(self, keyword, retries=3):
        """Search Croma for products using ScraperAPI"""
        if not keyword or not keyword.strip():
            print("Error: Empty search keyword provided.")
            return {"error": "Search keyword is required"}

        keyword = keyword.strip()
        encoded_keyword = quote(keyword)  # Properly encode spaces and special characters
        base_url = f"https://www.croma.com/searchB?q={encoded_keyword}:relevance"  # Added :relevance
        print(f"Generated Search URL: {base_url}")

        scraperapi_url = self._get_scraperapi_url(base_url)
        headers = {"User-Agent": self._get_random_user_agent()}

        for attempt in range(retries):
            try:
                response = requests.get(scraperapi_url, headers=headers, timeout=20)
                print(f"Attempt {attempt + 1}: Status Code {response.status_code}")

                if response.status_code == 200:
                    return self._parse_search_results(response.text)
                else:
                    print(f"Attempt {attempt + 1}: Failed with status {response.status_code}")
            except requests.exceptions.Timeout:
                print(f"Attempt {attempt + 1}: ScraperAPI timeout error. Retrying...")
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1}: Error: {e}")

        return {"error": "Failed to fetch data from Croma after multiple attempts"}

    def _parse_search_results(self, html):
        """Parse the HTML response and extract product details"""
        soup = BeautifulSoup(html, 'html.parser')

        # Save HTML to a file for debugging
        with open("croma_response.html", "w", encoding="utf-8") as file:
            file.write(html)
        print("HTML saved as 'croma_response.html'")

        # Print a sample of the raw HTML response (first 1000 characters)
       # print("HTML Response Sample:\n", html[:1000])

        products = []

        # Find all product containers
        product_containers = soup.find_all('div', {'class': 'cp-product'})
        print(f"Found {len(product_containers)} products")

        for container in product_containers:
            product = self._extract_product_info(container)
            if product:
                products.append(product)

        return products

    def _extract_product_info(self, container):
        """Extract product information from a product container"""
        try:
            # Extract title
            title_element = container.find('h3', {'class': 'product-title'})
            title = title_element.text.strip() if title_element else "No Title"

            # Extract price
            price_element = container.find('span', {'class': 'amount'})
            price = price_element.text.strip().replace('₹', '').replace(',', '') if price_element else "N/A"

            # Extract original price (if available)
            original_price_element = container.find('span', {'class': 'mrp-price'})
            original_price = original_price_element.text.strip().replace('₹', '').replace(',', '') if original_price_element else price

            # Extract discount percentage
            discount_element = container.find('span', {'class': 'discount'})
            discount = discount_element.text.strip() if discount_element else "N/A"

            # Extract rating
            rating_element = container.find('div', {'class': 'ratings'})
            rating = rating_element.text.strip() if rating_element else "N/A"

            # Extract image URL
            image_element = container.find('img', {'class': 'product-img'})
            image_url = image_element.get('data-src') if image_element else "No Image"

            # Extract product URL
            link_element = container.find('a', {'class': 'product-link'})
            product_url = "https://www.croma.com" + link_element.get('href') if link_element else "No URL"

            return {
                "title": title,
                "price": price,
                "original_price": original_price,
                "discount": discount,
                "rating": rating,
                "image_url": image_url,
                "product_url": product_url
            }

        except Exception as e:
            print(f"Error extracting product info: {str(e)}")
            return None

