# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import requests
import json
import time

# 去重结果，追加写入到文件，返回新增结果数
def drop_duplicates(filename, results):
	f = open(filename + ".txt", "a+")
	f.seek(0)
	l = f.readlines()
	rows = len(l)
	l.extend(results)
	l = set(l)
	f.truncate(0)
	f.seek(0)
	f.writelines(l)
	f.close()
	return len(l) - rows


class ZoomEye(object):
	def __init__(self, username=None, password=None):
		self.username = username
		self.password = password

		self.access_token = ''
		# self.zoomeye_login_api = "https://api.zoomeye.org/user/login"
		# self.zoomeye_dork_api = "https://api.zoomeye.org/{}/search"

		self.ip_port_list = []
		self.ip_list = []

		self.load_access_token()

	def load_access_token(self):
		if not os.path.isfile('access_token.txt'):
			print('[-] info : access_token file is not exist, please login first...')
			self.login()
		else:
			with open('access_token.txt', 'r') as fr:
				self.access_token = fr.read()

	def save_access_token(self):
		with open('access_token.txt', 'w') as fw:
			fw.write(self.access_token)

	def login(self):
		"""
		Prompt to input account name and password
		:return: None
		"""
		self.username = ''
		self.password = ''
		print('[*] try to login ...')
		data = {
			'username': self.username,
			'password': self.password
		}

		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'
		}

		# dumps 将 python 对象转换成 json 字符串
		data_encoded = json.dumps(data)
		try:
			resp = requests.post(url='https://api.zoomeye.org/user/login', data=data_encoded, headers=headers)
			# loads() 将 json 字符串转换成 python 对象
			r_decoded = json.loads(resp.text)

			# 获取到账户的access_token
			access_token = r_decoded['access_token']
			self.access_token = access_token
			self.save_access_token()
		except:
			print('[-] info : username or password is wrong, please try again ')
			exit()

	def search(self,data):

		if not self.access_token:
			self.login()

		# 将 token 格式化并添加到 HTTP Header 中
		headers = {
			'Authorization': 'JWT ' + self.access_token,
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'
		}

		# 要搜索的字符串  query = 'port:80 weblogic country:China'
		query = data

		# 设置获取结果的起始页面,对于量比较大的时候比较有用
		page = 1

		# 设置获取的结果页数
		num = 1

		index = 0
		while True:
			try:
				# 将查询字符串和页数结合在一起构造URL
				if index == num:
					break
				msg = '[{}/{}] fetch page: {}'.format(index+1, num, page)
				print(msg)

				api = 'https://api.zoomeye.org/host/search'
				# searchurl = '{}{}&page={}'.format(api, query, page)
				print('query==>', query)

				# 用于获取下一页的结果
				page += 1
				index += 1

				resp = requests.get(api, headers=headers, params={"query": query, "page": page})
				r_decoded = json.loads(resp.text)
				for x in r_decoded['matches']:
					#print(x['ip'], ':', x['portinfo']['port'])
					self.ip_port_list.append(x['ip'] + ':' + str(x['portinfo']['port'])+"\n")
					self.ip_list.append(x['ip']+"\n")
			except Exception as e:
				# 若搜索请求超过 API 允许的最大条目限制 或者 全部搜索结束，则终止请求
				if str(e) == 'matches':
					print('[-] info : account was break, excceeding the max limitations')
					break
				else:
					print('[-] info : ', str(e))
		self.save_result()
		pass

	def save_result(self):
		drop_duplicates('zoomeye_result',self.ip_port_list)
		drop_duplicates('zoomeye_ip',self.ip_list)





if __name__ == '__main__':
	file = open("domain.txt")
	for text in file.readlines():
		data1 = 'ssl:"'+text.strip('\n')+'"'
		data2 = 'hostname:"'+text.strip('\n')+'"'
		data3 = 'site:"'+text.strip('\n')+'"'
		zoomeye = ZoomEye()
		zoomeye.search(data1)
		zoomeye = ZoomEye()
		zoomeye.search(data2)
		zoomeye = ZoomEye()
		zoomeye.search(data3)
		pass