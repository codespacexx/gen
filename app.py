from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import uuid
import re
import concurrent.futures
from urllib.parse import quote
import logging
import time

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# Configure all Bangladeshi stores
STORE_CONFIG = {
    'startech': {
        'url': 'https://www.startech.com.bd/product/search?search={query}',
        'selectors': {
            'container': '.p-item',
            'name': '.p-item-name',
            'price': '.price-new, .p-item-price',
            'image': '.p-item-img img',
            'link': '.p-item-img a',
            'logo': '.brand img'
        }
    },
    'techland': {
        'url': 'https://www.techlandbd.com/index.php?route=product/search&search={query}',
        'selectors': {
            'container': '.product-layout',
            'name': '.name',
            'price': '.price-new',
            'image': '.product-img img',
            'link': '.product-img',
            'logo': '#logo img'
        }
    },
    'ryans': {
        'url': 'https://www.ryans.com/search?q={query}',
        'selectors': {
            'container': '.category-single-product',
            'name': '.card-text a',
            'price': '.pr-text',
            'image': '.image-box img',
            'link': '.image-box a',
            'logo': '.main-logo img'
        }
    },
    'binary': {
        'url': 'https://www.binarylogic.com.bd/search/{query}',
        'selectors': {
            'container': '.single_product',
            'name': '.p-item-name',
            'price': '.current_price',
            'image': '.p-item-img img',
            'link': '.p-item-img a',
            'logo': '.homepage_two__log svg'
        }
    },
    'pchouse': {
        'url': 'https://www.pchouse.com.bd/index.php?route=product/search&search={query}',
        'selectors': {
            'container': '.product-layout',
            'name': '.name',
            'price': '.price-new',
            'image': '.product-img img',
            'link': '.product-img',
            'logo': '#logo img'
        }
    },
    'ultratech': {
        'url': 'https://www.ultratech.com.bd/index.php?route=product/search&search={query}',
        'selectors': {
            'container': '.product-layout',
            'name': '.name',
            'price': '.price-new',
            'image': '.product-img img',
            'link': '.product-img',
            'logo': '#logo img'
        }
    },
    'vibegaming': {
        'url': 'https://vibegaming.com.bd/?s={query}&post_type=product',
        'headers': {
            'X-Forwarded-For': '119.30.41.88'
        },
        'selectors': {
            'container': '.product',
            'name': '.product-name',
            'price': '.amount',
            'image': '.no-back-image img',
            'link': '.thumbnail-wrapper a',
            'logo': '.sticky-logo'
        }
    },
    'skyland': {
        'url': 'https://www.skyland.com.bd/index.php?route=product/search&search={query}',
        'selectors': {
            'container': '.product-layout',
            'name': '.name',
            'price': '.price-new',
            'image': '.product-img img',
            'link': '.product-img',
            'logo': '#logo img'
        }
    }
}

def clean_price(price_text):
    if not price_text:
        return 0
    try:
        return float(re.sub(r'[^\d.]', '', price_text))
    except:
        return 0

def get_lowest_price(prices):
    valid_prices = [p for p in prices if p > 0]
    return min(valid_prices) if valid_prices else 0

def scrape_store(store_name, query):
    config = STORE_CONFIG[store_name]
    try:
        url = config['url'].format(query=quote(query))
        headers = config.get('headers', {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        logo = soup.select_one(config['selectors']['logo'])
        logo_src = logo.get('src') or logo.get('data-src') if logo else None
        
        products = []
        for item in soup.select(config['selectors']['container']):
            try:
                name = item.select_one(config['selectors']['name']).get_text(strip=True)
                price_elements = item.select(config['selectors']['price'])
                prices = [clean_price(p.get_text()) for p in price_elements]
                price = get_lowest_price(prices)
                
                img = item.select_one(config['selectors']['image'])
                img_src = img.get('src') or img.get('data-src') if img else None
                
                link = item.select_one(config['selectors']['link'])
                link_href = link.get('href') if link else None
                
                products.append({
                    'id': str(uuid.uuid4()),
                    'name': name,
                    'price': f"৳{price:,.0f}" if price > 0 else "Out of Stock",
                    'img': img_src or 'Image not found',
                    'link': link_href or '#'
                })
            except Exception as e:
                logging.error(f"Error parsing {store_name} item: {e}")
                continue
                
        return {
            'name': store_name.capitalize(),
            'products': products,
            'logo': logo_src or f'/static/logos/{store_name}.png'
        }
        
    except Exception as e:
        logging.error(f"Error scraping {store_name}: {e}")
        return {
            'name': store_name.capitalize(),
            'products': [],
            'logo': f'/static/logos/{store_name}.png'
        }

@app.route('/scrape/<product>')
def scrape_all(product):
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(scrape_store, store, product): store 
            for store in STORE_CONFIG
        }
        results = []
        for future in concurrent.futures.as_completed(futures):
            store = futures[future]
            try:
                results.append(future.result())
            except Exception as e:
                logging.error(f"{store} scraping failed: {e}")
                results.append({
                    'name': store.capitalize(),
                    'products': [],
                    'logo': f'/static/logos/{store}.png'
                })
    
    logging.info(f"Scraping completed in {time.time() - start_time:.2f}s")
    return jsonify(results)

@app.route('/')
def home():
    return "Welcome to TechTrack Scraper API (Python/Flask Version)"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
