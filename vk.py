import json
import urllib
from io import BytesIO
from os.path import basename

import requests
from dataclasses import dataclass
from pydantic import BaseModel, ValidationError, Field, validator

from utils.logger import setup_logger, log_er

BASE_VK_URL = 'https://api.vk.com/method/'

setup_logger(__name__)
printit = False
SZ_MN = 400
SZ_MX = 700
PHOTOS_LOAD = 30
PHOTOS_KEEP = 10


class City(BaseModel):
    id: int
    title: str


class University(BaseModel):
    id: int
    city_id = Field(default=-1, alias="city")
    country_id = Field(default=-1, alias="country")
    graduation: int = None
    name: str = None


class School(BaseModel):
    id: int
    city_id = Field(default=-1, alias="city")
    country_id = Field(default=-1, alias="country")
    year_from: int = None
    year_to: int = None
    name: str = None


# @dataclass(init=True, repr=True, frozen=True)
class VKUserEntity(BaseModel):
    id: int
    first_name: str
    last_name: str
    b_date = Field(default="", alias="bdate")
    city: City = None
    company = Field(default="")
    connections: dict = None
    universities: list[University] = []
    schools: list[School] = []
    home_town: str = None
    maiden_name: str = None
    sex: int = None
    mobile_phone: int = None


def vkapi_params(args=None):
    if not args:
        args = {}
    args['access_token'] = "vk1.a.TXQbXslZNhPdBXNWP8w357P3Uk6VGrIAiJmQzHzjBpX-U1gr2PKz2ykR5RAGHTPXz89hcDFa1KkuUQFj9YJYJj2-Vd089zkZ1QLp6I2WZ6u0_eK9IwN5HTAqO98gtwq6BsDnifFJjWu5NL3-rWtj-5NU9gt1VX494uB720e7uMiBtFx9mxjKeP91LHikX9HR"
    args['v'] = '5.131'
    args['lang'] = 'ru'
    return args


args = {
    'count': 1000,
    'offset': 0,
}


# def bio_download(url):
#     # print('bio_download:\n' + url)
#     r = requests.get(url, stream=True)
#     if r.status_code == 200:
#         bio = BytesIO()
#         bio.name = basename(url)
#         for chunk in r:
#             bio.write(chunk)
#         bio.seek(0)
#         # print(len(bio.read()))
#         return bio
#
#
# def find_best_img(img):
#     url = None
#     w, h, mn = 0, 0, 0
#     # album_id PROFILE=-6, WALL=-7
#     for size in img['sizes']:
#         new_mn = min(size['width'], size['height'])
#         save = False
#         if url is None:
#             save = True
#         elif new_mn > mn:
#             if mn >= SZ_MN:
#                 if new_mn < SZ_MX:
#                     save = True
#             else:
#                 save = True
#         elif new_mn >= SZ_MN and mn > SZ_MX:
#             save = True
#         if save:
#             url = size['url']
#             w, h = size['width'], size['height']
#             mn = new_mn
#     return w, h, img['album_id'], url


def get(method, args=None):
    response = requests.get(BASE_VK_URL + method + '?' + urllib.parse.urlencode(vkapi_params(args)))
    data = response.content.decode('utf-8')
    if printit:
        print('- ' + method + ':')
        print(data)
    if response.status_code == 200:
        data = json.loads(data)
        if 'response' in data:
            return data['response']
        else:
            txt = '- Vk Error in {}: NO response:\n{}'.format(method, data)
            print(txt)
            log_er(txt)
    else:
        txt = '- Vk Error in {}: bad status_code: {}\n{}'.format(method, response.status_code, data)
        print(txt)
        log_er(txt)
    return None


def get_users_search(params, fields=None, fun=None, count=1000, offset=0):
    # https://vk.com/dev/users.search
    # Returns a list with user_id's
    # print('get_users_search(count={}, offset={})'.format(count, offset))
    args = {
        'count': count,
        'offset': offset,
    }
    args.update(params)
    if fields is not None:
        args['fields'] = ','.join(fields)

    data = get('users.search', args)
    if data is not None and 'items' in data:
        data = data['items']
        if fun is not None:
            fun(data)
        return data
    if fun is None:
        return []


