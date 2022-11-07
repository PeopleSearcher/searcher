import random

from pydantic import BaseModel, validator, root_validator, ValidationError
import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

useragents = open('../useragents.txt').read().splitlines()


class Phone(BaseModel):
    """Class for phone number, phones numbers in Russia typically consist of 11 digits — the 1-digit (or all digits
    not considering the area code and telephone number)  country code, a 3-digit area code and a 7-digit telephone
    number. """
    phone_num: str | None = None
    country: str | None = None
    region: str | None = None
    operator: str | None = None
    additional: str | None = None

    @root_validator
    def parse_phone(cls, values):
        if values["phone_num"] is not None:
            values["phone_num"] = values["phone_num"].strip().replace(' ', '').replace('-', '').replace('(',
                                                                                                        '').replace(')',
                                                                                                                    '')
            values["phone_num"] = "+" + values["phone_num"] if values["phone_num"][0] != "+" and len(
                values["phone_num"]) >= 11 else values["phone_num"]
            if len(values["phone_num"]) == 12:
                options = webdriver.ChromeOptions()
                options.add_argument("--headless")
                driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)
                driver.get(f"https://phonenum.info/phone/{values['phone_num'][1:]}")
                html = driver.page_source
                driver.quit()
                soup = bs(html, features='html.parser')
                not_ported = soup.find("span", {"class": "phone_not_ported_message"})
                if not_ported["style"].strip() == "display:none":
                    values['additional'] = not_ported.nextSibling.nextSibling.text.strip().replace("\n", " ")
                data = soup.find("div", {"class": 'diapason'})
                if values["phone_num"][1:-10] == "7":
                    values["country"] = "Россия"
                values[
                    'region'] = data.previousSibling.previousSibling.previousSibling.previousSibling.previousSibling.previousSibling.text
                values[
                    'operator'] = data.previousSibling.previousSibling.previousSibling.previousSibling.previousSibling.previousSibling. \
                    previousSibling.previousSibling.previousSibling.previousSibling.text
            return values
        else:
            raise ValueError("phon_num is not presented")

    @property
    def country_code(self):
        return self.phone_num[1:-10] if len(self.phone_num) >= 12 else None

    @property
    def operator_code(self):
        return self.phone_num[1:-7][-3:] if len(self.phone_num) >= 12 else None

    @property
    def number(self):
        return self.phone_num[-7:] if len(self.phone_num) >= 12 else None

    def __str__(self):
        res = f"Телефон: {self.phone_num}"
        if self.country_code is not None:
            res += f"\nСтрана: {self.country}({self.country_code})\n" \
                   f"Принадлежность к региону: {self.region}({self.operator_code})\n" \
                   f"Оператор: {self.operator}\nКороткий номер: {self.number}"
            if self.additional is not None:
                res += f"\n{self.additional}"
        return res
