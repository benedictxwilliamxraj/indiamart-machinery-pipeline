import pandas as pd
import re
from selenium.webdriver.common.by import By
from urllib.parse import urlparse, parse_qs,urljoin

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from .page_scrape import _try_click_read_more

def scrape_product_details(driver):
    """
    Scrapes a single product page (expanded) using your PDP locators.
    """
    url = driver.current_url
    BASE = "https://export.indiamart.com/"

    # product_id from URL
    pid = None
    try:
        qs = parse_qs(urlparse(url).query)
        if "id" in qs and qs["id"]:
            pid = qs["id"][0]
        else:
            m = re.search(r"/product/(\d+)", url)
            if m: pid = m.group(1)
    except:
        pass

    out = {"product_id": pid, "product_url": url}

    # Product name
    try:
        out["product_name"] = driver.find_element(By.XPATH, "//h1[@id='prd_name']").text.strip()
    except:
        out["product_name"] = None

    # Image
    try:
        img = driver.find_element(By.XPATH, "//div[@id='img-zoom-container']//img[@id='prdimgdiv']")
        out["image_url"] = img.get_attribute("src") or img.get_attribute("data-zoom")
    except:
        out["image_url"] = None

    # Price
    try:
        price_txt = driver.find_element(By.XPATH, "//span[@id='prc_id']//span[contains(@class,'prc_conv')]").text.strip()
        m = re.search(r"(?:₹|Rs\.?|INR|\$)?\s*([\d,]+(?:\.\d+)?)", price_txt)
        out["price_raw"] = price_txt
        out["price"] = int(float(m.group(1).replace(",", ""))) if m else None
    except:
        out["price_raw"] = None
        out["price"] = None

    # 🔹 Expand READ MORE before scraping specs/description
    _try_click_read_more(driver)

    # Specs table
    specs = {}
    try:
        rows = driver.find_elements(By.XPATH, "//table[@id='desc_sku_tbl']//tr")
        for r in rows:
            tds = r.find_elements(By.XPATH, "./td")
            if len(tds) >= 2:
                k = (tds[0].text or "").strip()
                v = (tds[1].text or "").strip()
                if k and v:
                    specs[k] = v
    except:
        pass
    out["specs"] = specs

    # Description (expanded)
    try:
        desc = driver.find_element(By.XPATH, "//div[contains(@class,'pdp_desc')]").get_attribute("textContent").strip()
        out["description"] = re.sub(r"\s+\n", "\n", desc)
    except:
        out["description"] = None

    # Company details
    try:
        croot = driver.find_element(By.XPATH, "//div[@id='companyDetails']")
    except:
        croot = None

    if croot:
        # Name + URL
        try:
            comp_a = croot.find_element(By.XPATH, ".//a[contains(@href,'/company/')]")
            out["company_url"] = urljoin(BASE, comp_a.get_attribute("href"))
            comp_h2 = comp_a.find_element(By.TAG_NAME, "h2")
            out["company_name"] = comp_h2.text.strip()
            
        except:
            try:
                out["company_name"] = croot.find_element(By.XPATH, ".//h2").text.strip()
            except:
                out["company_name"] = None
            out["company_url"] = None

        # Location
        try:
            out["company_location"] = croot.find_element(By.XPATH, ".//span[contains(@class,'lne2txt')]").text.strip()
        except:
            out["company_location"] = None

        # Rating + count
        try:
            rating_block = croot.find_element(By.XPATH, ".//div[contains(@class,'sllrTph1')]").text
            rm = re.search(r"(\d+(?:\.\d+)?)\s*/\s*5", rating_block)
            cm = re.search(r"\((\d+)\)", rating_block)
            out["rating"] = float(rm.group(1)) if rm else None
            out["rating_count"] = int(cm.group(1)) if cm else None
        except:
            out["rating"] = None
            out["rating_count"] = None

        # GST & IEC
        try:
            out["gst_number"] = croot.find_element(By.XPATH, ".//span[contains(@class,'gstP')]/following-sibling::span").text.strip()
        except:
            out["gst_number"] = None
        try:
            out["iec_number"] = croot.find_element(By.XPATH, ".//span[normalize-space(text())='IEC']/following-sibling::span").text.strip()
        except:
            out["iec_number"] = None

        # Exports To list
        try:
            exp_txt = croot.find_element(By.XPATH, ".//span[b[normalize-space()='Exports To:']]").text
            exp_txt = re.sub(r"^\s*Exports To:\s*", "", exp_txt, flags=re.I)
            out["exports_to"] = [c.strip() for c in re.split(r"[;,/]", exp_txt) if c.strip()]
        except:
            out["exports_to"] = []

        # Badges
        badges, seen = [], set()
        try:
            for el in croot.find_elements(By.XPATH, ".//div[contains(@class,'tsVssVeM')]//span"):
                t = (el.text or "").strip()
                if t and any(k in t.lower() for k in ["verified", "trustseal", "manufacturer"]):
                    if t not in seen: badges.append(t); seen.add(t)
        except:
            pass
        out["badges"] = badges
    else:
        out.update({
            "company_name": None, "company_url": None,
            "company_location": None, "rating": None, "rating_count": None,
            "gst_number": None, "iec_number": None, "exports_to": [], "badges": []
        })

    return out