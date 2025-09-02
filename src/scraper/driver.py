from selenium import webdriver



def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Enable headless mode
    options.add_argument('--window-size=1920x1080')  # Optional, set window size
    # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    # return driver
    return webdriver.Chrome(options=opts)

