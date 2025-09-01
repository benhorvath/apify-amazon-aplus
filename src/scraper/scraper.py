"""
Contains the logic to extract relevant data from the HTML.
"""

from datetime import datetime

from src.scraper.utils import *

def scrape_data(url, soup):
    """ Main function to scrape relevant data from the page.
    """
    url_cleaned = strip_url_args(url)
    
    SUCCESS_FLAG = True
    
    product_title = safe_find(soup, "h1", id="title", text=True)
    product_asin = safe_find(soup, "input", id="ASIN", attr="value")
    price_dict = extract_price_json(soup)
    
    SUCCESS_FLAG = False if safe_find(soup, "div", id="dp-container") is None else SUCCESS_FLAG
    SUCCESS_FLAG = False if product_title is None else SUCCESS_FLAG
    SUCCESS_FLAG = False if product_asin is None else SUCCESS_FLAG
    SUCCESS_FLAG = False if price_dict['priceAmount'] < 0.01 else SUCCESS_FLAG
    
    export = export = {
        'timestamp': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        'success': SUCCESS_FLAG,
        'url': url_cleaned,
        'title': product_title,
        'asin': product_asin,
        'price_data': price_dict
    }
    
    return export
