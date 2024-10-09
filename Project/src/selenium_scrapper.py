from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import sys

import unittest, time, re

OUT = "selenium_out"
SCORES = (
    "10,10",
    "9.0,9.9",
    "8.0,8.9",
    "7.0,7.9",
    "6.0,6.9",
    "5.0,5.9",
    "4.0,4.9",
    "3.0,3.9",
    "2.0,2.9",
    "1.0,1.9",
    "0.0,0.9",
)
START_SCORE = 7
SCROLLS = 100

class Sel(unittest.TestCase):
    def setUp(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.ign.com/reviews/games"
        self.verificationErrors = []
        self.accept_next_alert = True
    def test_sel(self):
        driver = self.driver
        delay = 3
        driver.get(self.base_url)
        driver.find_element(By.ID, "onetrust-reject-all-handler").click()
        select = Select(driver.find_element(By.ID, "scoreRange"))
        for score in SCORES[START_SCORE:]:
            select.select_by_value(score)
            print("Scraping", score, "scores.")
            time.sleep(3)
            prevYOffset = -1
            for i in range(1,SCROLLS + 1):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                yOffset = self.driver.execute_script("return window.pageYOffset;")
                print(f"\r{i} scrolls (y={yOffset}). ", end="")
                if prevYOffset == yOffset:
                    print(f"Ended.")
                    prevYOffset = -1
                    break
                if i == SCROLLS:
                    print("Skipping.")
                prevYOffset = yOffset
                time.sleep(3)
            html_source = driver.page_source
            filename = f"{OUT}/result{score.split(',')[0]}.html"
            with open(filename, "w") as f:
                f.write(html_source)
                print(f"Saved to \"{f"{OUT}/result{score.split(',')[0]}.html"}\"")

if __name__ == "__main__":
    unittest.main()