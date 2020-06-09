#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2020-06-08 17:07:44
# @Author  : AnarL. (anar930906@gmail.com)
# @Link    : https://anar0615.wordpress.com
# @Version : V0.5

import os
import struct
import sys
import binascii
import pdb
from pywubi import wubi


"""
这个脚本代码部分参考：https://blog.csdn.net/zhangzhenhu/article/details/7014271
使用python3语法修改

搜狗的scel词库就是保存的文本的unicode编码，每两个字节一个字符（中文汉字或者英文字母）
找出其每部分的偏移位置即可
主要两部分
    1. 全局拼音表，貌似是所有的拼音组合，字典序
        格式为(index,len,pinyin)的列表
        index: 两个字节的整数 代表这个拼音的索引
        len: 两个字节的整数 拼音的字节长度
        pinyin: 当前的拼音，每个字符两个字节，总长len
    2. 汉语词组表
        格式为(same,py_table_len,py_table,{word_len,word,ext_len,ext})的一个列表
        same: 两个字节 整数 同音词数量
        py_table_len: 两个字节 整数
        py_table: 整数列表，每个整数两个字节，每个整数代表一个拼音索引
        word_len: 两个字节 整数 代表中文词组字节数长度
        word: 中文词组，每个中文两个字节，总长度word_len
        ext_len: 两个字节 整数 代表扩展信息的长度，好像都是10
        ext: 扩展信息 前两个字节是一个整数（不知道是不是词频）后八个字节全是0

        {word_len,word,ext_len,ext}一共重复same次 同音词 相同拼音表
"""

# 拼音表偏移
startPy = 0x1540
# 汉语词组表偏移
startChinese = 0x2628

# 全局拼音表
GPy_Table = {}


# 解析结果
# 元组(词频，拼音，中文词组)的列表
GTable = []


# 将原始字节码转为字符串
def byte2str(data):
    i = 0
    length = len(data)
    ret = u''
    while i < length:
        x = data[i:i + 2]
        t = chr(struct.unpack('H', x)[0])
        if t == u'\r':
            ret += u'\n'
        elif t != u' ':
            ret += t
        i += 2
    return ret


# 获取拼音表
def getPyTable(data):
    if data[0:4] != bytes(map(ord, '\x9D\x01\x00\x00')):
        return None
    data = data[4:]
    pos = 0
    length = len(data)
    while pos < length:
        index = struct.unpack('H', data[pos: pos + 2])[0]
        pos += 2
        ln = struct.unpack('H', data[pos: pos + 2])[0]
        pos += 2
        py = byte2str(data[pos:pos + ln])
        GPy_Table[index] = py
        pos += ln


# 获取一个词组的拼音
def getWordPy(data):
    pos = 0
    length = len(data)
    ret = u''
    while pos < length:
        index = struct.unpack('H', data[pos: pos + 2])[0]
        ret += GPy_Table[index]
        pos += 2
    return ret


# 获取一个词组
def getWrod(data):
    pos = 0
    length = len(data)
    ret = u''
    while pos < length:
        index = struct.unpack('H', data[pos: pos + 2])[0]
        ret += GPy_Table[index]
        pos += 2
    return ret


# 读取中文表
def getChinese(data):
    pos = 0
    length = len(data)
    while pos < length:
        # 同音词数量
        same = struct.unpack('H', data[pos: pos + 2])[0]
        # 拼音索引表长度
        pos += 2
        py_table_len = struct.unpack('H', data[pos: pos + 2])[0]
        # 拼音索引表
        pos += 2
        py = getWordPy(data[pos: pos + py_table_len])
        pos += py_table_len
        # 中文词组
        for i in range(same):
            # 中文词组长度
            c_len = struct.unpack('H', data[pos: pos + 2])[0]
            pos += 2
            word = byte2str(data[pos: pos + c_len])
            # 扩展数据长度
            pos += c_len
            ext_len = struct.unpack('H', data[pos: pos + 2])[0]
            # 词频
            pos += 2
            count = struct.unpack('H', data[pos: pos + 2])[0]
            # 保存
            GTable.append((count, py, word))
            # 到下个词的偏移位置
            pos += ext_len


def read_scel(file_name):
    print('-' * 60)
    f = open(file_name, 'rb')
    data = f.read()
    f.close()

    if data[0:12] != bytes(map(ord, '\x40\x15\x00\x00\x44\x43\x53\x01\x01\x00\x00\x00')):
        print('确认你选择的是搜狗词库(*.scel)？')
        sys.exit(0)
        pdb.set_trace()

    print('词库名： ', byte2str(data[0x130:0x338]))
    print('词库类型： ', byte2str(data[0x338:0x540]))
    print('描述信息： ', byte2str(data[0x540:0xd40]))
    print('词库示例： ', byte2str(data[0xd40:startPy]))

    getPyTable(data[startPy:startChinese])
    getChinese(data[startChinese:])


def wubi_convert(word):
    length = len(word)
    wubi_list = wubi(word)
    ret = ''
    if length == 2:
        ret = wubi_list[0][:2] + wubi_list[1][:2]
    elif length == 3:
        ret = wubi_list[0][:1] + wubi_list[1][:1] + wubi_list[2][:2]
    elif length >= 4:
        ret = wubi_list[0][:1] + wubi_list[1][:1] + wubi_list[2][:1] + wubi_list[-1][:1]
    return ret


def main():
    fl = input('请输入搜狗词库(*.scel)路径:')
    fl = os.path.expanduser(fl)
    read_scel(fl)
    fn = os.path.split(fl)[-1]
    fn = os.path.splitext(fn)[0]
    fn = fn + '.txt'
    f = open(fn, 'w')
    for word in GTable:
        f.write(word[2])
        f.write('\t')
        f.write(wubi_convert(word[2]))
        f.write('\n')
    f.close()


if __name__ == '__main__':
    main()
