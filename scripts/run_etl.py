import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
import pandas as pd
from etl.io import read_raw, write_processed
from etl.clean import clean_catalog, clean_details
from etl.transform import build_products, build_companies

if __name__ == "__main__":
    catalog, details = read_raw()
    catalog_c = clean_catalog(catalog)
    details_c = clean_details(details)

    # products = build_products(catalog_c, details_c)
    products = details_c
    companies = build_companies(products)

    write_processed(products, companies)
    print(f"Processed rows — products: {len(products):,} | companies: {len(companies):,}")
