import random

from bs4 import BeautifulSoup as bs
import requests
import json

json_file = open("file.json")
data = json.load(json_file)
useragents = open('useragents.txt').read().splitlines()


def make_request(search_type: str, search_data:str):
    search_descriptions = data[search_type].values()
    for description in search_descriptions:
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
            print(answers)
            print("="*20)


# read_json("file.json")
make_request("fio", "Власов Александр Александрович")