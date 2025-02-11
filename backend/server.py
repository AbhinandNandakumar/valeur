import random
import time
from fastapi import FastAPI
from amazon_scraper import AmazonScraper
from snapdeal_scraper import SnapdealScraper
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
amazon_scraper = AmazonScraper()
snapdeal_scraper = SnapdealScraper()

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
    """
    Fetch product details from both Amazon and Snapdeal.
    
    Args:
        query (str): The product search keyword.
        
    Returns:
        dict: Contains Amazon and Snapdeal product lists.
    """
    if not query:
        return {"error": "Missing search query"}
    
    # Add delay to avoid rate limiting
    time.sleep(random.uniform(1, 3))
    
    # Fetch results from both Amazon and Snapdeal
    amazon_products = amazon_scraper.search_products(query)
    print(amazon_products)
    snapdeal_products = snapdeal_scraper.search_products(query)

    return {
        "amazon_products": amazon_products,
        "snapdeal_products": snapdeal_products
    }

if __name__ == "__main__":  
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
