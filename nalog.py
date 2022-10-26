import glob
import os
import time

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

down_dir = "download_files"


def nalog(fio: str):
    url = "https://rmsp.nalog.ru/"

    # define browser and set options
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    prefs = {"profile.default_content_settings.popups": 0,
             "download.default_directory":
                 fr"{os.getcwd()}\download_files\\",  # IMPORTANT - ENDING SLASH V IMPORTANT
             "directory_upgrade": True}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    driver.get(url)
    # find input field and select it
    driver.find_element(By.XPATH,
                        "/html/body/div[1]/div[3]/div/form/div[1]/div[2]/div[1]/div/div[1]/div/div/input").click()
    # insert FIO to input field and start searching by \n
    driver.find_element(By.XPATH,
                        "/html/body/div[1]/div[3]/div/form/div[1]/div[2]/div[1]/div/div[1]/div/div/input").send_keys(
        f"{fio}\n")
    time.sleep(1)
    # check that button to download xlsx is presented and click it
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(
        (By.XPATH,
         "/html/body/div[1]/div[3]/div/form/div[2]/div[2]/div[1]/div[2]/button")))
    driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div/form/div[2]/div[2]/div[1]/div[2]/button").click()
    time.sleep(5)
    list_of_files = glob.glob(down_dir+"/*.xlsx")  # *.xlsx means that we need any file with that format
    latest_file = max(list_of_files, key=os.path.getctime).split("\\")[1]
    os.rename(f"{os.curdir}/{down_dir}/{latest_file}", f"{os.curdir}/{down_dir}/{fio}_{latest_file}")
    return f"{fio}_{latest_file}"


def parse_xlsx(filepath: str):
    xls = pd.read_excel(down_dir + f"/{filepath}", header=2, index_col=0)
    os.remove(f"{os.curdir}/{down_dir}/{filepath}")
    fio = filepath.split("_")[0]
    filtered = xls[xls["Наименование / ФИО"] == fio.upper()]
    filtered = filtered.to_json(force_ascii=False, orient='index')
    return filtered


def parse_nalog(fio: str):
    """
    Возвращает словарь предприятий и информацию о них, которые подходят по ФИО, словарь содержит информацию:
    Наименование, Тип преприятия, Категорию, ОГРН, ИНН, Вид деятельности, Регион, Район, Город, Дата создания/удаления,
    Телефон, Эл.Почта, ВебСайт, Кол-во работников
    :type fio: Fio of user
    """
    file = nalog(fio)
    print(parse_xlsx(file))


parse_nalog('Власов Александр Александрович')