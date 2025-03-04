import random
import time
from fastapi import FastAPI
from amazon_scraper import AmazonScraper
from snapdeal_scraper import SnapdealScraper
from croma_scraper import CromaScraper
from fastapi.middleware.cors import CORSMiddleware

# Set your ScraperAPI key here
SCRAPERAPI_KEY = "1e1fe6ea3984685acdfb3658408e08ed"

app = FastAPI()
amazon_scraper = AmazonScraper(api_key=SCRAPERAPI_KEY)  # Pass API key
snapdeal_scraper = SnapdealScraper()
croma_scraper = CromaScraper()

# Allow React frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search")
async def search_products(query: str):
    print("hello")
    """
    Fetch product details from Amazon, Snapdeal, and Chroma.
    
    Args:
        query (str): The product search keyword.
        
    Returns:
        dict: Contains Amazon, Snapdeal, and Chroma product lists.
    """
    if not query:
        return {"error": "Missing search query"}
    
    # Add delay to avoid rate limiting
    time.sleep(random.uniform(2, 5))  # Increased delay for Amazon

    # Fetch results from Snapdeal and Chroma
    amazon_products = amazon_scraper.search_products(query)  # Uses ScraperAPI
    #print(amazon_products)
    snapdeal_products = snapdeal_scraper.search_products(query)
    croma_products = croma_scraper.search_products(query)
    #print("Croma Products:", croma_products)  # Debugging print
    return {
        "amazon_products": amazon_products,
        "snapdeal_products": snapdeal_products,
        "croma_products": croma_products
    }

if __name__ == "__main__":  
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
