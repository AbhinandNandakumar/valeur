from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SnapdealScraper:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
        # Initialize Selenium options.
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        
    def _get_random_user_agent(self):
        return random.choice(self.user_agents)
    
    def search_products(self, keyword, use_selenium=True, wait_time=5, limit=15):
        """
        Search Snapdeal for products based on keyword
        
        Parameters:
        - keyword: Search term
        - use_selenium: Whether to use Selenium for dynamic content loading
        - wait_time: Time to wait for page to load completely (in seconds)
        - limit: Maximum number of products to return
        """
        base_url = f"https://www.snapdeal.com/search?keyword={keyword.replace(' ', '%20')}"
        url = f"{base_url}&sort=rlvncy"
        print(f"Scraping URL: {url}")
        
        if use_selenium:
            return self._search_with_selenium(url, wait_time, limit)
        else:
            return self._search_with_requests(url, limit)
    
    def _search_with_requests(self, url, limit):
        """Use regular requests for scraping (may miss dynamically loaded content)"""
        headers = {
            "User-Agent": self._get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                # Add a short delay to emulate page loading
                time.sleep(3)
                return self._parse_search_results(response.text, limit)
            else:
                return {"error": f"Failed to fetch page. Status code: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def _search_with_selenium(self, url, wait_time, limit):
        """Use Selenium to wait for dynamic content to load"""
        try:
            # Set up the driver with random user agent
            self.chrome_options.add_argument(f"user-agent={self._get_random_user_agent()}")
            driver = webdriver.Chrome(options=self.chrome_options)
            
            # Navigate to the URL
            driver.get(url)
            
            # Wait for the page to load
            print(f"Waiting {wait_time} seconds for page to load completely...")
            time.sleep(wait_time)
            
            # Scroll down to ensure all lazy-loaded images are loaded
            self._scroll_page(driver)
            
            # Wait for product images to be loaded
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "img.product-image"))
            )
            
            # Get page source after dynamic content has loaded
            html = driver.page_source
            driver.quit()
            
            return self._parse_search_results(html, limit)
        except Exception as e:
            print(f"Error with Selenium: {str(e)}")
            if 'driver' in locals():
                driver.quit()
            return {"error": str(e)}
    
    def _scroll_page(self, driver):
        """Scroll down to load just enough products"""
        # Scroll just once to load the initial set of products
        driver.execute_script("window.scrollTo(0, 1000);")
        time.sleep(2)
    
    def _parse_search_results(self, html, limit):
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Find all product containers
        product_containers = soup.find_all('div', {'class': 'product-tuple-listing'}, limit=limit)
        
        for container in product_containers:
            product = self._extract_product_info(container)
            if product:
                products.append(product)
                if len(products) >= limit:
                    break
                
        return products
    
    def _extract_product_info(self, container):
        try:
            # Extract only the essential information
            # Extract title
            title_element = container.find('p', {'class': 'product-title'})
            title = title_element.text.strip() if title_element else "No Title"

            # Extract price
            price_element = container.find('span', {'class': 'product-price'})
            price = price_element.text.strip().replace('₹', '').replace(',', '') if price_element else "N/A"

            # Extract image URL
            image_element = container.find('img', {'class': 'product-image'})
            image_url = image_element.get('src') if image_element else None
            
            # If image src is not available, try data-src attribute (for lazy-loaded images)
            if not image_url or image_url.endswith('default-product-image.jpg'):
                image_url = image_element.get('data-src') if image_element else "No Image"

            # Extract product URL
            link_element = container.find('a', {'class': 'dp-widget-link'})
            product_url = 'https://www.snapdeal.com' + link_element.get('href') if link_element else "No URL"

            rating_element = container.find('div', {'class': 'filled-stars'})
            rating = rating_element.get('style', '').replace('width:', '').replace('%', '') if rating_element else None
            if rating:
                rating = float(rating) / 20

            return {
                "title": title,
                "price": price,
                "image_url": image_url,
                "product_url": product_url,
                "rating":rating
            }
            
        except Exception as e:
            print(f"Error extracting product info: {str(e)}")
            return None