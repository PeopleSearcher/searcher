import random

from pydantic import BaseModel, validator, root_validator
import requests
from bs4 import BeautifulSoup as bs
useragents = open('../useragents.txt').read().splitlines()

class Phone(BaseModel):
    """Class for phone number, phones numbers in Russia typically consist of 11 digits — the 1-digit (or all digits
    not considering the area code and telephone number)  country code, a 3-digit area code and a 7-digit telephone
    number. """
    phone_num: str | None = None
    country: str | None = None
    region: str | None = None
    operator: str | None = None

    @root_validator
    def parse_phone(cls, values):
        values["phone_num"] = values["phone_num"].strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        values["phone_num"] = "+" + values["phone_num"] if values["phone_num"][0] != "+" and len(values["phone_num"]) >= 11 else values["phone_num"]
        if len(values["phone_num"]) == 12:
            response = requests.get(f"https://fincalculator.ru/telefon/region-po-nomeru/{values['phone_num']}")
            soup = bs(response.text, features='html.parser')
            divs = soup.findAll('div', {'class': "tel-info_result-label"})
            for div in divs:
                if div.text == 'Страна : ':
                    values["country"] = div.nextSibling.text.strip()
                if div.text == 'Регион : ':
                    values['region'] = div.nextSibling.text.strip()
                if div.text == 'Оператор : ':
                    values['operator'] = div.nextSibling.text.strip()
        return values

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
        if self.country_code is not None:
            return f"Телефон: {self.phone_num}\nСтрана: {self.country}({self.country_code})\n" \
                   f"Принадлежность к региону: {self.region}({self.operator_code})\n" \
                   f"Оператор: {self.operator}\nКороткий номер: {self.number}"
        else:
            return f"Телефон: {self.phone_num}"
