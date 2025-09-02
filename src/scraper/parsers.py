from selenium.webdriver.common.by import By
from urllib.parse import urljoin
import re

def parse_one_card(card):
    BASE = "https://export.indiamart.com/"
    
    # find the anchor that points to products/?id=...
    a = None
    for xp in [
        ".//a[starts-with(@href,'products/?id=')]",          
        ".//a[contains(@href,'/product/')]",                 
    ]:
        els = card.find_elements(By.XPATH, xp)
        if els:
            a = els[0]; break
    if not a:
        return None

    href = a.get_attribute("href")
    if not href:
        return None
    product_url = urljoin(BASE, href)

    m = re.search(r"(?:[?&])id=(\d+)", product_url) or re.search(r"/product/(\d+)", product_url)
    product_id = m.group(1) if m else None
    if not product_id:
        return None

    return {"product_id": product_id, "product_url": product_url}