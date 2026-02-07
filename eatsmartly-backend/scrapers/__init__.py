"""
Web scrapers for Indian e-commerce platforms
"""
from .amazon_scraper import search_amazon_india, get_amazon_product_details
from .bigbasket_scraper import search_bigbasket, get_bigbasket_product_details

__all__ = [
    'search_amazon_india',
    'get_amazon_product_details',
    'search_bigbasket',
    'get_bigbasket_product_details'
]
