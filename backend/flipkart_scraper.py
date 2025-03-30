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

class FlipkartScraper:
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
            search_url = f"https://www.flipkart.com/search?q={safe_keyword}"
            
            # Bypass login popup
            self.driver.get("https://www.flipkart.com")
            time.sleep(random.uniform(1, 3))
            
            try:
                # Try to close login popup if it exists
                close_button = self.driver.find_element(By.XPATH, "//button[@class='_2KpZ6l _2doB4z']")
                close_button.click()
                time.sleep(random.uniform(1, 2))
            except:
                # If no popup, continue
                pass
            
            # Navigate to search page
            self.driver.get(search_url)
            
            # Wait for products with longer timeout
            wait = WebDriverWait(self.driver, 20)
            wait.until(
                 EC.presence_of_all_elements_located(
        (By.XPATH, "//*[@class='slAVV4' or @class='tUxRFH']")
    )
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
        soup = BeautifulSoup(html, 'html.parser')
        products = []

    # Multiple possible product container classes based on category
        container_classes = ['slAVV4', 'tUxRFH', '_13oc-S']

    # Try to find products using multiple container classes
        product_containers = []
        for class_name in container_classes:
            product_containers = soup.find_all('div', class_=class_name)
            if product_containers:
                break  # Stop once we find products

        print("Found product containers:", product_containers)

        for container in product_containers:
            try:
                product = self._extract_product_info(container)
                if product and product.get('title'):
                    products.append(product)
            except Exception as e:
                self.logger.warning(f"Product extraction error: {e}")

        return products

    
    def _extract_product_info(self, container) -> Dict[str, str]:
    
        try:
            # Multiple class names for product title
            title_classes = ['wjcEIp', 'KzDlHZ', 'IRpwTa']
            title_element = None
            for class_name in title_classes:
                title_element = container.find('a', class_=class_name) or container.find('div',class_ = class_name)
                if title_element:
                    break  # Stop if found
            title = title_element.text.strip() if title_element else "N/A"
            #print("Mobile Phone",title)

            # Extract product URL
            #product_url = title_element.get('href', '') if title_element else container.find('a',class_="CGtC98").get('href', '') 



            product_url = None
            if title_element :
                product_url = title_element.get('href', '')
        
        # If first approach didn't work, try second approach
            if not product_url:
                alt_url_element = container.find('a', class_="CGtC98")
                if alt_url_element:
                    product_url = alt_url_element.get('href', '')



            full_product_url = f"https://www.flipkart.com{product_url}" if product_url else "No URL"
            #print(full_product_url)

            # Multiple class names for price
            price_classes = ['Nx9bqj', '_30jeq3', '_1_WHN1']
            price_element = None
            for class_name in price_classes:
                price_element = container.find('div', class_=class_name)
                if price_element:
                    break
            price = price_element.text.strip().replace('₹', '').replace(',', '') if price_element else "N/A"
           # print(price)

            # Multiple class names for discount
            discount_classes = ['UkUFwK', '_3Ay6Sb']
            discount_element = None
            for class_name in discount_classes:
                discount_element = container.find('div', class_=class_name)
                if discount_element:
                    break
            discount = discount_element.text.strip() if discount_element else "N/A"
            #print(discount)

            # Multiple class names for image
            image_classes = ['DByuf4', '_396cs4', '_2r_T1I']
            image_element = None
            for class_name in image_classes:
                image_element = container.find('img', class_=class_name)
                if image_element:
                    break
            image_url = image_element.get('src', 'No Image') if image_element else "No Image"
            #print(image_url)

            return {
                "title": title,
                "price": price,
                "discount": discount,
                "image_url": image_url,
                "product_url": full_product_url
            }

        except Exception as e:
            self.logger.warning(f"Product info extraction error: {e}")
            return {}


# FastAPI setup remains the same
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)