#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import getopt
import sys
from PIL import Image

SINGLE_IMG_SIZE = 300


def supprted_format(ext):
    exts = ['.jpg', '.png', '.jpeg']
    if ext.lower() in exts:
        return True
    return False


def expand_user_path(p):
    p = os.path.expanduser(p)
    return p


def traverse_folder_images(f):
    f = expand_user_path(f)
    ret_imgs = []
    for item in os.listdir(f):
        path = os.path.join(f, item)
        ext = os.path.splitext(path)[-1]
        if supprted_format(ext):
            ret_imgs.append(path)

    return ret_imgs


def calculate_result_image_size(img_list):
    count = len(img_list)
    ret_size = (0, 0)
    if count in [2]:
        ret_size = (SINGLE_IMG_SIZE, SINGLE_IMG_SIZE * 2)                 # {1-2}
    elif count in [3, 4]:
        ret_size = (SINGLE_IMG_SIZE * 2, SINGLE_IMG_SIZE * 2)            # {1|2-3|4}
    elif count in [5, 6]:
        ret_size = (SINGLE_IMG_SIZE * 2, SINGLE_IMG_SIZE * 3)           # {1|2-3|4-5|6}
    elif count in [7, 8, 9]:
        ret_size = (SINGLE_IMG_SIZE * 3, SINGLE_IMG_SIZE * 3)           # {1|2|3-4|5|6-7|8|9}
    elif count in [10, 11, 12]:
        ret_size = (SINGLE_IMG_SIZE * 3, SINGLE_IMG_SIZE * 4)           # {1|2|3-4|5|6-7|8|9-10|11|12}
    elif count in [13, 14, 15, 16]:
        ret_size = (SINGLE_IMG_SIZE * 4, SINGLE_IMG_SIZE * 4)            # {1|2|3|4-5|6|7|8-9|10|11|12-13|14|15|16}
    else:
        ret_size = (SINGLE_IMG_SIZE, SINGLE_IMG_SIZE)                      # {1}

    ret_size = (int(ret_size[0]), int(ret_size[1]))
    return ret_size


def calculate_img_position(img_list, idx, horizontal=True):
    count = len(img_list)
    t_dir = img_list[idx]
    img_size = resize_image_suitable(t_dir)
    ret_pos = (0, 0)
    if count in [2]:
        for i in range(count):
            if i == idx:
                # h = "变量1" if a>b else "变量2"
                pos_x = (SINGLE_IMG_SIZE - img_size[0]) / 2 if horizontal else 0
                pos_y = 0 if horizontal else (SINGLE_IMG_SIZE - img_size[1]) / 2
                ret_pos = (pos_x, pos_y)
                break
    elif count in [3, 4]:
        for i in range(count):
            if i == idx:
                pos_x = (SINGLE_IMG_SIZE * (i % 2)) if horizontal else (SINGLE_IMG_SIZE * (i % 2)) + (SINGLE_IMG_SIZE - img_size[0]) / 2
                row = int(i / 2)
                pos_y = SINGLE_IMG_SIZE * row + ((SINGLE_IMG_SIZE - img_size[1]) / 2) if horizontal else (row * SINGLE_IMG_SIZE)
                ret_pos = (pos_x, pos_y)
                break
    elif count in [5, 6]:
        for i in range(count):
            if i == idx:
                pos_x = (SINGLE_IMG_SIZE * (i % 2)) if horizontal else (SINGLE_IMG_SIZE * (i % 2)) + (SINGLE_IMG_SIZE - img_size[0]) / 2
                row = int(i / 3)
                pos_y = SINGLE_IMG_SIZE * row + ((SINGLE_IMG_SIZE - img_size[1]) / 2) if horizontal else (row * SINGLE_IMG_SIZE)
                ret_pos = (pos_x, pos_y)
                break
    elif count in [7, 8, 9]:
        for i in range(count):
            if i == idx:
                pos_x = (SINGLE_IMG_SIZE * (i % 3)) if horizontal else (SINGLE_IMG_SIZE * (i % 3)) + (SINGLE_IMG_SIZE - img_size[0]) / 2
                row = int(i / 3)
                pos_y = SINGLE_IMG_SIZE * row + ((SINGLE_IMG_SIZE - img_size[1]) / 2) if horizontal else (row * SINGLE_IMG_SIZE)
                ret_pos = (pos_x, pos_y)
                break
    elif count in [10, 11, 12]:
        for i in range(count):
            if i == idx:
                pos_x = (SINGLE_IMG_SIZE * (i % 3)) if horizontal else (SINGLE_IMG_SIZE * (i % 3)) + (SINGLE_IMG_SIZE - img_size[0]) / 2
                row = int(i / 3)
                pos_y = SINGLE_IMG_SIZE * row + ((SINGLE_IMG_SIZE - img_size[1]) / 2) if horizontal else (row * SINGLE_IMG_SIZE)
                ret_pos = (pos_x, pos_y)
                break
    elif count in [13, 14, 15, 16]:
        for i in range(count):
            if i == idx:
                pos_x = (SINGLE_IMG_SIZE * (i % 4)) if horizontal else (SINGLE_IMG_SIZE * (i % 4)) + (SINGLE_IMG_SIZE - img_size[0]) / 2
                row = int(i / 4)
                pos_y = SINGLE_IMG_SIZE * row + ((SINGLE_IMG_SIZE - img_size[1]) / 2) if horizontal else (row * SINGLE_IMG_SIZE)
                ret_pos = (pos_x, pos_y)
                break
    else:
        ret_pos = (SINGLE_IMG_SIZE, SINGLE_IMG_SIZE)
    ret_pos = (int(ret_pos[0]), int(ret_pos[1]))
    return ret_pos


