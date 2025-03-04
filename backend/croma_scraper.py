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
        
        return options
    
    def _setup_driver(self) -> bool:
        """Robust WebDriver setup with error handling"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Use webdriver manager to handle driver installation
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
                
                return True
            except Exception as e:
                self.logger.warning(f"WebDriver setup attempt {attempt+1} failed: {e}")
                time.sleep(random.uniform(1, 3))
        
        self.logger.error("Failed to setup WebDriver after multiple attempts")
        return False
    
    def _simulate_human_browsing(self):
        """Simulate more human-like browsing behavior"""
        try:
            # Random scrolling
            scroll_script = """
            var totalHeight = Math.max(
                document.body.scrollHeight, 
                document.body.offsetHeight, 
                document.documentElement.clientHeight, 
                document.documentElement.scrollHeight, 
                document.documentElement.offsetHeight
            );
            
            var scrollSteps = Math.floor(Math.random() * 3) + 2;
            var currentPos = 0;
            
            for (var i = 0; i < scrollSteps; i++) {
                var scrollAmount = Math.random() * (totalHeight / scrollSteps);
                window.scrollTo(0, currentPos + scrollAmount);
                currentPos += scrollAmount;
            }
            """
            self.driver.execute_script(scroll_script)
            
            # Random small pauses
            time.sleep(random.uniform(0.5, 2))
        except Exception as e:
            self.logger.warning(f"Browsing simulation error: {e}")
    
    def search_products(self, keyword: str, max_products: int = 10) -> List[Dict[str, Any]]:
        """Enhanced product search with improved detection avoidance"""
        if not self._setup_driver():
            return [{"error": "Failed to setup WebDriver"}]
        
        try:
            # Carefully construct search URL
            safe_keyword = '+'.join(keyword.split())
            search_url = f"https://www.croma.com/search/?text={safe_keyword}&sort=relevance"
            
            # Navigate with delays
            self.driver.get("https://www.croma.com")
            time.sleep(random.uniform(1, 3))
            
            # Actual search navigation
            self.driver.get(search_url)
            
            # Wait for products with longer timeout
            wait = WebDriverWait(self.driver, 20)
            wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'product-item'))
            )
            
            # Simulate human-like browsing
            self._simulate_human_browsing()
            
            # Additional random wait
            time.sleep(random.uniform(2, 4))
            
            # Extract page source
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
            #print("hiii",product_url_element)
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
            
            image_url = container.find('img', {'class': 'product-image'}).get('src', 'No Image') if container.find('img', {'class': 'product-image'}) else "No Image"
            
            return {
               # "product_id": product_id,
                "title": title,
                 "price": price,
               # "original_price": original_price,
                "discount": discount ,
                #"image_url": image_url,
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
