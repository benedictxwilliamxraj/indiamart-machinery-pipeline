import time
import pandas as pd
import sys
import os 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from .parsers import parse_one_card


def scroll_to_load_all_cards(driver, card_selector, idle_rounds=3, step_sleep=0.8, max_rounds=40):
    WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))
    # ensure at least one card (if present)
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, card_selector)))
    except Exception:
        return 0

    last_count, idle, rounds = 0, 0, 0
    while rounds < max_rounds and idle < idle_rounds:
        rounds += 1
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(step_sleep)
        count = len(driver.find_elements(By.CSS_SELECTOR, card_selector))
        if count == last_count:
            idle += 1
        else:
            idle, last_count = 0, count
    return last_count

def _try_click_read_more(driver, timeout=5):
    XPATHS = [
        # Exact text matches
        "//*[self::a or self::button or self::span][normalize-space()='READ MORE']",
        "//*[self::a or self::button or self::span][normalize-space()='Read More']",
        "//*[self::a or self::button or self::span][normalize-space()='Read more']",
        "//*[self::a or self::button or self::span][normalize-space()='View more']",
        "//*[self::a or self::button or self::span][normalize-space()='VIEW MORE']",
        # Common class/name patterns
        "//*[contains(@class,'read') and contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'more')]",
        "//*[contains(@onclick,'read') and contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'more')]",
    ]
    clicked = False
    for xp in XPATHS:
        try:
            els = driver.find_elements(By.XPATH, xp)
            for el in els:
                if not el.is_displayed():
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                    time.sleep(0.15)
                driver.execute_script("arguments[0].click();", el)  # JS click avoids overlay issues
                clicked = True
                # give content time to expand
                time.sleep(0.3)
        except Exception:
            continue
    if clicked:
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(@class,'pdp_desc') or contains(@id,'desc') or contains(@class,'desc')]"))
            )
        except Exception:
            pass
    return clicked


def scrape_page_data(driver):
    
    card_selector = "div.new_mobile_card"  # narrowed to avoid duplicate wrapping
    scroll_to_load_all_cards(driver, card_selector)

    cards = driver.find_elements(By.CSS_SELECTOR, card_selector)
    seen_local = set()
    rows = []

    for card in cards:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", card)
        time.sleep(0.05)
        entry = parse_one_card(card)
        if not entry:
            continue
        key = entry["product_id"]
        if key in seen_local:
            continue
        seen_local.add(key)

        rows.append({
            "product_id": entry["product_id"],
            "product_url": entry["product_url"],
            "source_url": driver.current_url
        })

    return pd.DataFrame(rows)