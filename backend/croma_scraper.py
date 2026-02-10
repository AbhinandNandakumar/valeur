import re
import time
import random
import logging
from typing import List, Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

class CromaScraper:
    def __init__(self, log_level=logging.INFO):
        # Setup logging
        logging.basicConfig(
            level=log_level, 
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Comprehensive Chrome options
        self.chrome_options = self._configure_chrome_options()
        
        self.driver = None
    
    def _configure_chrome_options(self) -> Options:
        """Configure Chrome options for improved stealth"""
        options = Options()
        
        # Stealth and anti-detection configurations
        stealth_args = [
            "--headless=new",
            "--disable-blink-features=AutomationControlled",
            "--disable-extensions",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-browser-side-navigation"
        ]
        
        for arg in stealth_args:
            options.add_argument(arg)
        
        # User Agent Randomization
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
        ]
        options.add_argument(f"user-agent={random.choice(user_agents)}")
        
        # Experimental options to reduce detection
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Use eager strategy - don't wait for images/subresources
        options.page_load_strategy = 'eager'
        
        return options
    
    def _setup_driver(self) -> bool:
        """Robust WebDriver setup with error handling"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Use system Chromium if available (Docker/Render), else webdriver_manager
                import os
                chromedriver_path = os.environ.get('CHROMEDRIVER_PATH')
                chrome_bin = os.environ.get('CHROME_BIN')
                if chrome_bin:
                    self.chrome_options.binary_location = chrome_bin
                if chromedriver_path:
                    service = Service(chromedriver_path)
                else:
                    service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
                
                # Additional stealth technique
                self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                    "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                    """
                })
                
                # Set page load timeout
                self.driver.set_page_load_timeout(30)
                
                return True
            except Exception as e:
                self.logger.warning(f"WebDriver setup attempt {attempt+1} failed: {e}")
                time.sleep(random.uniform(1, 3))
        
        self.logger.error("Failed to setup WebDriver after multiple attempts")
        return False
    
    def _simulate_human_browsing(self):
        """Quick scroll to trigger lazy-loaded content"""
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)
        except Exception as e:
            self.logger.warning(f"Browsing simulation error: {e}")
    
    def _wait_for_images_to_load(self):
        """Wait for product items to be present"""
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'product-item'))
            )
            time.sleep(2)
        except Exception as e:
            self.logger.warning(f"Error while waiting for products: {e}")
            time.sleep(3)
    
    def search_products(self, keyword: str, max_products: int = 15) -> List[Dict[str, Any]]:
        """Enhanced product search with improved detection avoidance"""
        if not self._setup_driver():
            return [{"error": "Failed to setup WebDriver"}]
        
        try:
            # Carefully construct search URL
            safe_keyword = '%20'.join(keyword.split())  # Ensure proper encoding
            search_url = f"https://www.croma.com/searchB?q={safe_keyword}%3Arelevance&text={safe_keyword}"
            self.logger.info(f"Searching: {search_url}")

            # Go directly to search URL (skip homepage to save time)
            self.driver.get(search_url)

            # Wait for products to appear
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'product-item'))
            )

            # Quick scroll to load lazy content
            self._simulate_human_browsing()

            # Wait for product data
            self._wait_for_images_to_load()
            
            # Extract page source after ensuring images are loaded
            page_source = self.driver.page_source
            
            # Close driver
            self.driver.quit()
            
            # Parse and return results
            products = self._parse_search_results(page_source)
            return products[:max_products]
        
        except Exception as e:
            self.logger.error(f"Comprehensive search error: {e}")
            if self.driver:
                self.driver.quit()
            return [{"error": f"Search failed: {str(e)}"}]
    
    def _parse_search_results(self, html: str) -> List[Dict[str, str]]:
        """Robust parsing with comprehensive error handling"""
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        product_containers = soup.find_all('li', {'class': 'product-item'})
        
        for container in product_containers:
            try:
                product = self._extract_product_info(container)
                print(product)
                if product and all(product.values()):
                    products.append(product)
            except Exception as e:
                self.logger.warning(f"Product extraction error: {e}")
        
        return products
    
    def _extract_product_info(self, container) -> Dict[str, str]:
        """Comprehensive product info extraction with robust fallbacks"""
        try:
            def safe_extract(finder, default="N/A"):
                """Safely extract text or attribute"""
                try:
                    return finder().text.strip() if finder() else default
                except Exception:
                    return default
            
            # Extract product URL
            product_url_element = container.find('h3', {'class': 'product-title'})
            if product_url_element:
               product_link = product_url_element.find('a')  # Find the <a> inside <h3>
               product_url = product_link.get('href', '') if product_link else ''
            else:
               product_url = ''
            print("hy",product_url)
            full_product_url = f"https://www.croma.com{product_url}" if product_url else "No URL"
            
            # More robust product ID extraction
            product_id_match = re.search(r'/p/(\d+)', product_url or '')
            product_id = product_id_match.group(1) if product_id_match else ""
            print(safe_extract(lambda: container.find('h3', {'class': 'product-title'})))
            title = safe_extract(lambda: container.find('h3', {'class': 'product-title'}))
            price = safe_extract(
                    lambda: container.find('span', {'class': 'amount'}),
                    default=""
                ).replace('₹', '').replace(',', '')
            
            original_price = safe_extract(
                    lambda: container.find('span', {'class': 'strike-through'}),
                    default=""
                ).replace('₹', '').replace(',', '') 
            
            discount = safe_extract(
                    lambda: container.find('span', {'class': 'discount'}),
                    default=""
                )
            
            # Enhanced image extraction with multiple fallback options
            image_element = container.select_one('div img')
            image_url = "No Image"
            
            if image_element:
                # Try getting src attribute
                image_url = image_element.get('src', '')
                
                # If src is empty, try data-src (for lazy loading)
                if not image_url or image_url.endswith('placeholder.png'):
                    image_url = image_element.get('data-src', '')
                
                # If data-src is empty, try srcset
                if not image_url:
                    srcset = image_element.get('srcset', '')
                    if srcset:
                        # Extract the first URL from srcset
                        srcset_parts = srcset.split(',')
                        if srcset_parts:
                            first_url = srcset_parts[0].strip().split(' ')[0]
                            if first_url:
                                image_url = first_url
            
            if not image_url or image_url == "No Image":
                # Final fallback: check for any image in the container
                any_img = container.find('img')
                if any_img and any_img.get('src'):
                    image_url = any_img.get('src')
            
            return {
                "title": title,
                "price": price,
                "discount": discount,
                "image_url": image_url,
                "product_url": full_product_url
             }
        
        except Exception as e:
            self.logger.warning(f"Detailed product info extraction error: {e}")
            return {}

# FastAPI setup
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)