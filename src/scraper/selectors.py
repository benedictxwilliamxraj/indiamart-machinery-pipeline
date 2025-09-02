from selenium.webdriver.common.by import By

def extract_top_row_links(driver, top_row_selector="a.clr4.sgst-lst"):
    elems = driver.find_elements(By.CSS_SELECTOR, top_row_selector)
    hrefs = []
    for e in elems:
        href = e.get_attribute("href")
        if href:
            hrefs.append(href)
    return hrefs