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
    
    # Basic product information
    product_title = safe_find(soup, "h1", id="title", text=True)
    product_asin = safe_find(soup, "input", id="ASIN", attr="value")
    is_merchant_exclusive = safe_find(soup, "input", id="isMerchantExclusive",
                                      attr="value")
    merchant_id = safe_find(soup, "input", id="merchantID", attr="value")
    store_id = safe_find(soup, "input", id="storeID", attr="value") 
    ships_from, sold_by = extract_ships_and_seller(soup)
    
    breadcrumbs_list = safe_find(soup, 
                                 attrs={"data-feature-name": "desktop-breadcrumbs"}, text=True).split('›')

    byline_element = safe_find(soup, attrs={'data-feature-name': 'bylineInfo'})
    byline_text = nws(byline_element.text.strip().replace('Visit the ', ''))
    byline_link = strip_url_args(safe_find(byline_element, 'a', attr='href'))

    # Thumbnails and variations
    thumbnails = safe_find(soup, attrs={'aria-label': 'Image thumbnails'})
    count_thumbnails = len(safe_find_all(thumbnails, "li", class_="imageThumbnail"))
    
    variations = safe_find(soup, "div", 
                           attrs={"data-totalvariationcount": True}, attr="data-totalvariationcount", default='0')
    variations_count = extract_numeric(variations)
    
    # Price
    price_dict = extract_price_json(soup)

    # Social proof
    ac_badge = bool(safe_find(soup, "div", class_="mvt-ac-badge-wrapper",
                              default=None))

    social_proof = safe_find(soup,
                             attrs={'data-feature-name': 'socialProofingAsinFaceout'}, text=True, default=False)
    social_proof_integer = extract_numeric(social_proof, allow_k=True)
    
    # Documents
    product_documents_div = safe_find(soup, "div",
                                      id="productDocuments_feature_div")
    product_documents_links = safe_find_all(product_documents_div, "a",
                                            default=[])
    product_documents_count = len(product_documents_links)
    product_documents_titles = [doc.text.strip() for doc in product_documents_links]
    
    # Reviews
    avg_review_stars_str = safe_find(soup, "span",
                                     attrs={"data-hook": "rating-out-of-text"}, text=True, default='')
    avg_review_stars = extract_numeric(avg_review_stars_str, kind=float)

    total_review_count_str = safe_find(soup, "span",
                                       attrs={"data-hook": "total-review-count"}, text=True, default='')
    total_review_count = extract_numeric(total_review_count_str, kind=int)

    # TODO: FIX
    # ratings_percentages = extract_review_percentages(soup)
    
    # A+ modules and features
    whats_in_the_box_exists = bool(safe_find(soup, "div",
                                             id="whatsInTheBoxDeck", default=None))
    
    product_details_exists = bool(safe_find(soup, "div",
                                            id="productDescription_feature_div",default=None))

    aplus_div = safe_find(soup, "div", id="aplus", default=None)
    aplus_div_exists = bool(aplus_div)
    aplus_modules_count = len(safe_find_all(soup, "div", class_="aplus-module"))
    aplus_v2_exists = bool(safe_find(soup, "div", class_="aplus-v2"))
    aplus_premium_exists = bool(safe_find(soup, "div", class_='premium-aplus'))

    aplus_feature_widgets_count = len(safe_find_all(aplus_div, "div", 
                                                    class_='celwidget'))


    aplus_brand_story_hero_exists = bool(safe_find(soup, "div",
                            class_="apm-brand-story-carousel-hero-container",
                            default=None))

    aplus_brand_story_div = safe_find(soup, "div", id="aplusBrandStory_feature_div")
    aplus_brand_story_div_count = len(safe_find_all(aplus_brand_story_div,
                                                    "div"))

    aplus_carousel_exists = bool(safe_find(aplus_div, "ol",
                                           class_="a-carousel"))
    aplus_slides_count = len(safe_find_all(aplus_div, "li",
                                           class_="a-carousel-card"))

    aplus_bg_img_exists = bool(safe_find(aplus_div, "div",
                                    class_='apm-brand-story-background-image'))

    premium_bg_wrapper_exists = bool(safe_find(soup, "div",
                                        class_='premium-background-wrapper'))

    aplus_mantle_pages_count = len(safe_find_all(soup, "li",
                                                 class_="aplus-pagination-dot"))

    vse_player_exists = bool(safe_find(soup, "div", class_='vse-player'))
    
    # Simple validation to mark scrape status
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
        'is_merchant_exclusive': True if is_merchant_exclusive == "1" else False,
        'merchant_id': merchant_id,
        'store_id': None if store_id == '' else store_id,
        'byline_text': byline_text,
        'byline_link': byline_link,
        'ships_from': ships_from,
        'sold_by': sold_by,
        'breadcrumbs': breadcrumbs_list,
        'thumbnails_count': count_thumbnails,
        'variations_count': variations_count,
        'price_data': price_dict,
        # 'availability': availability,
        'amazons_choice_badge': ac_badge,
        'social_proof': social_proof,
        'social_proof_integer': 0 if social_proof_integer is None else social_proof_integer,
        'whats_in_the_box_exists': whats_in_the_box_exists,
        'documents_count': product_documents_count,
        'documents_titles': product_documents_titles,
        'avg_review_stars': avg_review_stars,
        'total_review_count': 0 if not total_review_count else total_review_count,
        # 'ratings_histogram': {
        #     5: ratings_percentages[0],
        #     4: ratings_percentages[1],
        #     3: ratings_percentages[2],
        #     2: ratings_percentages[3],
        #     1: ratings_percentages[4]   
        # },
        'product_details_exists': product_details_exists,
        'aplus_modules_count': aplus_modules_count,
        'aplus_v2_exists': aplus_v2_exists,
        'aplus_feature_widgets_count': aplus_feature_widgets_count,
        'aplus_brand_story_div_count': aplus_brand_story_div_count,
        'aplus_brand_story_hero_exists': aplus_brand_story_hero_exists,
        'aplus_carousel_slides_count': aplus_slides_count,
        'aplus_bg_img_exists': aplus_bg_img_exists,
        'aplus_premium_exists': aplus_premium_exists,
        'premium_bg_wrapper_exists': premium_bg_wrapper_exists,
        'aplus_mantle_pages_count': aplus_mantle_pages_count,
        'vse_player_exists': vse_player_exists
    }
    
    return export
