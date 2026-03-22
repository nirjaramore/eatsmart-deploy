"""
Web scrapers for Indian e-commerce platforms
"""
from .amazon_scraper import search_amazon_india, get_amazon_product_details
from .bigbasket_scraper import search_bigbasket, get_bigbasket_product_details
from .openfoodfacts_scraper import (
    search_open_food_facts,
    get_open_food_facts_product_details,
)

__all__ = [
    'search_amazon_india',
    'get_amazon_product_details',
    'search_bigbasket',
    'get_bigbasket_product_details',
    'search_open_food_facts',
    'get_open_food_facts_product_details',
]
