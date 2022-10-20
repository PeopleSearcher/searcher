import json
import urllib
from io import BytesIO
from os.path import basename

import requests

from utils.logger import setup_logger, log_er

BASE_VK_URL = 'https://api.vk.com/method/'

setup_logger(__name__)
printit = False
SZ_MN = 400
SZ_MX = 700
PHOTOS_LOAD = 30
PHOTOS_KEEP = 10


def vkapi_params(args=None):
    if not args:
        args = {}
    args['access_token'] = ""
    args['v'] = '5.131'
    args['lang'] = 'ru'
    return args


args = {
    'count': 1000,
    'offset': 0,
}


def bio_download(url):
    # print('bio_download:\n' + url)
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        bio = BytesIO()
        bio.name = basename(url)
        for chunk in r:
            bio.write(chunk)
        bio.seek(0)
        # print(len(bio.read()))
        return bio


def find_best_img(img):
    url = None
    w, h, mn = 0, 0, 0
    # album_id PROFILE=-6, WALL=-7
    for size in img['sizes']:
        new_mn = min(size['width'], size['height'])
        save = False
        if url is None:
            save = True
        elif new_mn > mn:
            if mn >= SZ_MN:
                if new_mn < SZ_MX:
                    save = True
            else:
                save = True
        elif new_mn >= SZ_MN and mn > SZ_MX:
            save = True
        if save:
            url = size['url']
            w, h = size['width'], size['height']
            mn = new_mn
    return w, h, img['album_id'], url


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


def get_user_photos_urls(user_id):
    # Returns a list with photo urls
    # print('get_user_photos({})'.format(user_id))
    args = {
        'owner_id': user_id,
        'count': PHOTOS_LOAD,
    }
    response = requests.get(BASE_VK_URL + 'photos.getAll' + '?' + urllib.parse.urlencode(vkapi_params(args)))
    data = response.content.decode('utf-8')
    if response.status_code == 200:
        data = json.loads(data)
        if 'response' in data:
            data = data['response']
            res = []
            for img in data['items']:
                cur = find_best_img(img)
                if cur[3] is not None:
                    res.append(cur)
            res.sort(key=lambda x: x[2], reverse=True)
            res = res[:PHOTOS_KEEP]
            res = list(map(lambda x: x[3], res))
            return res
        else:
            done = False
            if not done:
                txt = '- Vk Error in photos.getAll: NO response:\n{}'.format(data)
                print(txt)
                log_er(txt)
    else:
        txt = '- Vk Error in photos.getAll: bad status_code: {}\n{}'.format(response.status_code, data)
        print(txt)
        log_er(txt)
    return []


def get_user_photos(user_id, print_urls=False):
    urls = get_user_photos_urls(user_id)
    if print_urls:
        print(urls)
    res = {}
    for url in urls:
        if url is None:
            log_er('- Vk url is None user_id {}'.format(user_id))
            continue
        bio = bio_download(url)
        # key = '{}-{}'.format(user_id, bio.name.split('.')[0])
        key = bio.name.split('.')[0]
        res[key] = bio
    return res


def get_user_by_screen_name(screen_name: str):
    args = {"user_ids": screen_name}
    data = get('users.get', args=args)
    return data
# users = get_users_search({})
# for user in users:
#     photos = get_user_photos(user["id"])
#     print(photos)

screen_names = ["vechnodoma", "no_bches", "young_gnom"]
users = get_user_by_screen_name(",".join(screen_names))
print(users)