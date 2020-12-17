#!/usr/bin/env python3
# -*- encoding:utf-8 -*-
import requests, re, os, sys, getopt
import datetime, time
from bs4 import BeautifulSoup as bs
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.image as pimg

class point:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.available = []
		self.value = 0


def rowNum(p, sudoku):
	row = set(sudoku[p.y * 9 : (p.y + 1) * 9])
	row.remove(0)
	return row

def colNum(p, sudoku):
	col = []
	length = len(sudoku)
	for i in range(p.x, length, 9):
		col.append(sudoku[i])
	col = set(col)
	col.remove(0)
	return col

def blockNum(p, sudoku):
	block_x = p.x // 3
	block_y = p.y // 3
	block = []
	start = block_y * 3 * 9 + block_x * 3
	for i in range(start, start + 3):
		block.append(sudoku[i])

	for i in range(start + 9, start + 9 + 3):
		block.append(sudoku[i])

	for i in range(start + 9 + 9, start + 9 + 9 + 3):
		block.append(sudoku[i])

	block = set(block)
	block.remove(0)
	return block

def initPoint(sudoku):
	pointList = []
	length = len(sudoku)
	for i in range(length):
		if sudoku[i] == 0:
			p = point(i % 9, i // 9)
			for j in range(1, 10):
				if j not in rowNum(p, sudoku) and j not in colNum(p, sudoku) and j not in blockNum(p, sudoku):
					p.available.append(j)

			pointList.append(p)

	return pointList

def tryInsert(p, sudoku):
	availableNum = p.available
	for v in availableNum:
		p.value = v
		if check(p, sudoku):
			sudoku[p.y * 9 + p.x] = p.value
			if len(pointList) <= 0:
				showSudoku(sudoku, fill = True)
				end_time = time.time()
				use_time = end_time - start_time
				print('解开数独耗时:%.3f s'%use_time)
				exit()
			p2 = pointList.pop()
			tryInsert(p2, sudoku)
			sudoku[p2.y * 9 + p2.x] = 0
			sudoku[p.y * 9 + p.x] = 0
			p2.value = 0
			pointList.append(p2)

		else :
			pass


def check(p, sudoku):
	if p.value == 0:
		print('not assign value to point p!')
		return False
	if p.value not in rowNum(p, sudoku) and p.value not in colNum(p, sudoku) and p.value not in blockNum(p, sudoku):
		return True
	else:
		return False

def sudokuStringToList(sudoku_str):
	sudoku_str_list = list(sudoku_str)
	sudoku = []
	for p in sudoku_str_list:
		sudoku.append(int(p))

	return sudoku

def showSudoku(sudoku, fill):
	for j in range(9):
		if j % 3 == 0:
			print('='*38)
		else:
			print('-'*38)
		for i in range(9):
			if i == 0:
				print('||', end='')
			if (i + 1) % 3 == 0:
				print('%d |'%sudoku[j * 9 + i], end = '|')
			else:
				print('%d | '%sudoku[j * 9 + i], end = '')
		print('')
	print('='*38)

	local_time = time.strftime('%Y-%b-%d %H-%M:%S', time.localtime())
	ti = ''
	if fill == True:
		ti = local_time + '-fill.png'
	else :
		ti = local_time + '-blank.png'
	draw_sudoku(sudoku, title = ti)
	# img = pimg.read(ti)
	# iPlot = plt.imshow(img)
	# plt.show()
	

def cal_sudoku(sudoku_str):
	sudoku = sudokuStringToList(sudoku_str)
	global pointList, start_time, origin_sudoku
	origin_sudoku = sudoku[:]
	pointList = initPoint(sudoku)
	showSudoku(sudoku, fill = False)
	print('')
	p = pointList.pop()
	time.sleep(2)
	start_time = time.time()
	tryInsert(p,sudoku)

def get_sudoku_str():
	url = 'http://nine.websudoku.com'
	res = requests.get(url)
	soup = bs(res.text, 'html.parser')
	tb = soup.find('table', id = 'puzzle_grid')
	tds = tb.findAll('td')
	rt = ''
	for td in tds:
		space = td.find('input')
		if space.has_attr('value'):
			rt = ''.join([rt, space['value']])
		else:
			rt = ''.join([rt, '0'])

	return rt

def draw_sudoku(sudoku, title):
	# import blank image
	im = Image.open('./../resources/blank.png')

	# draw border
	draw = ImageDraw.Draw(im)
	draw.line([0,0,0,900,900,900,900,0,0,0], fill = "#000000", width = 10)

	# draw space
	for i in range(9):
		if i % 3 != 0:
			draw.line([i * 100, 0, i * 100, 900], fill = "#000000", width = 5)
			draw.line([0, i * 100, 900, i * 100], fill = "#000000", width = 5)
		else :
			draw.line([i * 100, 0, i * 100, 900], fill = "#000000", width = 10)
			draw.line([0, i * 100, 900, i * 100], fill = "#000000", width = 10)
	# draw text
	font = ImageFont.truetype('msyh.ttf', 50)
	for j in range(9):
		for i in range(9):
			start_top = (i * 100, j * 100)
			val = sudoku[j * 9 + i]
			val_str = ''
			if val == 0:
				val_str = ' '
			else :
				val_str = str(val)

			size = draw.textsize(val_str, font = font)
			inline_top = ((100 - size[0]) / 2, (100 - size[1]) / 2)
			text_top = (start_top[0] + inline_top[0], start_top[1] + inline_top[1])
			if origin_sudoku[j * 9 + i] == 0:
				draw.text(text_top, text = val_str, font = font, fill = "#ff0000", algin = "center")
			else :
				draw.text(text_top, text = val_str, font = font, fill = '#000000', algin = "center")

	del draw
	im.save(title)
	im.show()
	im.close()

def show_help():
	print('Usage: {} [OPTIONS]'.format(os.path.basename(__file__)))
	print('OPTIONS:')
	print('\t-m : Input sudoku by manul.')
	print('\t-w : Get sudoku from http://www.websudoku.com')
	print('\t-c : Get sudoku from http://cn.sudokupuzzle.org')
	print('\t-d : Input date of http://cn.sudokupuzzle.org. Default is today. Date format yyyy-mm-dd')
	print('\t-t : Difficulty of sudoku. Default difficulty is "middle". Available types: beginner, primary, middle, senior, professional')
	sys.exit(1)

def get_sudoku_puzzle(date = '', difficulty = 'middle'):
	year = month = day = ''
	if len(date) == 0:
		d = datetime.date.fromtimestamp(time.time() - 864400)
		year = d.year
		month = d.month
		day = d.day
	else :
		year = date.split('-')[0]
		month = date.split('-')[1]
		day = date.split('-')[2]

	difficulties = {'beginner' : 0, 'primary' : 1, 'middle' : 2, 'senior' : 3, 'professional' : 4}
	url = 'http://cn.sudokupuzzle.org/online2.php?nd={}&y={}&m={}&d={}'.format(difficulties[difficulty], year, month, day)
	res = requests.get(url)
	return parse_sudoku_str_from_sudokupuzzle(res.text)

def parse_sudoku_str_from_sudokupuzzle(content):
	reg = r'\d{81}'
	m = re.search(reg, content)
	sudoku_str = m.group(0)[:81]
	return sudoku_str
		

if __name__ == '__main__':
	try:
		options, args = getopt.getopt(sys.argv[1:],'hmwc:d:t:', ['help', 'websudoku', 'sudokupuzzle', 'date=', 'type='])
		date = ''
		diff = 'middle'
		for name, value in options:
			if name in ('-h', '--help'):
				show_help()
			elif name in ('-w', '--websudoku'):
				sudoku_str = get_sudoku_str()
				cal_sudoku(sudoku_str)
				sys.exit(0)
			elif name in ('-c', '--sudokupuzzle'):
				sudoku_str = value
			elif name in ('-d', '--date'):
				date = value
			elif name in ('-t', '--type'):
				diff = value

		if sudoku_str == None:
			sudoku_str = get_sudoku_puzzle(date = date, difficulty = diff)
		cal_sudoku(sudoku_str)


	except Exception as e:
		raise e