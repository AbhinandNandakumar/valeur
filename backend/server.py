from fastapi import FastAPI
from amazon_scraper import AmazonScraper
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
scraper = AmazonScraper()

# Allow React frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search")
def search_amazon(query: str):
    if not query:
        return {"error": "Missing search query"}
    
    products = scraper.search_products(query)
    return {"products": products}

