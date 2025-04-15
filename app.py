# Add these imports at the top
import httpx
from bs4 import BeautifulSoup
from fastapi import BackgroundTasks

# Add this endpoint to your FastAPI app
@app.post("/api/scrape")
async def scrape_prices(query: str, stores: List[str], background_tasks: BackgroundTasks):
    """Initiate scraping from multiple stores"""
    background_tasks.add_task(run_scrapers, query, stores)
    return {"status": "scraping_started", "query": query, "stores": stores}

async def run_scrapers(query: str, stores: List[str]):
    """Background task to run all scrapers"""
    results = []
    
    if 'startech' in stores:
        try:
            startech_results = await scrape_startech(query)
            results.extend(startech_results)
        except Exception as e:
            print(f"StarTech scraping failed: {e}")
    
    if 'ryans' in stores:
        try:
            ryans_results = await scrape_ryans(query)
            results.extend(ryans_results)
        except Exception as e:
            print(f"Ryans scraping failed: {e}")
    
    # Add more store scrapers as needed
    
    # Process and save results
    processed = process_scraped_data(results)
    # Here you would typically save to database
    print(f"Scraping complete. Found {len(processed)} items.")

async def scrape_startech(query: str):
    """Scrape StarTech.com.bd"""
    async with httpx.AsyncClient() as client:
        url = f"https://www.startech.com.bd/search?search={query}"
        response = await client.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        products = []
        for item in soup.select('.product-thumb'):
            name = item.select_one('.product-name').get_text(strip=True)
            price_text = item.select_one('.price span').get_text(strip=True)
            price = float(price_text.replace('৳', '').replace(',', ''))
            
            # Check for original price
            original_price = None
            if item.select_one('.price-old'):
                original_text = item.select_one('.price-old').get_text(strip=True)
                original_price = float(original_text.replace('৳', '').replace(',', ''))
            
            products.append({
                "store": "StarTech",
                "name": name,
                "price": price,
                "original_price": original_price,
                "url": item.select_one('a').get('href'),
                "image": item.select_one('img').get('src'),
                "in_stock": "Out of Stock" not in item.text
            })
        
        return products

async def scrape_ryans(query: str):
    """Scrape RyansComputers.com"""
    async with httpx.AsyncClient() as client:
        url = f"https://www.ryanscomputers.com/search?q={query}"
        response = await client.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        products = []
        for item in soup.select('.single-product'):
            name = item.select_one('.product-title').get_text(strip=True)
            price_text = item.select_one('.price span').get_text(strip=True)
            price = float(price_text.replace('৳', '').replace(',', ''))
            
            # Ryans specific parsing
            original_price = None
            if item.select_one('.regular-price'):
                original_text = item.select_one('.regular-price').get_text(strip=True)
                original_price = float(original_text.replace('৳', '').replace(',', ''))
            
            products.append({
                "store": "Ryans",
                "name": name,
                "price": price,
                "original_price": original_price,
                "url": item.select_one('a').get('href'),
                "image": item.select_one('img').get('data-original'),
                "in_stock": not item.select_one('.out-of-stock')
            })
        
        return products

def process_scraped_data(raw_data):
    """Normalize scraped data into our standard format"""
    processed = []
    
    for item in raw_data:
        # Generate a unique ID based on product name and store
        product_id = hash(f"{item['name']}-{item['store']}")
        
        processed.append({
            "id": product_id,
            "name": item["name"],
            "image": item.get("image", ""),
            "rating": 4.0,  # Default rating
            "reviews": 0,   # Default review count
            "specs": extract_specs(item["name"]),
            "prices": [{
                "store": item["store"],
                "amount": item["price"],
                "original_amount": item.get("original_price"),
                "discount": calculate_discount(item.get("original_price"), item["price"]),
                "url": item["url"],
                "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "is_lowest": False,
                "in_stock": item.get("in_stock", True)
            }]
        })
    
    return processed
