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
        
        # Set page load strategy to ensure complete page loading
        options.page_load_strategy = 'normal'
        
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
                
                # Set page load timeout
                self.driver.set_page_load_timeout(30)
                
                return True
            except Exception as e:
                self.logger.warning(f"WebDriver setup attempt {attempt+1} failed: {e}")
                time.sleep(random.uniform(1, 3))
        
        self.logger.error("Failed to setup WebDriver after multiple attempts")
        return False
    
    def _simulate_human_browsing(self):
        """Simulate more human-like browsing behavior with multiple scroll pauses"""
        try:
            # Get total height of page
            total_height = self.driver.execute_script("""
                return Math.max(
                    document.body.scrollHeight, 
                    document.body.offsetHeight, 
                    document.documentElement.clientHeight, 
                    document.documentElement.scrollHeight, 
                    document.documentElement.offsetHeight
                );
            """)
            
            # Scroll in multiple steps with pauses
            window_height = self.driver.execute_script("return window.innerHeight")
            scrolls_needed = max(3, total_height // window_height)
            
            for i in range(scrolls_needed):
                # Calculate scroll position
                scroll_top = (i / scrolls_needed) * total_height
                
                # Scroll to position
                self.driver.execute_script(f"window.scrollTo(0, {scroll_top});")
                
                # Longer pause after each scroll to allow images to load
                time.sleep(random.uniform(0.5, 3))
            
            # Scroll back to top
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # Scroll all the way down once more
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            # Scroll halfway up
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(1)
        except Exception as e:
            self.logger.warning(f"Browsing simulation error: {e}")
    
    def _wait_for_images_to_load(self):
        """Enhanced method to ensure all images are fully loaded"""
        try:
            # Initial delay to allow page resources to be requested
            time.sleep(5)
            
            # First check all product items are present
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'product-item'))
            )
            
            # Explicitly wait for image elements inside product items
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.product-item img'))
            )
            
            # Execute JavaScript to check if images are loaded
            # More sophisticated check that counts loaded vs total images
            script = """
            const images = Array.from(document.querySelectorAll('.product-item img'));
            const totalImages = images.length;
            const loadedImages = images.filter(img => img.complete && img.naturalHeight !== 0).length;
            return {
                total: totalImages,
                loaded: loadedImages,
                allLoaded: totalImages === loadedImages && totalImages > 0
            };
            """
            
            # Try multiple times with longer delays
            max_attempts = 1
            for attempt in range(max_attempts):
                img_status = self.driver.execute_script(script)
                
                self.logger.info(f"Image status: {img_status['loaded']}/{img_status['total']} loaded")
                
                if img_status['allLoaded']:
                    self.logger.info(f"All {img_status['total']} images are loaded")
                    break
                else:
                    self.logger.info(f"Waiting for images to load (attempt {attempt+1}/{max_attempts})")
                    # Increase wait time for each attempt
                    time.sleep(3 + attempt)
            
            # Force any lazy-loaded images to load by scrolling again
            self._simulate_human_browsing()
            
            # Final extended delay to ensure everything is loaded
            time.sleep(5)
            
        except Exception as e:
            self.logger.warning(f"Error while waiting for images: {e}")
            # Fallback longer delay in case of error
            time.sleep(10)
    
    def search_products(self, keyword: str, max_products: int = 10) -> List[Dict[str, Any]]:
        """Enhanced product search with improved detection avoidance"""
        if not self._setup_driver():
            return [{"error": "Failed to setup WebDriver"}]
        
        try:
            # Carefully construct search URL
            safe_keyword = '%20'.join(keyword.split())  # Ensure proper encoding
            search_url = f"https://www.croma.com/searchB?q={safe_keyword}%3Arelevance&text={safe_keyword}"
            print(search_url)
            
            # Navigate with delays
            self.driver.get("https://www.croma.com")
            time.sleep(random.uniform(2, 4))
            
            # Actual search navigation
            self.driver.get(search_url)
            
            # Wait for page to load completely
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'product-item'))
            )
            
            # Initial delay after page load
            time.sleep(5)
            
            # Simulate human-like browsing
            self._simulate_human_browsing()
            
            # Wait specifically for images to load with enhanced method
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