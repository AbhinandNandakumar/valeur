import random
import time
from fastapi import FastAPI
from amazon_scraper import AmazonScraper
from flipkart_scraper import FlipkartScraper
from snapdeal_scraper import SnapdealScraper
from croma_scraper import CromaScraper
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Set your ScraperAPI key here
SCRAPERAPI_KEY = "1e1fe6ea3984685acdfb3658408e08ed"

app = FastAPI()
amazon_scraper = AmazonScraper(api_key=SCRAPERAPI_KEY)  # Pass API key
snapdeal_scraper = SnapdealScraper(api_key=SCRAPERAPI_KEY)
croma_scraper = CromaScraper()
flipkart_scraper = FlipkartScraper()

# Allow React frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search")
async def search_products(query: str, sites: str = "1,2,3,4"):
    """
    Fetch product details from selected e-commerce sites.
    
    Args:
        query (str): The product search keyword.
        sites (str): Comma-separated list of site identifiers to scrape.
                    1=Amazon, 2=Snapdeal, 3=Croma, 4=Flipkart
        
    Returns:
        dict: Contains product lists from the selected sites.
    """
    if not query:
        return {"error": "Missing search query"}
    
    # Parse selected sites
    site_list = sites.split(',')
    
    # Initialize results
    results = {}
    
    # Add delay to avoid rate limiting
    time.sleep(random.uniform(1, 3))
    
    # Fetch results from selected sites
    if "1" in site_list:  # Amazon
        results["amazon_products"] = amazon_scraper.search_products(query)
    else:
        results["amazon_products"] = []
        
    if "2" in site_list:  # Snapdeal
        results["snapdeal_products"] = snapdeal_scraper.search_products(query)
    else:
        results["snapdeal_products"] = []
        
    if "3" in site_list:  # Croma
        results["croma_products"] = croma_scraper.search_products(query)
    else:
        results["croma_products"] = []
        
    if "4" in site_list:  # Flipkart
        results["flipkart_products"] = flipkart_scraper.search_products(query)
    else:
        results["flipkart_products"] = []
    
    return results

@app.get("/keep-alive")
def keep_alive():
    return JSONResponse(content={"status": "Server is alive"})

if __name__ == "__main__":  
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)