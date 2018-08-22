#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup as bs
import os

def get_images(weico_url):
	res = requests.get(weico_url)
	soup = bs(res.text, 'html.parser')

	text_div = soup.find('div', {'class' : 'weibo-text'})
	img_tags = text_div.find_next('div').findAll('img')
	imgs = []
	for tag in img_tags:
		imgs.append(validate_url(tag['src']))

	return imgs

def validate_url(url):
	if url.startswith('http://') or url.startswith('https://'):
		return url
	elif url.startswith('//') or url.startswith('/'):
		return 'http://' + url.replace('/', '', 2)

def download_image(img_url, save_path = ''):
	if len(save_path) == 0:
		save_path = img_url.split('/')[-1]

	res = requests.get(img_url)
	with open(save_path, 'wb') as f:
		for chunk in res.iter_content(chunk_size = 512 * 1024):
			if chunk:
				f.write(chunk)

def main():
	url = input('please input or paste weico share url:')
	if len(url) == 0:
		print('Error!')
	images = get_images(url)
	idx = 1
	for item in images:
		download_image(item, save_path = '{}.jpg'.format(idx))
		idx += 1
	os.system('open .')

if __name__ == '__main__':
	main()