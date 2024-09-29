from fastapi import FastAPI, Depends, HTTPException
from .scraper import Scraper
from .cache import Cache
from .auth import verify_token
from .models import save_to_db, load_from_db

app = FastAPI()

cache = Cache()

@app.get("/scrape")
async def scrape_products(pages: int = 1, proxy: str = None, token: str = Depends(verify_token)):
    scraper = Scraper(pages=pages, proxy=proxy)
    scrapedProducts = await scraper.scrape()

    products = []
    for product in scrapedProducts:
        cached_product = cache.get(product['title'])
        if not cached_product or cached_product['price'] != product['price']:
            save_to_db(product)
            cache.set(product['title'], product)
            products.append(product)

    return {"message": f"{len(products)} products scraped and updated."}
