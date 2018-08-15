#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import os, sys, time, re, json, random, getopt
import requests
from lxml.html import fromstring
import urllib.parse as parse

class BDPanDownloader(object):
	"""docstring for BDPanDownloader"""
	def __init__(self, link, password = '', isEncrypt = False, isFolder = False):
		super(BDPanDownloader, self).__init__()
		self.link = link
		self.password = password
		self.isEncrypt = isEncrypt
		self.isFolder = isFolder

		self.session = requests.Session()
		self.file = ''
		self.primaryID = ''
		self.uk = ''
		self.sign = ''
		self.timestamp = ''
		self.fidList = ''
		self.verifyCodeString = ''
		self.verifyCodeInput = ''
		self.headers = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36', 'Host' : 'pan.baidu.com', 'Origin' : 'https://pan.baidu.com'}

	def initCookies(self):
		self.session.get(url = 'http://pan.baidu.com', headers = self.headers)

	def verifyPassword(self):
		match = re.match(r'http[s]?://[pan|yun]\.baidu\.com/s/1(.*)', self.link)
		if not match:
			print('匹配链接错误.')
			return False

		url = 'https://pan.baidu.com/share/verify'
		surl = match.group(1)
		payload = {'surl' : surl, 't' : str(int(time.time() * 1000)), 'bdstoken' : 'null', 'channel' : 'chunlei', 'clienttype' : '0', 'web' : '1', 'app_id' : '250528'}
		data = {'pwd' : self.password, 'vcode' : '', 'vcode_str' : ''}

		self.headers['Referer'] = self.link
		res = self.session.post(url = url, data = data, params = payload, headers = self.headers)
		d = json.loads(res.text)

		return True if d['errno'] == 0 else False

	def getParams(self):
		try:
			res = self.session.get(self.link, headers = self.headers)
			res.encoding = 'utf-8'
			self.file = fromstring(res.content).findtext('.//title').split('_')[0]
			m = re.search('\"sign\":\"(.+?)\"', res.text)
			self.sign = m.group(1)
			m = re.search('\"timestamp\":(\d+?),', res.text)
			self.timestamp = m.group(1)
			m = re.search('\"shareid\":(\d+?),', res.text)
			self.primaryID = m.group(1)
			m = re.search('\"uk\":(\d+?),', res.text)
			self.uk = m.group(1)
			m = re.search('\"fs_id\":(\d+?),', res.text)
			self.fidList = '[' + m.group(1) + ']'
			return True
		except Exception as e:
			print(self.sign, self.timestamp, self.primaryID, self.fidList)
			return False

	def getVerifyCode(self):
		print('正在下载验证码...')

		url = 'http://pan.baidu.com/api/getvcode'
		payload = {'prod' : 'pan' , 't' : random.random(), 'bdstoken' : 'null', 'channel' : 'chunlei', 'clienttype' : '0', 'web' : '1', 'app_id' : '250528'}
		res = self.session.get(url = url, params = payload, headers = self.headers)
		d = json.loads(res.text)

		self.verifyCodeString = d['vcode']

		# Save verify code image
		img = 'verify_code.jpg'
		res = self.session.get(url = 'http://pan.baidu.com/genimage?' + self.verifyCodeString, headers = self.headers)
		with open(img, 'wb') as f:
			for chunk in res.iter_content(chunk_size = 1024):
				f.write(chunk)

		f.close()
		self.open_file(img)
		self.verifyCodeInput = input('请输入验证码:')
		os.remove(img)

	def open_file(self, path):
		# open verify code
		if os.name == nt:
			os.system('start ' + path)
		else:
			if os.uname()[0] == 'Linux':
				os.system('eog ' + path)
			else:
				os.system('open ' + path)

	def getResponseJson(self, needVerify = False):
		url = 'http://pan.baidu.com/api/sharedownload'
		payload = {'sign' : self.sign, 'timestamp' : self.timestamp, 'bdstoken' : 'null', 'channel' : 'chunlei', 'clienttype' : '0', 'web' : '1', 'app_id' : '250528'}
		data = {'encrypt' : '0', 'product' : 'share', 'type' : 'nolimit', 'uk' : self.uk, 'primaryid' : self.primaryID, 'fid_list' : self.fidList}
		if self.isFolder:
			data['type'] = 'batch'

		if self.isEncrypt:
			data['extra'] = '{"sekey":"' + parse.unquote(self.session.cookies['BDCLND']) + '"}'

		if needVerify:
			data['vcode_input'] = self.verifyCodeInput
			data['vcode_str'] = self.verifyCodeString

		res = self.session.post(url = url, params = payload, data = data, headers = self.headers)
		return json.loads(res.text)

	def error_code_meaning(self, errno):
		info = {
		0 : '成功', 
		-1 : '下载的内容中包含违规信息',
		-20 : '显示验证码',
		113 : '页面已过期',
		116 : '该分享不存在',
		118 : '没有下载权限',
		121 : '选择操作的文件过多'
		}
		return info[errno]

	def getDownloadLink(self):
		try:
			self.initCookies()
			if self.isEncrypt:
				if not self.verifyPassword():
					print('分享文件的密码错误.')
					return None

			if not self.getParams():
				print('请输入分享密码.')
				return None

			# try to get the download link for the first time(without verify code)
			js = self.getResponseJson()
			while True:
				if js['errno'] == 0:
					return js['dlink'] if self.isFolder else js['list'][0]['dlink']
				elif js['errno'] == -20:
					self.getVerifyCode()
					js = self.getResponseJson(needVerify = True)
				else:
					print('错误代码:', js['errno'])
					print('错误信息:', self.error_code_meaning(js['errno']))
					return None
		except Exception as e:
			print('出现异常 : ', e)
			return None

	def download_file(self):
		link = self.getDownloadLink()
		f = open(self.file, 'wb')
		print('正在下载 : ', self.file)
		res = self.session.get(link)
		for chunk in res.iter_content(chunk_size = 1024 * 1024):
			f.write(chunk)

		self.open_file(f)



def show_usage():
	print('-'*75)
	print('Usage : {} [-h|-f|-d|-p][--help|--folder|--download|--password] [arg] url')
	print('  -h, --help\t\t\tShow this help info.')
	print('  -f, --folder\t\t\tSharing link is folder.')
	print('  -d, --download\t\t\tDownload sharing file directly.')
	print('  -p, --password PASSWORD\t\tSharing file is encrypted.')

def main():
	opts, args = getopt.getopt(sys.argv[1:-1], 'hfdp:', ['help', 'folder', 'download', 'password='])
	password = ''
	folder = False
	download = False
	for opt, arg in opts:
		if opt in ('-h', '--help'):
			show_usage()
			sys.exit()
		if opt in ('-d', '--download'):
			download = True
		if opt in ('-f', '--folder'):
			folder = True
		if opt in ('-p', '--password'):
			password = arg

	if not sys.argv[-1].startswith('http'):
		print('请输入链接.')
		show_usage()
		sys.exit()

	if len(password) > 0 and len(password) != 4:
		print('密码长度错误。')
		sys.exit(0)

	enc = False
	if len(password) == 4:
		enc = True

	pan = BDPanDownloader(sys.argv[-1], password = password, isEncrypt = enc, isFolder = folder)
	if not download:
		link = pan.getDownloadLink()
		print(pan.file, ':', link)
	else:
		pan.download_file()

if __name__ == '__main__':
	main()

