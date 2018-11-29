#! /usr/bin/env python3
# -*- coding:utf-8 -*-

# 说明：
#       这个程序主要用来根据图片，找出一笔连接所有空格而不重复的连接方法
# 流程说明：
#       1. 根据图片格子，将图片平均分割
#       2. 判断每个格子的颜色，如果是黑色，则表明该格无空格；如果是白色，则表明该格是空格；如果
#          是其他颜色，则该格是连线起点格。
#       3. 给每个格子标上序号(从0开始)，执行算法，找出对应的顺序---已完成
#       4. 根据计算结果，在原图上画出正确的路线。
import colorsys
from PIL import Image
from PIL import ImageDraw
import getopt
import sys

crop_origin = (115, 250)
crop_size = (520, 520)

DEBUG = False

# ---------------------分割图片-----------------------
def split_image(img, row, col):
    image_size = img.size
    w = int(image_size[0] / col)
    h = int(image_size[1] / row)
    splited_images = []
    for i in range(row):
        for j in range(col):
            x = j * w
            y = i * h
            temp = img.crop((x, y, x + w, y + h))
            splited_images.append(temp)
    return splited_images


# ---------------------判断空格类型-----------------------
def get_main_color(img):
    if img.mode != 'RGB':
        img = img.convert('RGB')
    delta_h = 0
    avg_h = sum(t[0] for t in [colorsys.rgb_to_hsv(*img.getpixel((x, y))) for x in range(img.size[0]) for y in range(img.size[1])]) / (img.size[0] * img.size[1])
    f = filter(lambda x: abs(colorsys.rgb_to_hsv(*x)[0] - avg_h) > delta_h, [img.getpixel((x, y)) for x in range(img.size[0]) for y in range(img.size[1])])
    beyond = list(f)
    if len(beyond):
        r = int(sum(e[0] for e in beyond) / len(beyond))
        g = int(sum(e[1] for e in beyond) / len(beyond))
        b = int(sum(e[2] for e in beyond) / len(beyond))
        for i in range(int(img.size[0] / 2)):
            for j in range(int(img.size[1] / 10)):
                img.putpixel((i, j), (r, g, b))
        return r, g, b
    return None


# ---------------------连线算法-----------------------
# 深度优先遍历, graph 为图的邻接矩阵, path为路径栈, used为已访问栈, step为已经遍历的顶点数
def dfs(graph, path, used, step):
    if step == len(graph):
        return path
    else:
        for i in range(len(graph)):
            if not used[i] and graph[path[step - 1]][i] == 1:
                used[i] = True
                path[step] = i
                if dfs(graph, path, used, step + 1) is not None:  # 递归
                    return path
                else:  # 返回父节点
                    used[i] = False
                    path[step] = -1
        return None


def init(graph, v):
    used = []
    path = []
    for i in range(len(graph)):
        used.append(False)
        path.append(-1)
    used[v] = True
    path[0] = v
    path_index = dfs(graph, path, used, 1)
    return path_index


# 返回当前结点编号
def get_index(i, j, G):
    num = 0  # 用于计算图中的空格数
    for a in range(i):
        num += G[a].count('0')
    for b in range(j):
        if G[i][b] == '0':
            num += 1
    return i * len(G[i]) + j - num


# 将一维列表转换成二维列表
def get_graph(G):
    G = [list(x) for x in G]
    EG = []
    for i in range(len(G)):
        for j in range(len(G[i])):
            if G[i][j] == '0':
                continue
            side_list = []
            if j + 1 <= len(G[i]) - 1:
                if G[i][j + 1] == '1':
                    index = get_index(i, j + 1, G)
                    side_list.append(index)
            if j - 1 >= 0:
                if G[i][j - 1] == '1':
                    index = get_index(i, j - 1, G)
                    side_list.append(index)
            if i + 1 <= len(G) - 1:
                if G[i + 1][j] == '1':
                    index = get_index(i + 1, j, G)
                    side_list.append(index)
            if i - 1 >= 0:
                if G[i - 1][j] == '1':
                    index = get_index(i - 1, j, G)
                    side_list.append(index)
            EG.append(side_list)
    return EG


# 将二维列表转换成邻接矩阵
def get_matrix(graph):
    result = [[0] * len(graph) for _ in range(len(graph))]
    for i in range(len(graph)):
        for j in graph[i]:
            result[i][j] = 1
    return result


# ---------------------读取图片-------------------------
def get_pic_info(file, row, col):
    img = Image.open(file)
    if abs(img.size[0] - img.size[1]) > 5:
        img = img.crop((crop_origin[0], crop_origin[1], crop_origin[0] + crop_size[0], crop_origin[1] + crop_size[1]))
        if DEBUG:
            img.show()
    arr = split_image(img, row, col)
    rgb_list = []
    for im in arr:
        r, g, b = get_main_color(im)
        if DEBUG:
            print(r, g, b)
        rgb_list.append([r, g, b])
    return rgb_list


