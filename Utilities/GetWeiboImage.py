#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup as bs
import re
import json


def validate_url(url):
    if url.startswith('http://') or url.startswith('https://'):
        return url
    elif url.startswith('//') or url.startswith('/'):
        return 'http://' + url.replace('/', '', 2)


def parse_weibo_id(link):
    url = validate_url(link)
    reg = r'\d{16}'
    w_id = re.search(reg, url)
    if w_id:
        return w_id.group(0)
    else:
        print('Please check, there is a 16 digits in the link.')


def get_weibo_content_json(weibo_id):
    weibo_url = 'https://m.weibo.cn/detail/{0}'.format(weibo_id)
    reg = r'\[(\{\s+.*\})\]'
    res = requests.get(weibo_url)
    soup = bs(res.text, 'html.parser')
    json_script = soup.findAll('script')[1].string
    json_script = json_script.replace('\n', ' ')
    m = re.search(reg, json_script)
    d = json.loads(m.group(0)[1:-1])
    return d


def find_all_images_in_weibo(weibo_info):
    pics = weibo_info['pic_ids']
    image_urls = []
    pic_infos = weibo_info['pics']
    for pic in pic_infos:
        if pic['pid'] in pics:
            large_url = pic['large']['url']
            image_urls.append(large_url)
    return image_urls


def download_images(img_links):
    for link in img_links:
        download_single_image(link)


def download_single_image(img_url, save_path=''):
    if len(save_path) == 0:
        save_path = img_url.split('/')[-1]

    res = requests.get(img_url)
    with open(save_path, 'wb') as f:
        for chunk in res.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)


def main():
    link = input('Please input/paste weibo share link:')
    weibo_id = parse_weibo_id(link)
    d = get_weibo_content_json(weibo_id)
    all_imgs = find_all_images_in_weibo(d['status'])
    download_images(all_imgs)


if __name__ == '__main__':
    main()
