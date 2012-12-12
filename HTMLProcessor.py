# -*- coding: utf-8 -*-
"""HTMLProcessor.py

Implement HTML parser for:
	1, sis
	2, hkbisk
Job is extracting records from raw web pages.

"""
from copy import deepcopy
from sgmllib import SGMLParser

class sisHTMLProcessor(SGMLParser):
	"""Extract records from SexInSex."""
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

	def start_span(self, attrs):
		if self.record_flag is not True:
			return
		if attrs.__len__()==0:
			return
		if attrs[0][0]=='id' and \
			attrs[0][1].rfind('thread_')==0:
				self.detail_flag = True
				# First statement of self.cur_record['title']
				self.cur_record['title'] = ''
				self.cur_record['href'] = "http://67.220.92.23/bbs/"\
						+ attrs[0][1].replace('_', '-') + "-1-1.html"

	def end_span(self):
		self.detail_flag = False
	
	def handle_data(self, text):
		if self.detail_flag:
			# The reason using += instead of = is that the
			# whole text will be divided into some parts.
			# 
			# For example, the text "Hello<try>" will be
			# divided to "Hello", "<", "try", ">", thus we
			# need to combine them back by using +=.
			#
			# The first statement of this variable is in
			# function start_span.
			self.cur_record['title'] += text
	
	def get_records(self):
		return self.all_records

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
	content = open('p').read()
	p.feed(content)
	for record in p.get_records():
		print record['href']
		print record['title']
		print '\n'