#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import re
import requests
import sys
import traceback
from datetime import datetime
from datetime import timedelta
from lxml import etree
import time as sysTime

class Weibo:
    """Weibo class."""
    cookie = {'Cookie' : ''}
    headers = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'Host' : 'weibo.com'}
    def __init__(self, user_id, filter = 0):
        self.user_id = user_id
        self.filter = filter
        self.username = ''
        self.weibo_num = 0
        self.weibo_num2 = 0
        self.following = 0
        self.followers = 0
        self.weibo_content = []
        self.weibo_place = []
        self.publish_time = []
        self.up_num = []
        self.retweet_num = []
        self.comment_num = []
        self.publish_tool =[]

    def get_user_name(self):
        try:
            url = 'https://weibo.cn/%d/info'%(self.user_id)
            html = requests.get(url, cookies = self.cookie).content
            selector = etree.HTML(html)
            username = selector.xpath('//title/text()')[0]
            self.username = username[:-3]
            # print('用户名:' + self.username)
        except Exception as e:
            print('Error : ', e)
            traceback.print_exc()

    def get_user_info(self):
        try:
            url = 'https://weibo.cn/u/%d?filter=%d&page=1'%(self.user_id, self.filter)
            html = requests.get(url, cookies = self.cookie).content
            selector = etree.HTML(html)
            pattern = r'\d+\.?\d*'

            str_wb = selector.xpath("//div[@class='tip2']/span[@class='tc']/text()")[0]
            guid = re.findall(pattern, str_wb, re.S|re.M)
            for value in guid:
                num_wb = int(value)
                break
            self.weibo_num = num_wb
            # print('微博数:', str(self.weibo_num))

            str_gz = selector.xpath("//div[@class='tip2']/a/text()")[0]
            guid = re.findall(pattern, str_gz, re.M)
            self.following = int(guid[0])
            # print('关注数:', str(self.following))

            str_fs = selector.xpath("//div[@class='tip2']/a/text()")[1]
            guid = re.findall(pattern, str_fs, re.M)
            self.followers = int(guid[0])
            # print('粉丝数:', str(self.followers))
            print('='*30)
        except Exception as e:
            print('Error :', e)
            traceback.print_exc()

    def get_long_weibo(self, weibo_link):
        try:
            html = requests.get(weibo_link, cookies = self.cookie).content
            selector = etree.HTML(html)
            info = selector.xpath("//div[@class='c']")[1]
            wb_content = info.xpath("div/span[@class='ctt']")[0].xpath("string(.)")
            wb_content = wb_content[1:]
            return wb_content
        except Exception as e:
            print('Error :', e)
            traceback.print_exc()

    def get_weibo_info(self):
        try:
            url = 'https://weibo.cn/u/%d?filter=%d&page=1'%(self.user_id, self.filter)
            html = requests.get(url, cookies = self.cookie).content
            selector = etree.HTML(html)
            if selector.xpath("//input[@name='mp']") == []:
                page_num = 1
            else:
                page_num = (int)(selector.xpath("//input[@name='mp']")[0].attrib['value'])
            pattern = r'\d+\.?\d*'
            for page in range(1, page_num + 1):
                url2 = 'https://weibo.cn/u/%d?filter=%d&page=%d' % (self.user_id, self.filter, page)
                html2 = requests.get(url2, cookies=self.cookie).content
                selector2 = etree.HTML(html2)
                info = selector2.xpath("//div[@class='c']")
                is_empty = info[0].xpath("div/span[@class='ctt']")
                if is_empty:
                    for i in range(len(info) - 2):
                        str_t = info[i].xpath("div/span[@class='ctt']")
                        weibo_content = str_t[0].xpath("string(.)")
                        weibo_content = weibo_content[:-1]
                        weibo_id = info[i].xpath("@id")[0][2:]
                        a_link = info[i].xpath("div/span[@class='ctt']/a/@href")
                        if a_link:
                            if (a_link[-1] == '/comment/' + weibo_id or '/comment/' + weibo_id + '?' + a_link[-1]):
                                weibo_link = 'https://weibo.cn' + a_link[-1]
                                wb_content = self.get_long_weibo(weibo_link)
                                if wb_content:
                                    weibo_content = wb_content
                        self.weibo_content.append(weibo_content)
                        # print('微博内容 : ', weibo_content)

                        div_first = info[i].xpath("div")[0]
                        a_list = div_first.xpath('a')
                        weibo_place = '无'
                        for a in a_list:
                            if 'https://place.weibo.com/imgmap/center' in a.xpath('@href')[0] and a.xpath("text()")[0] == '显示地图':
                                weibo_place = div_first.xpath("span[@class='ctt']/a")[-1]
                                if '的秒拍视频' in div_first.xpath("span[@class='ctt']/a")[-2]:
                                    weibo_place = weibo_place.xpath("string(.)")
                                    break
                        self.weibo_place.append(weibo_place)
                        # print('微博位置:', weibo_place)

                        str_time = info[i].xpath("div/span[@class='ct']")
                        str_time = str_time[0].xpath("string(.)")
                        publish_time = str_time.split('来自')[0]
                        if '刚刚' in publish_time:
                            publish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        elif '分钟' in publish_time:
                            minute = publish_time[:publish_time.find('分钟')]
                            minute = timedelta(minutes=int(minute))
                            publish_time = (datetime.now() - minute).strftime('%Y-%m-d %H:%M:%S')
                        elif '今天' in publish_time:
                            today = datetime.now().strftime('%Y-%m-%d')
                            time = publish_time[3:]
                            publish_time = today + ' ' + time
                        elif '月' in publish_time:
                            year = datetime.now().strftime('%Y')
                            month = publish_time[0:2]
                            day = publish_time[3:5]
                            time = publish_time[7:12]
                            publish_time = (year + '-' + month + '-' + day + ' ' + time)
                        else:
                            publish_time = publish_time[:16]
                        self.publish_time.append(publish_time)
                        # print('微博发布时间 :', publish_time)

                        if len(str_time.split('来自')) > 1:
                            publish_tool = str_time.split('来自')[1]
                        else:
                            publish_tool = '无'
                        self.publish_tool.append(publish_tool)
                        # print('微博来自:', publish_tool)

                        str_footer = info[i].xpath("div")[-1]
                        str_footer = str_footer.xpath("string(.)")
                        str_footer = str_footer[str_footer.rfind('赞'):]
                        guid = re.findall(pattern, str_footer, re.M)

                        up_num = int(guid[0])
                        self.up_num.append(up_num)
                        # print('赞 : ', str(up_num))

                        retweet_num = int(guid[1])
                        self.retweet_num.append(retweet_num)
                        # print('转 : ', str(retweet_num))

                        comment_num = int(guid[2])
                        self.comment_num.append(comment_num)
                        # print('评 : ', str(comment_num))
                        # print('='*30)

                        self.weibo_num2 += 1

            if not self.filter:
                print('共', str(self.weibo_num2), '条微博')
            else:
                print('共', str(self.weibo_num), '条微博,其中', str(self.weibo_num2), '条为原创微博。')
            sysTime.sleep(1.5)
        except Exception as e:
            print('Error : ', e)
            traceback.print_exc(e)

    def write_txt(self):
        try:
            if self.filter:
                result_header = '\n\n原创微博内容:\n'
            else:
                result_header = '\n\n微博内容:\n'
            result = ('用户信息\n用户昵称:' + self.username +
                      '用户id:' + str(self.user_id) +
                      '微博数:' + str(self.weibo_num) +
                      '关注数:' + str(self.following) +
                      '粉丝数:' + str(self.followers) +
                      result_header)
            for i in range(self.weibo_num2 + 1):
                text = (str(i) + ':' + self.weibo_content[i - 1] + '\n' +
                        '微博位置:' + self.weibo_place[i - 1] + '\n' +
                        '发布时间:' + self.publish_time[i - 1] + '\n' +
                        '点赞数:' + str(self.up_num[i - 1]) +
                        '转发数:' + str(self.retweet_num[i - 1]) +
                        '    评论数:' + str(self.comment_num[i - 1]) + '\n' +
                        '发布工具:' + self.publish_tool[i - 1] + '\n\n')
                result = result + text
            file_dir = os.path.split(os.path.realpath(__file__))[0] + os.sep + 'weibo'
            if not os.path.isdir(file_dir):
                os.mkdir(file_dir)
            file_path = file_dir + os.sep + self.username + '(%d)' % self.user_id + '.txt'
            f = open(file_path, 'wb')
            f.write(result.encode('utf-8'))
            f.close()
            print('微博写入文件完毕.')
            print('保存路径:', file_path)
        except Exception as e:
            print('Error : ', e)
            traceback.print_exc()

    def start(self):
        try:
            self.get_user_name()
            self.get_user_info()
            self.get_weibo_info()
            self.write_txt()
            print('信息抓取完成.')
            print('=' * 30)
        except Exception as e:
            print('Error : ', e)
            traceback.print_exc()


def main():
    try:
        user_id = 2662779307
        filter = 0
        wb = Weibo(user_id, filter)
        wb.start()
        print('用户名:', wb.username)
        print('全部微博数:', str(wb.weibo_num))
        print('关注数:', str(wb.following))
        print('粉丝数:', str(wb.followers))
        if wb.weibo_content:
            print('最新/置顶 微博内容:', wb.weibo_content[0])
            print('最新/置顶 微博位置:', wb.weibo_place[0])
            print('最新/置顶 微博发布时间:', wb.publish_time[0])
            print('最新/置顶 微博获赞:', wb.up_num[0])
            print('最新/置顶 微博转发:', wb.retweet_num[0])
            print('最新/置顶 微博评论:', wb.comment_num[0])
            print('最新/置顶 微博发布工具:', wb.publish_tool[0])
    except Exception as e:
        print('Error : ', e)
        traceback.print_exc()


if __name__ == '__main__':
    main()
