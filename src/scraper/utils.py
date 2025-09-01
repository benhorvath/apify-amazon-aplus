"""
Contains two kinds of functions:

1. Wrappers to BeautifulSoup's `find` and `find_all` functions, wrapped with a
   decorator to handle cases where those elements don't exist in the HTML
2. Functions that require a bit of extra effort to extract the relevant data,
   like regex.
"""

from functools import wraps
import re
from urllib.parse import urlparse, urlunparse

def strip_url_args(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

def safe_extract(default=None):
    """
    Decorator to wrap extractors so they never raise.
    Returns `default` if an exception occurs. Can then use:
        
    @safe_extract(default=None)
    def my_function(x):
        ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return default
        return wrapper
    return decorator
    
def safe_return(default=None):
    """Decorator: return `default` if first arg is None."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(parent, *args, **kwargs):
            if parent is None:
                return default
            return fn(parent, *args, **kwargs)
        return wrapper
    return decorator
    
def nws(text: str) -> str:
    """ Normalize white space: Replace all contiguous white space of any
    length with a single space."""
    return re.sub(r'\s+', ' ', text).strip()
    
@safe_return(default=None)
def safe_find(parent, *args, attr=None, text=False, default=None, **kwargs):
    """
    A general safe wrapper around BeautifulSoup .find()

    - If text=True, return stripped text
    - If attr is provided, return that attribute
    - Otherwise return the element itself

    The `default` argument is returned if the element or attribute is missing.
    """
    el = parent.find(*args, **kwargs)
    if not el:
        return default

    if text:
        return nws(el.get_text())
    if attr:
        return el.get(attr, default)
    return el

@safe_return(default=[])
def safe_find_all(parent, *args, **kwargs):
    """Safe wrapper around .find_all(), returning [] if nothing is found."""
    return parent.find_all(*args, **kwargs)    

@safe_return(default=(None, None))
def extract_ships_and_seller(parent):
    text = safe_find(parent, attrs={'data-feature-name': 'shipFromSoldByAbbreviated'}, text=True)
    pattern = r"Ships from:\s*(.*?)\s+Sold by:\s*(.*)"
    match = re.search(pattern, text)
    ships_from = nws(match.group(1))
    sold_by = nws(match.group(2))
    return ships_from, sold_by
    
@safe_return(default=[None]*5)
def extract_review_percentages(soup):
    soup = safe_find(soup, "ul", id="histogramTable")
    meters = [int(m['aria-valuenow']) for m in soup.find_all('div', class_='a-meter')]
    if meters == [0]*5:
        meters = [None]*5
    return meters
    
def extract_numeric(text: str, kind: type = int, allow_k: bool = False):
    """
    Extracts a number from text. 
    - kind: int or float for conversion
    - allow_k: interpret 'K' as *1000
    """
    if not text:
        return None
    
    match = re.search(r'([\d,.]+)(K)?', text)
    if not match:
        return None
    
    num = match.group(1).replace(',', '')
    val = float(num) if '.' in num or kind is float else int(num)
    
    if allow_k and match.group(2):  # handle K suffix
        val *= 1000
    return kind(val) if kind is int else val
    
def extract_price_json(soup) -> dict:
    """
    Extracts price components from a JSON-like string.
    Returns a dict with numeric values converted appropriately.
    """
    PRICE_REGEX = re.compile(
        r'"displayPrice":"(?P<displayPrice>[^"]+)"'
        r'.*?"priceAmount":(?P<priceAmount>[\d.]+)'
        r'.*?"currencySymbol":"(?P<currencySymbol>[^"]+)"'
        r'.*?"integerValue":"(?P<integerValue>\d+)"'
        r'.*?"decimalSeparator":"(?P<decimalSeparator>[^"]+)"'
        r'.*?"fractionalValue":"(?P<fractionalValue>\d+)"',
        re.DOTALL
    )
    
    price_data = safe_find(soup, attrs={'data-feature-name': 'twisterPlusWWDesktop'}, text=True)
    
    match = PRICE_REGEX.search(price_data)
    if not match:
        return {}
    price_dict = match.groupdict()

    # Convert numeric values
    numeric_vals = [('priceAmount', float),
                    ('integerValue', int),
                    ('fractionalValue', int)]
    for key, cast in numeric_vals:
        price_dict[key] = cast(price_dict[key])

    return price_dict