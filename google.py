from bs4 import BeautifulSoup as bs
import json


def get_requests_url(path):
    with open(path) as json_file:
        data = json.load(json_file)

        print(data.values())


# read_json("file.json")
get_requests_url("file.json", "123123")