def resize_image_suitable(img_path):
    img = Image.open(img_path)
    img_size = img.size
    ret_size = (0, 0)
    if img_size[0] == img_size[1]:
        ret_size = (SINGLE_IMG_SIZE, SINGLE_IMG_SIZE)
    elif img_size[0] > img_size[1]:
        img_w = SINGLE_IMG_SIZE
        img_h = SINGLE_IMG_SIZE / img_size[0] * img_size[1]
        ret_size = (int(img_w), int(img_h))
    elif img_size[0] < img_size[1]:
        img_h = SINGLE_IMG_SIZE
        img_w = SINGLE_IMG_SIZE / img_size[1] * img_size[0]
        ret_size = (int(img_w), int(img_h))
    return ret_size


def remove_transparency(im, bg_color=(255, 255, 255)):
    if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
        alpha = im.convert('RGBA').split()[-1]
        bg = Image.new('RGBA', im.size, bg_color + (255, ))
        bg.paste(im, mask=alpha)
        return bg
    else:
        return im


def combine_images(img_list, save_path='default.png'):
    count = len(img_list)
    if count == 0:
        print('No images found.')
        return

    result_size = calculate_result_image_size(img_list)
    result_img = Image.new('RGBA', result_size)

    paste_pos = (0, 0)
    for item in img_list:
        try:
            im = Image.open(item)
        except IOError:
            print("Error: Image(%s) not found." % (item))
        else:
            img_size = resize_image_suitable(item)
            im = im.resize(img_size)
            idx = img_list.index(item)
            hori = img_size[0] > img_size[1]
            paste_pos = calculate_img_position(img_list, idx, hori)
            result_img.paste(im, paste_pos)
    result_img = remove_transparency(result_img)
    result_img.save(save_path)


def show_usage():
    print('-' * 75)
    print('Usage: %s [-h|-f|-i|-o][--help|--folder|--input|--output] args' % __file__)
    print('\t-h, --help\t\t\tShow this help info.')
    print('\t-f, --folder PATH\t\tCombine all images in folder PATH')
    print('\t-i, --input PATH\t\tCombine image from PATH.')
    print('\t-o, --output PATH\t\tSave combined image to the path. Default in current folder')


def main():
    ops, args = getopt.getopt(sys.argv[1:], 'hf:i:o:', ['help', 'folder=', 'input=', 'output='])
    inputs = []
    folder = ''
    output = ''
    for opt, arg in ops:
        if opt in ('-h', '--help'):
            show_usage()
            sys.exit(1)
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
        inputs = traverse_folder_images(folder)
    if len(folder) == 0:
        temp = []
        for i in inputs:
            temp.append(expand_user_path(i))
        inputs = temp

    # print(len(inputs))
    if len(output) == 0:
        combine_images(inputs)
    else:
        combine_images(inputs, save_path=expand_user_path(output))


if __name__ == '__main__':
    main()
