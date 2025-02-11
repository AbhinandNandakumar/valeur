from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import random
import time
import re

class SnapdealScraper:
    def __init__(self):  # <-- Fixed __init__ method
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
        
    def _get_random_user_agent(self):
        return random.choice(self.user_agents)
    
    def search_products(self, keyword):
        """Search Snapdeal for products based on keyword"""
        products = []
        base_url = f"https://www.snapdeal.com/search?keyword={keyword.replace(' ', '%20')}"
        
        url = f"{base_url}&sort=rlvncy"
        print(f"Scraping URL: {url}")
        
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
                return self._parse_search_results(response.text)
            else:
                return {"error": f"Failed to fetch page. Status code: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def _parse_search_results(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Find all product containers
        product_containers = soup.find_all('div', {'class': 'product-tuple-listing'})
        
        for container in product_containers:
            product = self._extract_product_info(container)
            if product:
                products.append(product)
                
        return products
    
    def _extract_product_info(self, container):
        try:
            # Extract product ID
            product_id = container.get('data-product-id', '')

            # Extract title
            title_element = container.find('p', {'class': 'product-title'})
            title = title_element.text.strip() if title_element else "No Title"

            # Extract price
            price_element = container.find('span', {'class': 'product-price'})
            price = price_element.text.strip().replace('₹', '').replace(',', '') if price_element else "N/A"

            # Extract original price if available
            original_price_element = container.find('span', {'class': 'product-desc-price'})
            original_price = original_price_element.text.strip().replace('₹', '').replace(',', '') if original_price_element else "N/A"

            # Extract discount percentage
            discount_element = container.find('div', {'class': 'product-discount'})
            discount = discount_element.text.strip() if discount_element else "N/A"

            # Extract rating
            rating_element = container.find('div', {'class': 'filled-stars'})
            rating = rating_element.get('style', '').replace('width:', '').replace('%', '') if rating_element else None
            if rating:
                rating = float(rating) / 20  # Convert percentage to 5-star scale

            # Extract image URL
            image_element = container.find('img', {'class': 'product-image'})
            image_url = image_element.get('src') if image_element else "No Image"

            # Extract product URL
            link_element = container.find('a', {'class': 'dp-widget-link'})
            product_url = 'https://www.snapdeal.com' + link_element.get('href') if link_element else "No URL"

            return {
                "product_id": product_id,
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