def vk_search(fi: str):
    params = {
        'q': fi,
        'fields': "bdate, universities, screen_name, schools, "
                  "maiden_name, city, connections, country, "
                  "home_town"
    }
    return parse_vk_search(get_users_search(params=params))


def parse_vk_search(response):
    print(response)
    vk_users = []

    for item in response:
        # vk_id = item['id']
        # first_name = item['first_name']
        # last_name = item['last_name']
        # b_date = '' if not ('bdate' in item) else item['bdate']
        # city = '' if not ('city' in item) else item['city']
        # company = '' if not ('company' in item) else item['company']
        # connections = '' if not ('connections' in item) else item['connections']
        # universities = []
        # if 'universities' in item:
        #     for university in item['universities']:
        #         universities.append(university['name'])
        # home_town = '' if not ('hometown' in item) else item['home_town']
        # maiden_name = '' if not ('maiden_name' in item) else item['maiden_name']
        # sex = -1 if not ('sex' in item) else item['sex']
        # mobile_phone = '' if not ('mobile_phone' in item) else item['mobile_phone']
        #
        # vk_user = VKUserEntity(
        #     vk_id,
        #     first_name,
        #     last_name,
        #     b_date,
        #     city,
        #     company,
        #     connections,
        #     universities,
        #     home_town,
        #     maiden_name,
        #     sex,
        #     mobile_phone
        # )

        raw_json_user = json.dumps(item)
        vk_user = VKUserEntity.parse_raw(raw_json_user)

        vk_users.append(vk_user)

    return vk_users


# def get_user_photos_urls(user_id):
#     # Returns a list with photo urls
#     # print('get_user_photos({})'.format(user_id))
#     args = {
#         'owner_id': user_id,
#         'count': PHOTOS_LOAD,
#     }
#     response = requests.get(BASE_VK_URL + 'photos.getAll' + '?' + urllib.parse.urlencode(vkapi_params(args)))
#     data = response.content.decode('utf-8')
#     if response.status_code == 200:
#         data = json.loads(data)
#         if 'response' in data:
#             data = data['response']
#             res = []
#             for img in data['items']:
#                 cur = find_best_img(img)
#                 if cur[3] is not None:
#                     res.append(cur)
#             res.sort(key=lambda x: x[2], reverse=True)
#             res = res[:PHOTOS_KEEP]
#             res = list(map(lambda x: x[3], res))
#             return res
#         else:
#             done = False
#             if not done:
#                 txt = '- Vk Error in photos.getAll: NO response:\n{}'.format(data)
#                 print(txt)
#                 log_er(txt)
#     else:
#         txt = '- Vk Error in photos.getAll: bad status_code: {}\n{}'.format(response.status_code, data)
#         print(txt)
#         log_er(txt)
#     return []
#
#
# def get_user_photos(user_id, print_urls=False):
#     urls = get_user_photos_urls(user_id)
#     if print_urls:
#         print(urls)
#     res = {}
#     for url in urls:
#         if url is None:
#             log_er('- Vk url is None user_id {}'.format(user_id))
#             continue
#         bio = bio_download(url)
#         # key = '{}-{}'.format(user_id, bio.name.split('.')[0])
#         key = bio.name.split('.')[0]
#         res[key] = bio
#     return res
#
#
# def get_users_info(screen_name: str):
#     args = {"user_ids": screen_name, "fields": "about, activities, bday, status, universities, screen_name, schools, "
#                                                "relatives, quotes, personal, occupation, nickname, military, "
#                                                "maiden_name, books, career, city, connections, contacts, country, "
#                                                "domain, home_town, intersts"}
#     data = get('users.get', args=args)
#     return data


# users = get_users_search({})
# for user in users:
#     photos = get_user_photos(user["id"])
#     print(photos)

print(vk_search("Ramil Salakhov"))

