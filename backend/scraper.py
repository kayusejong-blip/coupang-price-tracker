import json
import re
import requests
import urllib3
import os
import logging
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bright Data Settings
BRIGHTDATA_USERNAME = os.getenv("BRIGHTDATA_USERNAME")
BRIGHTDATA_PASSWORD = os.getenv("BRIGHTDATA_PASSWORD")
BRIGHTDATA_HOST = "brd.superproxy.io"
BRIGHTDATA_PORT = 33335

PROXY_URL = f"http://{BRIGHTDATA_USERNAME}:{BRIGHTDATA_PASSWORD}@{BRIGHTDATA_HOST}:{BRIGHTDATA_PORT}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}

def scrape_coupang(url: str):
    """
    Scrapes Coupang product page using Bright Data Web Unlocker.
    Parses JSON-LD for robustness.
    """
    logger.info(f"Scraping with Bright Data: {url}")
    
    proxies = {
        "http": PROXY_URL,
        "https": PROXY_URL,
    }

    try:
        current_proxies = proxies if BRIGHTDATA_USERNAME and BRIGHTDATA_PASSWORD else None
        
        resp = requests.get(
            url,
            headers=HEADERS,
            proxies=current_proxies,
            timeout=60,
            verify=False
        )
        resp.raise_for_status()
        
        if "Access Denied" in resp.text:
            return {"success": False, "error": "Access Denied (Bright Data configuration needed)"}

        soup = BeautifulSoup(resp.text, "html.parser")
        
        product_data = {}
        
        # 1. Try JSON-LD parsing (Most robust)
        json_ld_scripts = soup.find_all("script", type="application/ld+json")
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                if data.get("@type") == "Product":
                    product_data['name'] = data.get("name")
                    product_data['thumbnail'] = data.get("image", [None])[0] if isinstance(data.get("image"), list) else data.get("image")
                    
                    offers = data.get("offers")
                    if isinstance(offers, dict):
                        product_data['price'] = float(offers.get("price", 0))
                    elif isinstance(offers, list) and len(offers) > 0:
                        product_data['price'] = float(offers[0].get("price", 0))
                    
                    if product_data.get('name'):
                        logger.info("Parsed data from JSON-LD")
                        break
            except Exception as je:
                logger.debug(f"JSON-LD parse skip: {je}")

        # 2. Fallback to CSS Selectors
        if not product_data.get('name'):
            name_el = soup.select_one(".prod-buy-header__title, h2.prod-buy-header__title, .product-title")
            if name_el:
                product_data['name'] = name_el.get_text(strip=True)
            
            if not product_data.get('price'):
                price_selectors = [".total-price strong", ".unit-price", ".origin-price", ".card-total-price", ".final-price-amount"]
                for selector in price_selectors:
                    price_el = soup.select_one(selector)
                    if price_el:
                        price_text = price_el.get_text(strip=True)
                        if price_text:
                            product_data['price'] = float(re.sub(r'[^\d]', '', price_text))
                            break
            
            if not product_data.get('thumbnail'):
                thumb_selectors = [".prod-image__detail", "#repImage", ".target-image", "meta[property='og:image']"]
                for selector in thumb_selectors:
                    thumb_el = soup.select_one(selector)
                    if thumb_el:
                        if thumb_el.name == 'meta':
                            product_data['thumbnail'] = thumb_el.get("content")
                        else:
                            product_data['thumbnail'] = thumb_el.get("src") or thumb_el.get("data-src")
                        if product_data['thumbnail']: break

        if not product_data.get('name'):
            # Save for debugging if still failing
            if not os.path.exists("data"): os.makedirs("data")
            with open("data/last_failed_page.html", "w", encoding="utf-8") as f:
                f.write(resp.text)
            return {"success": False, "error": "상품 정보를 찾을 수 없습니다."}

        # Cleanup thumbnail URL
        if product_data.get('thumbnail') and product_data['thumbnail'].startswith("//"):
            product_data['thumbnail'] = "https:" + product_data['thumbnail']

        logger.info(f"Success: {product_data.get('name')} - {product_data.get('price')}")
        return {
            "name": product_data.get('name'),
            "price": product_data.get('price', 0),
            "thumbnail": product_data.get('thumbnail', ""),
            "success": True
        }

    except Exception as e:
        logger.error(f"Scrape failed for {url}: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Test
    test_url = "https://www.coupang.com/vp/products/7791843896"
    print(scrape_coupang(test_url))
