# -*- coding: utf-8 -*-
"""check.py

Basic class for checking information from:
	1, hkbisi
	2, SexInSex

"""
import socket

class Check():
	"""Class for checking new posts of bbs."""
	# Names of websites.
	SIS = 'sis'
	HKBISI = 'hkbisi'
	# Websites that we will check.
	check_sites = {HKBISI:"http://hkbisi.com/forum.php",\
			SIS:"http://67.220.92.23/bbs"}
	

	def __init__(self, user="Rehtal", password="19900326zmR"):
		"""arg:
			user: user name of hkbisi.
			password: corresponding password of user."""
		self.cookie_data = {'username':user,\
				'password':password}

		self.raw_data = {self.HKBISI:[], self.SIS:[]}
		self.all_records = {self.HKBISI:[], self.SIS:[]}
		self.final_results = {self.HKBISI:[], self.SIS:[]}

		# CONSTANT VARIABLES
		self.PAGES = 50
	
	def fetch(self):
		"""Fetch records from bbs included in
		check_sites."""

		# Multi-threads will be used here in later version.
		self._fetch_hkbisi()
		self._fetch_sis()
	
	def check(self, keywords, check_type):
		"""Check records and save to files.
		arg:
			keywords: this is a list that stores all keywords
			and those records that contain such keywords
			consist of the result.
			
			check_type: a string that describe such check
			style such as 'subtitle' or 'tokyo hot'."""

		# Multi-threads will be used here in later version.
		self._check_hkbisi(keywords, check_type)
		self._check_sis(keywords, check_type)

	def _fetch_hkbisi(self):
		"""This function begin to fetch records from
		hkbisi."""
		
		# Generate all urls.
		gen_url = lambda s: "http://hkbisi.com/forum-2-"\
				+ s + ".html"

		# Prepare urls.
		all_urls = [gen_url(str(i)) for i in\
				range(1, self.PAGES+1)]

		# Prepare cookie.
		# More detail: 
		# http://stackoverflow.com/questions/189555/how-to-use-python-to-login-to-a-webpage-and-retrieve-cookies-for-later-usage
		import urllib, urllib2, cookielib
		cj = cookielib.CookieJar()
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
		encoded_data = urllib.urlencode(self.cookie_data)
		opener.open("http://hkbisi.com/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes",\
				encoded_data)

		# Not using list conprehension because we need to
		# suspend a while in case the web site reject too
		# many requests in a short time.  
		# Multi-threads can be used to enhance this part.
		import time
		for url in all_urls:
			print "Fetching:"+url
			while True:
				try:
					self.raw_data[self.HKBISI].append(opener.open(url,\
						timeout=5).read())
				except socket.timeout:
					continue
				else:
					time.sleep(1)
					break

		# Extract records.
		from hkbisiHTMLProcessor import\
				hkbisiHTMLProcessor as HHP
		for page in self.raw_data[self.HKBISI]:
			p = HHP()
			p.feed(page)
			self.all_records[self.HKBISI].extend(p.get_records())

	def _check_hkbisi(self, keywords, check_type):
		"""Check the result of hkbisi.
		
		arg:see self.run()"""
		self.final_results[self.HKBISI] = []

		# Check.
		import re
		f = open(self.HKBISI+"_records.txt", 'w')
		for record in self.all_records[self.HKBISI]:
			f.write(record['title']+'\n')
			f.write(record['href']+'\n')
			f.write('\n\n\n')

			title = record['title'].decode('utf8')

			if record not in self.final_results[self.HKBISI] and\
					[keyword for keyword in keywords if\
					re.search(keyword, title) is not None]\
					.__len__()!=0:
				self.final_results[self.HKBISI].append(record)
		f.close()
		
		# Prepare date of today.
		from datetime import datetime
		now = datetime.now().strftime("%Y_%m_%d")

		# Make dir named the date of today.
		import os
		os.system("mkdir \""+self.HKBISI+"/"+now+"\"")

		# Dump to files.
		f = open(self.HKBISI+"/"+now+"/"+check_type+".html", 'w')
		f.write("<table>\n")
		for record in self.final_results[self.HKBISI]:
			f.write("<tr><th><a href=\"%(href)s\">%(title)s</a>\
					</th></tr>" % record)
		f.write("</table>")
		f.close()
	
	def _fetch_sis(self):
		"""This function begin to fetch records from
		hkbisi."""

		# Generate all urls.
		gen_url = lambda s: "http://67.220.92.23/bbs/forum-230-"\
				+ s + ".html"

		# Prepare urls.
		all_urls = [gen_url(str(i)) for i in\
				range(1, self.PAGES+1)]

		import time
		import urllib2
		# Set proxy because of GFW.
		proxy_handler = urllib2.ProxyHandler({"http":"http://127.0.0.1:8087"})
		opener = urllib2.build_opener(proxy_handler)
		# Not using list conprehension because we need to
		# suspend a while in case the web site reject too
		# many requests in a short time.  
		# Multi-threads can be used to enhance this part.
		for url in all_urls:
			print "Fetching:"+url
			while True:
				try:
					self.raw_data[self.SIS].append(opener.open(url,\
						timeout=5).read())
				except socket.timeout:
					continue
				else:
					time.sleep(1)
					break

		# Extract records.
		from sisHTMLProcessor import\
				sisHTMLProcessor as SHP
		for page in self.raw_data[self.SIS]:
			p = SHP()
			p.feed(page)
			self.all_records[self.SIS].extend(p.get_records())

	def _check_sis(self, keywords, check_type):
		"""Check the result of sis.
		
		arg:see self.run()"""
		self.final_results[self.SIS] = []

		# Check.
		import re
		f = open(self.SIS+"_records.txt", 'w')
		for record in self.all_records[self.SIS]:
			f.write(record['title']+'\n')
			f.write(record['href']+'\n')
			f.write('\n\n\n')

			title = record['title'].decode('gbk')

			if record not in self.final_results[self.SIS] and\
					[keyword for keyword in keywords if\
					re.search(keyword, title) is not None]\
					.__len__()!=0:
				self.final_results[self.SIS].append(record)
		f.close()
		
		# Prepare date of today.
		from datetime import datetime
		now = datetime.now().strftime("%Y_%m_%d")

		# Make dir named the date of today.
		import os
		os.system("mkdir \""+self.SIS+"/"+now+"\"")

		# Dump to files.
		f = open(self.SIS+"/"+now+"/"+check_type+".html", 'w')
		f.write("<table>\n")
		for record in self.final_results[self.SIS]:
			f.write("<tr><th><a href=\"%(href)s\">%(title)s</a>\
					</th></tr>" % record)
		f.write("</table>")
		f.close()

if __name__ == "__main__":
	c = Check()
	c.fetch()
	keywords = {}
	keywords['subtitle'] = [u'中文', u'字幕']
	keywords['tokyo_hot'] = [ur"东[京]?热", ur"東[京]熱",\
			ur"[T,t]okyo[-, ]*[H,h]ot"]
	keywords['double'] = [ur"[两,兩]穴", ur"[双,雙]插"]

	for key, value in keywords.items():
		c.check(value, key)
