import pandas as pd
import time
import re
from urllib.parse import urlparse, urljoin
from selenium.webdriver.common.by import By

def scrape_similar_products(driver):
    """
    Scrape product_id → product_url pairs from the PDP's #similarProducts section.
    Returns DataFrame[product_id, product_url, source_url]
    """
    src_url = driver.current_url
    origin = f"{urlparse(src_url).scheme}://{urlparse(src_url).netloc}"

    def _abs(href: str) -> str:
        return urljoin(origin, href)

    rows, seen = [], set()

    # 1) locate the similar section
    try:
        root = driver.find_element(By.ID, "similarProducts")
    except:
        return pd.DataFrame(rows)

    # 2) click any "View more" triggers inside this section (ids like viewmoreRel-10)
    try:
        for vm in root.find_elements(By.XPATH, ".//*[starts-with(@id,'viewmoreRel-')]"):
            if vm.is_displayed():
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", vm)
                driver.execute_script("arguments[0].click();", vm)
                time.sleep(0.2)
    except:
        pass

    # 3) force-reveal hidden card rows (class 'dn') just in case
    try:
        driver.execute_script("""
            [...document.querySelectorAll('#similarProducts [id^="prd-card-"]')]
                .forEach(el => el.classList.remove('dn'));
        """)
        time.sleep(0.05)
    except:
        pass

    # 4) collect anchors that point to product pages
    anchors = root.find_elements(By.XPATH, ".//a[starts-with(@href,'/products/?id=')]")
    for a in anchors:
        href = a.get_attribute("href") or ""
        if not href:
            continue
        href = _abs(href)
        m = re.search(r"(?:[?&])id=(\d+)", href)
        if not m:
            continue
        pid = m.group(1)
        if pid in seen:
            continue
        seen.add(pid)
        rows.append({"product_id": pid, "product_url": href, "source_url": src_url})

    return pd.DataFrame(rows)
