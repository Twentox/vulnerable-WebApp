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

def visit_page():
    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Firefox(options=options)

    driver.get("http://web:5000")

    driver.add_cookie({
    "name": "session",
    "value": "eyJtb2RlIjoidW5zZWN1cmUiLCJyb2xlIjoic3RhZmYifQ.adUS8w.FpTmyggnoK__1y7w5bSxKGirE-Q"
    })

    driver.get("http://web:5000/staff")

    driver.close()


if __name__ == "__main__":
    wait_for_web()

    while True:
        visit_page()
        time.sleep(60)


