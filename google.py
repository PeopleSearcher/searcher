import os
import random
import time

from bs4 import BeautifulSoup as bs
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import json

load_dotenv("config.env")

SELENIUM_DEBUG = os.getenv('SELENIUM_DEBUG')
json_file = open("file.json")
data = json.load(json_file)
useragents = open('useragents.txt').read().splitlines()


def make_request(search_type: str, search_data: str):
    search_descriptions = data[search_type].values()
    result = []
    for description in search_descriptions:
        if description["request"] == "request":
            user_agent = random.choice(useragents)
            headers = {
                "User-Agent": user_agent
            }
            formatted_url = description["url"].format(field=search_data)
            # TODO solve yandex problem(captcha)
            response = requests.get(formatted_url, headers=headers)
            if response.status_code == 200:
                soup = bs(response.text, "html.parser")
                cls = {}
                if 'class' in description:
                    cls = {"class": description["class"]}
                answers = soup.findAll(description["search"], cls)
                result.append(answers)
        elif description["request"] == "selenium":
            options = webdriver.ChromeOptions()
            if SELENIUM_DEBUG == "False":
                options.add_argument("--headless")

            else:
                options.add_argument("--start-maximized")
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
            # we take only surname because of saverudata.info
            driver.get(description["url"].format(field=search_data.split(" ")[0]))
            WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                (By.XPATH,
                 '//*[@id="root"]/main/article/div[6]/div/input')))
            driver.find_element(By.XPATH, '//*[@id="root"]/main/article/div[6]/div/input').click()
            driver.find_element(By.XPATH, '//*[@id="root"]/main/article/div[6]/div/input').send_keys(search_data + "\n")
            persons = []
            while True:
                WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                    (By.XPATH,
                     '//*[@id="root"]/main/article/div[6]/div/a')))
                html = driver.page_source
                soup = bs(html, "html.parser")
                phones = soup.find_all("b", string="Телефон:")
                for phone in phones:
                    persons.append(phone.parent)
                try:
                    WebDriverWait(driver, 3).until(EC.presence_of_element_located(
                        (By.XPATH,
                         "//a[text()=' следующие 100 >']")))
                    driver.find_element(By.XPATH, "//a[text()=' следующие 100 >']").click()
                except TimeoutException:
                    break
            result.append(persons)
    return result
