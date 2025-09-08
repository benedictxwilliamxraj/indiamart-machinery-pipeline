import argparse
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from scraper import crawl


DEFAULT_START_URL = "https://export.indiamart.com/search.php?ss=industrial+machinery"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-url", default=DEFAULT_START_URL)
    parser.add_argument("--max-pages", type=int, default=10)
    parser.add_argument("--max-products", type=int, default=100)
    args = parser.parse_args()

    harvested_df, product_details_df, visited_products, visited_pages = crawl(
        start_url=args.start_url,
        max_pages=args.max_pages,
        max_products=args.max_products,
    )

    print(f"Visited pages: {len(visited_pages)} | products: {len(visited_products)}")
    if not harvested_df.empty:
        print(harvested_df.head(3).to_string(index=False))
        harvested_df.to_csv('/Users/benedictraj/Documents/MyProjects/IndiaMartDataVis/src/storage/harvested_df.csv')
        product_details_df.to_csv('/Users/benedictraj/Documents/MyProjects/IndiaMartDataVis/src/storage/products.csv')

    else:
        print("No rows harvested.")

if __name__ == "__main__":
    main()