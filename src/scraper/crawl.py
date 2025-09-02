import re
import time
import pandas as pd
from driver import init_driver
from page_scrape import scrape_page_data
from product_scrape import scrape_product_details
from similar_scrape import scrape_similar_products
from collections import deque
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selectors import extract_top_row_links
from selenium.webdriver.support import expected_conditions as EC

def crawl(start_url, max_pages=10, max_products=20, top_row_selector="a.clr4.sgst-lst"):
    driver = init_driver()

    # Queues & visited
    page_queue = deque()       
    product_queue = deque()   # {"product_id": ..., "product_url": ...}
    visited_pages = set()
    visited_products = set()

    # Data buckets
    harvested_df = pd.DataFrame(columns=["product_id", "product_url", "source_url"])   # from listing/product pages
    product_details_df = pd.DataFrame()                                               # 🔹 new: detailed PDP rows

    try:

        driver.get(start_url)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        page_queue.append(start_url)

        for href in extract_top_row_links(driver, top_row_selector):
            if href not in visited_pages:
                page_queue.append(href)

        # ---- 1) Process listing/category pages ----
        pages_done = 0
        while page_queue and pages_done < max_pages and len(visited_products) < max_products:
            page_url = page_queue.popleft()
            if page_url in visited_pages:
                continue

            try:
                if pages_done > 10:
                    time.sleep(60)
                driver.get(page_url)
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            except Exception as e:
                print(f"[WARN] Failed to load page: {page_url} -> {e}")
                continue

            page_df = scrape_page_data(driver)  # harvest product_id/product_url pairs from this page
            if not page_df.empty:
                harvested_df = pd.concat([harvested_df, page_df], ignore_index=True)
                for _, row in page_df.iterrows():
                    pid, purl = row["product_id"], row["product_url"]
                    if pid and pid not in visited_products:
                        product_queue.append({"product_id": pid, "product_url": purl})

            visited_pages.add(page_url)
            pages_done += 1
            print(f"[PAGE] Visited: {page_url} | products queued: {len(product_queue)} | pages_done: {pages_done}")

        # ---- 2) Process product pages (PDPs) ----
        product_processed = 0
        while product_queue:
            item = product_queue.popleft()
            pid, purl = item["product_id"], item["product_url"]
            if not pid or pid in visited_products:
                continue

            try:
                if product_processed > 30:
                    time.sleep(60)
                driver.get(purl)
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            except Exception as e:
                print(f"[WARN] Failed to load product: {purl} -> {e}")
                continue

            # 🔹 scrape full product details here
            
            try:
                details = scrape_product_details(driver)   # uses your PDP XPaths
                if details:
                    # ensure product_id present; if missing, backfill from queue item
                    if not details.get("product_id"):
                        details["product_id"] = pid
                        details["product_url"] = purl
                    product_details_df = pd.concat([product_details_df, pd.DataFrame([details])], ignore_index=True)
            except Exception as e:
                print(f"[WARN] PDP parse failed for {purl}: {e}")

            # 🔹 also harvest any product cards shown on PDP (similar/more-from-seller)
            if len(visited_products) < max_products:
                prod_page_df = scrape_similar_products(driver)
                # print(prod_page_df)
                if not prod_page_df.empty:
                    harvested_df = pd.concat([harvested_df, prod_page_df], ignore_index=True)
                    for _, r in prod_page_df.iterrows():
                        pid, purl = r["product_id"], r["product_url"]
                        if pid and pid not in visited_products:
                            product_queue.append({"product_id": pid, "product_url": purl})

            visited_products.add(pid)
            print(f"[PROD] Visited product: {pid} | product_queue: {len(product_queue)} | visited_products: {len(visited_products)}")

    finally:
        driver.quit()

    # tidy up
    if not harvested_df.empty:
        harvested_df.drop_duplicates(subset=["product_id"], inplace=True, ignore_index=True)
    if not product_details_df.empty:
        product_details_df.drop_duplicates(subset=["product_id"], inplace=True, ignore_index=True)

    # return both: catalog of discovered products + detailed PDP rows
    return harvested_df, product_details_df, visited_products, visited_pages