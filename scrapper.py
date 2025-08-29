from collections import deque
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Enable headless mode
    options.add_argument('--window-size=1920x1080')  # Optional, set window size
    
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    return driver







if __name__ == "__main__":
    results, visited = crawl(START_URL)
    print(f"Visited {len(visited)} pages")
    print("Sample:", results[:2])