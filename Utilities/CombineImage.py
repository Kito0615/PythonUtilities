#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import os, getopt, sys, math
from PIL import Image

OUTPUT_SIZE = 900

def supported_format(ext):
	exts = ['.jpg', '.png', '.jpeg']
	if ext.lower() in exts:
		return True

	return False
def expand_user_path(p):
	p = os.path.expanduser(p)
	return p

def travers_folder_images(f):
	f = expand_user_path(f)
	ret_images = []
	for item in os.listdir(f):
		path = os.path.join(f, item)
		ext = os.path.splitext(path)[-1]
		if supported_format(ext):
			ret_images.append(path)

	return ret_images

# To do : auto calculate combined image size
def auto_calculate(img_list, final_size = (900, 900)):
	pass

def combine_images(img_list, save_path = 'default.png'):
	count = len(img_list)
	if count == 0:
		print('No image found.')
		return

	ret_image = Image.new('RGBA', (OUTPUT_SIZE, OUTPUT_SIZE))
	line = int(math.sqrt(count))

	each_size = int(OUTPUT_SIZE / line)

	x = 0
	y = 0

	for item in img_list:
		try:
			im = Image.open(item)
		except IOError:
			print('Error : image(%s) not found.'%(item))
		else:
			im = im.resize((each_size, each_size))
			ret_image.paste(im, (x * each_size, y * each_size))
			x += 1
			if x == line:
				x = 0
				y += 1

	ret_image.save(save_path)

def show_usage():
	print('-'*75)
	print('Usage : %s [-h|-f|-i|-o][--help|--folder|--input|--output] args')
	print('  -h, --help\t\t\tShow this help info.')
	print('  -f, --folder PATH\t\tCombine all images in folder PATH.')
	print('  -i, --input PATH\t\tCombine image from PATH. Can be used more than 1 time.')
	print('  -o, --output PATH\t\tSave combined image to the PATH.')

def main():
	ops, args = getopt.getopt(sys.argv[1:], 'hf:i:o:', ['help', 'folder=', 'input=', 'output='])
	inputs = []
	folder = ''
	output = ''
	for opt, arg in ops:
		if opt in ('-h', '--help'):
			show_usage()
			sys.exit()
		if opt in ('-f', '--folder'):
			folder = arg
		if opt in ('-i', '--input'):
			inputs.append(arg)
		if opt in ('-o', '--output'):
			output = arg

	if len(inputs) == 0 and len(folder) == 0:
		show_usage()
		sys.exit(-1)

	if len(inputs) == 0:
		inputs = travers_folder_images(folder)
	if len(folder) == 0:
		temp = []
		for i in inputs:
			temp.append(expand_user_path(i))

		inputs = temp

	if len(output) == 0:
		combine_images(inputs)
	else:
		combine_images(inputs, expand_user_path(output))

if __name__ == '__main__':
	main()
