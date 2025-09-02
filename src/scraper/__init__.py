__version__ = "0.1.0"

# Re-export public API
from .driver import init_driver
from .crawl import crawl
from .page_scrape import extract_top_row_links, scroll_to_load_all_cards, scrape_page_data
from .parsers import parse_one_card
from .product_scrape import scrape_product_details
from .similar_scrape import scrape_similar_products

__all__ = [
    "init_driver",
    "crawl",
    "extract_top_row_links",
    "scroll_to_load_all_cards",
    "scrape_page_data",
    "parse_one_card",
    "scrape_product_details",
    "scrape_similar_products",
]