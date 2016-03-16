# -*- coding: utf-8 -*-

import random

from imageporndirtyrubot.exception import APIException

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

from bs4 import BeautifulSoup
import requests


USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9) AppleWebKit/537.71 (KHTML, like Gecko) Version/7.0 Safari/537.71',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:25.0) Gecko/20100101 Firefox/25.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
]

GOOGLE_BASE_URL = 'http://www.google.com/'
GOOGLE_SEARCH_BY_ENDPOINT = 'http://images.google.com/searchbyimage?hl=en&image_url={}'


class GoogleCaptchaAPIException(APIException):
    pass


def raw_request(url, referer):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4',
        'Cache-Control': 'no-cache',
        'Connection': 'close',
        'DNT': '1',
        'Pragma': 'no-cache',
        'Referer': referer,
        'User-Agent': random.choice(USER_AGENTS),
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise APIException('Google Exception: {}'.format(str(e)), http_code=e.response.status_code)

    soup = BeautifulSoup(response.content, 'html5lib')

    # check for Fucking Google Captcha
    if soup.find_all('input', {'name': 'captcha'}):
        raise GoogleCaptchaAPIException()

    return soup


def find_higher_resolution_image(url, min_width=0, min_height=0):
    result = raw_request(GOOGLE_SEARCH_BY_ENDPOINT.format(url), referer='http://www.google.com/imghp')

    all_sizes_a_tag = result.find('a', text='All sizes')
    if not all_sizes_a_tag:
        # nothing found :(
        return None, None

    all_sizes_url = urlparse.urljoin(GOOGLE_BASE_URL, all_sizes_a_tag['href'])
    all_sizes_result = raw_request(all_sizes_url, referer=all_sizes_url)
    img_links = all_sizes_result.find_all('a', {'class': 'rg_l'})

    # find biggest image
    result_url = None
    result_w = min_width
    result_h = min_height
    for a in img_links:
        preview_url = a['href']
        querystring = urlparse.urlparse(preview_url).query
        querystring_dict = urlparse.parse_qs(querystring)

        w = int(querystring_dict['w'][0])
        h = int(querystring_dict['h'][0])
        if (w > result_w or h > result_h) and w >= result_w and h >= result_h:
            # bigger image found
            result_url = querystring_dict['imgurl'][0]
            result_w = w
            result_h = h

    if result_url:
        return result_url, (result_w, result_h)
    return None, None
