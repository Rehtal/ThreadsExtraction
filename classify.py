# -*- coding: utf-8 -*-
"""classify.py

Classify all records by matching keywords.

Using consumer and producer model.

"""

from datetime import datetime
import threading
import re
import os

def record_classify(keywords, site, record_empty_semaphore,\
record_full_semaphore, record_share_buffer, end_event):
	"""Filter hkbici records by matching keywords.
	input:
	  site: hkbici or sis.
	  keywords: dict of keywords.
	  record_empty_semaphore: empty space for record_share_buffer.
	  record_full_semaphore: remain space for record_share_buffer.
	  record_share_buffer: records shared buffer.
	  end_event: end event for no more product.
	output:
	  no output."""
	# Prepare date of today.
	now = datetime.now().strftime("%Y_%m_%d")

	# Make dir named the date of today.
	os.system("mkdir \""+site+"\"")
	os.system("mkdir \""+site+"/"+now+"\"")
	
	# Create files corresponding to keyword type.
	pass_files = {}
	for keyword_type in keywords.keys():
		pass_files[keyword_type] =\
		open('./'+site+"/"+now+"/"+keyword_type+".html", 'w')
		pass_files[keyword_type].write("<table>\n")

	# All records must be backuped.
	all_file = open('./'+site+"_records.txt", 'w')

	# Store those checked records.
	checked_records = []

	while end_event.isSet()==False:
		# PV operation.
		record_full_semaphore.acquire()
		record = record_share_buffer.pop()
		record_empty_semaphore.release()

		if record in checked_records:
			continue

		all_file.write(record['title']+'\n')
		all_file.write(record['href']+'\n')
		all_file.write('\n\n\n')

		belong_types = check_keywords(keywords, record)
		for belong_type in belong_types:
			pass_files[belong_type].write\
			("<tr><th><a href=\"%(href)s\"> %(title)s</a></th></tr>\n" % record)

		checked_records.extend(record)
	
	# Close all opened files.
	for keyword_type in keywords.keys():
		pass_files[keyword_type].write("</table>")
		pass_files[keyword_type].close()
	all_file.close()

def check_keywords(keywords, record):
	"""Using keywords to classify record.
	input:
	  keywords: dict of keywords.
	  record: a record.
	output:
	  A list of keyword types that this record belongs to."""

	# Make sure coding is utf8
	try:
		title = record['title'].decode('gbk')
	except UnicodeDecodeError:
		try:
			title = record['title'].decode('utf8')
		except:
			#print 'ERROR:', record
			return []

	belong_types = []
	for keywords_item in keywords.items():
		keyword_type, keywords = keywords_item
		
		if [keyword for keyword in keywords if \
			re.search(keyword, title) is not None]\
			.__len__()!=0:
			belong_types.append(keyword_type)

	return belong_types

def load_keywords():
	"""Load keywords from file.
	output:
	  a dict to keywords."""
	keywords = {}
	cur_keyword = ''
	f = open('keywords', 'r')
	for line in f.readlines():
		line = line.strip('\n')
		if line.__len__()==0:
			continue
		if line[0]=='[' and line[-1]==']':
			cur_keyword = line[1:-1]
			keywords[cur_keyword] = []
		else:
			keywords[cur_keyword].append(line.decode('utf8'))
	f.close() 

	return keywords

def classifyThreadings(thread_args):
	"""Combine all these functions together using multi-thread.
	input:
	  thread_args: all necessary variables for threading."""
	keywords = load_keywords()
	threads = []
	for key in thread_args:
		v = thread_args[key].copy()
		v['keywords'] = keywords
		v['site'] = key
		t = threading.Thread(target=record_classify, kwargs=v)
		t.start()
		t.setName('classify:'+key)
		threads.append(t)
	
	return threads