# ------------------将图片转换成一维数组------------------
def get_start_point_index(color_list):
    color_str = ''.join(color_list)
    loc = color_str.find('sp')
    cnt = 0
    for ch in color_str[:loc]:
        if ch == '1':
            cnt += 1
    return cnt


def make_map_list(color_str, row, col):
    map_list = []
    for r in range(row):
        row = ''
        for c in range(col):
            row = row + color_str[r * col + c]
        map_list.append(row)
    return map_list


def judge_space_color(rgb_tuple):
    differ = 10
    if abs(rgb_tuple[0] - 37) <= differ and abs(rgb_tuple[1] - 45) <= differ and abs(rgb_tuple[2] - 61) <= differ:
        return '0'
    elif abs(rgb_tuple[0] - 155) <= differ and abs(rgb_tuple[1] - 157) <= differ and abs(rgb_tuple[2] - 162) <= differ:
        return '1'
    else:
        return 'sp'


# ----------------------------将路线画出-----------------------------
def draw_line(file, sp_index, path, row, col):
    img = Image.open(file)
    start_point = (0, 0)
    file_size = img.size
    if abs(img.size[0] - img.size[1]) > 5:
        start_point = crop_origin
        file_size = crop_size
    sp_row = int(sp_index / row)
    sp_col = int(sp_index % col)
    sp_wid = int(file_size[0] / row)
    sp_hig = int(file_size[1] / col)
    start_center = (start_point[0] + sp_wid / 2.0,
                    start_point[1] + sp_hig / 2.0)
    idx = 0
    drawer = ImageDraw.Draw(img)
    next_center = start_center
    while idx < len(path) - 1:
        draw_starter = next_center
        if path[idx + 1] - path[idx] == 1:  # 向右
            next_center = (next_center[0] + sp_wid, next_center[1])
        elif path[idx + 1] - path[idx] == -1:  # 向左
            next_center = (next_center[0] - sp_wid, next_center[1])
        elif path[idx + 1] - path[idx] > 1:  # 向下
            next_center = (next_center[0], next_center[1] + sp_hig)
        elif path[idx + 1] - path[idx] < -1:  # 向上
            next_center = (next_center[0], next_center[1] - sp_hig)

        drawer.line((draw_starter, next_center), fill='red', width=4)
        idx += 1
    img.show()


# ----------------------------一笔画函数------------------------------
def get_one_draw(file, row, col):
    rgb_list = get_pic_info(file, row, col)
    color_list = []
    for tp in rgb_list:
        color_list.append(judge_space_color(tp))
    if DEBUG:
        print(color_list)
    sp_index = get_start_point_index(color_list)
    map_list = make_map_list(''.join(color_list).replace('sp', '1'), row, col)
    G = get_graph(map_list)
    map_matrix = get_matrix(G)
    path = init(map_matrix, sp_index)
    if DEBUG:
        print(path)
    draw_line(file, sp_index, path, row, col)


# -------------------------帮助函数------------------------------
def show_usage():
    print('-' * 75)
    print('Usage : %s [-h|-i|-c|-r|-d][--help|--input|--col|--row|-debug] args' % __file__)
    print('\t-h, --help\t\t Print this help information.')
    print('\t-d, --debug\t\t Print debug info.')
    print('\t-i, --input PATH\t Input the image with quiz of Fill blank one line.')
    print('\t-r, --row NUM\t Input the quiz with how many rows.')
    print('\t-c, --col NUM\t Input the quiz with how many columns.')


# -----------------Main 函数-------------------------------
def main():
    ops, args = getopt.getopt(sys.argv[1:], 'hi:r:c:', ['help', 'input=', 'row=', 'col='])
    file = ''
    row = 0
    col = 0
    for opt, arg in ops:
        if opt in ('-h', '--help'):
            show_usage()
            sys.exit(0)
        elif opt in ('-i', '--input'):
            file = arg
        elif opt in ('-r', '--row'):
            row = int(arg)
        elif opt in ('-c', '--col'):
            col = int(arg)
        elif opt in ('-d', '--debug'):
            DEBUG = True

    if row == 0 or col == 0 or len(file) == 0 or row != col:
        show_usage()
        sys.exit(0)
    else:
        get_one_draw(file, row, col)


if __name__ == '__main__':
    # get_one_draw('Temp/test.jpg', 6, 6)
    # map_list = [
    #     '011110',
    #     '111111',
    #     '111111',
    #     '111111',
    #     '111110',
    #     '001111'
    # ]
    # G = get_graph(map_list)
    # map_matrix = get_matrix(G)
    # sp = 22
    # path = init(map_matrix, sp)
    # print(path)
    main()
