from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time
import requests

def wait_for_web():
    while True:
        try:
            r = requests.get("http://web:5000")
            if r.status_code == 200:
                print("Webserver ready!")
                break
        except:
            print("Waiting for webserver...")
        time.sleep(2)

def visit_page(driver):
    driver.get("http://web:5000/staff")


if __name__ == "__main__":
    wait_for_web()

    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Firefox(options=options)

    driver.get("http://web:5000/?mode=unsecure")
    driver.get("http://web:5000/login")

    driver.find_element(By.NAME, "username").send_keys("jerry")
    driver.find_element(By.NAME, "password").send_keys("jerry")
    driver.find_element(By.CSS_SELECTOR, ".login-submit").click()

    # 🔁 Danach nur noch nutzen
    while True:
        visit_page(driver)
        time.sleep(60)



