# -*- coding: utf-8 -*-
"""hkbisiHTMLProcessor.py

This file implement basic class hkbisiHTMLProcessor for
extracting records from hkbisi.com.

"""
from copy import deepcopy
from sgmllib import SGMLParser

class hkbisiHTMLProcessor(SGMLParser):
	"""Extract records from hkbisi.com."""
	def reset(self):
		# Flags
		self.record_flag = False
		self.detail_flag = False

		# Result
		self.all_records = []
		self.cur_record = {}

		SGMLParser.reset(self)

	def start_tbody(self, attrs):
		if attrs.__len__() == 0:
			return
		if attrs[0][0]=='id' and \
			attrs[0][1].rfind('normalthread_')==0:
				self.record_flag = True
	
	def end_tbody(self):
		if self.record_flag:
			self.all_records.append(deepcopy(self.cur_record))
			self.record_flag = False
	
	def start_a(self, attrs):
		if ('class', 'xst') in attrs and self.record_flag:
			self.detail_flag = True
			self.cur_record['href'] = "http://hkbisi.com/" + \
					[value for key, value in attrs if \
					key=='href'][0]

	def end_a(self):
		self.detail_flag = False

	def handle_data(self, text):
		if self.detail_flag:
			self.cur_record['title'] = text
	
	def get_records(self):
		return self.all_records

if __name__ == '__main__':
	p = hkbisiHTMLProcessor()
	content = open('test.htm').read()
	p.feed(content)
	for record in p.get_records():
		print record['href']
