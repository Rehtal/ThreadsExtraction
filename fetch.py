# -*- coding: utf-8 -*-
"""fetch.py

1, Fetch specific web pages from:
	1, hkbici
	2, SexInSex
2, Extract records from raw web page.

Using consumer and producer model.

"""
import threading
import socket
from HTMLProcessor import hkbiciHTMLProcessor as HHP
from HTMLProcessor import sisHTMLProcessor as SHP

PAGES = 50
HKBICI = 'hkbici'
SIS = 'sis'

def fetchSIS(page_empty_semaphore, page_full_semaphore, page_share_buffer):
	"""Fetch web pages from SexInSex.
	input:
	  page_empty_semaphore: semaphore for empty space.
	  page_full_semaphore: semaphore for full space.
	  page_share_buffer: shared buffer between consumer and producer"""
	# Generate all urls.
	gen_url = lambda s: "http://67.220.92.23/bbs/forum-230-"\
	+ s + ".html"

	# Prepare urls.
	all_urls = [gen_url(str(i)) for i in\
	range(1, PAGES+1)]

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
				# Traditional PV operation.
				page_empty_semaphore.acquire()
				page_share_buffer.append(opener.open(url,\
				timeout=5).read())
				page_full_semaphore.release()
			except socket.timeout:
				continue
			else:
				time.sleep(1)
				break

def fetchHKBICI(page_empty_semaphore, page_full_semaphore, page_share_buffer):
	"""Fetch web pages from hkbici.
	input:
	  page_empty_semaphore: semaphore for empty space.
	  page_full_semaphore: semaphore for full space.
	  page_share_buffer: shared buffer between consumer and producer"""
	# Generate all urls.
	gen_url = lambda s: "http://hkbici.com/forum-2-"\
	+ s + ".html"

	# Prepare urls.
	all_urls = [gen_url(str(i)) for i in\
	range(1, PAGES+1)]

	# Prepare cookie.
	# More detail: 
	# http://stackoverflow.com/questions/189555/how-to-use-python-to-login-to-a-webpage-and-retrieve-cookies-for-later-usage
	import urllib, urllib2, cookielib
	cookie_data = {'username':'Rehtal', 'password':'19900326zmR'}
	cj = cookielib.CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	encoded_data = urllib.urlencode(cookie_data)
	opener.open("http://hkbici.com/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes",\
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
				# Traditional PV operation.
				page_empty_semaphore.acquire()
				page_share_buffer.append(opener.open(url,\
						timeout=5).read())
				page_full_semaphore.release()
			except socket.timeout:
				continue
			else:
				time.sleep(1)
				break

def extract(site, page_empty_semaphore, page_full_semaphore,\
page_share_buffer, record_empty_semaphore, record_full_semaphore,\
record_share_buffer, end_event):
	"""Extract records from site.
	input:
 	 page_empty_semaphore: empty semaphore for pages.
	 page_full_semaphore: full semaphore for pages.
	 page_share_buffer: shared buffer between page consumer and
	   producer.
 	 record_empty_semaphore: empty semaphore for records.
	 record_full_semaphore: full semaphore for records.
	 record_share_buffer: shared buffer between record consumer and
	   producer.
	 end_event: no more record and set end signal."""
	# Traditional PV operation.
	if site==HKBICI:
		p = HHP()
	elif site==SIS:
		p = SHP()
	for i in range(PAGES): 
		page_full_semaphore.acquire()
		p.reset()
		p.feed(page_share_buffer.pop())
		page_empty_semaphore.release()
		new_records = p.get_records()
		record_share_buffer.extend(new_records)
		for record in new_records:
			record_empty_semaphore.acquire()
			record_full_semaphore.release()

	end_event.set()

	# Below codes can solve the bug that classify threads no
	# ending cuz they will wait for the full semaphore.
	end_record = {}
	end_record['title'] = ''
	end_record['href'] = '' 
	record_empty_semaphore.acquire()
	record_share_buffer.append(end_record)
	record_full_semaphore.release()

def fetchThreadings(thread_args):
	"""Combine all these functions together using multi-thread.
	input:
	  thread_args: all necessary variables for threading."""
	# Prepare data
	sis = {}
	sis['page_full_semaphore'] = threading.Semaphore(0)
	sis['page_empty_semaphore'] = threading.Semaphore(PAGES)
	sis['page_share_buffer'] = []
	hkbici = {}
	hkbici['page_full_semaphore'] = threading.Semaphore(0)
	hkbici['page_empty_semaphore'] = threading.Semaphore(PAGES)
	hkbici['page_share_buffer'] = []

	# Threading.
	sis_producer = threading.Thread(target=fetchSIS, kwargs=sis)
	sis_producer.start()
	sis_producer.setName('Get SIS pages')

	extend_sis = sis.copy()
	extend_sis.update(thread_args[SIS])
	extend_sis['site'] = SIS
	sis_consumer = threading.Thread(target=extract, kwargs=extend_sis)
	sis_consumer.start()
	sis_consumer.setName('Extract SIS pages')
	
	hkbici_producer = threading.Thread(target=fetchHKBICI,\
	kwargs=hkbici)
	hkbici_producer.start()
	hkbici_producer.setName('Get HKBICI pages')
	
	extend_hkbici = hkbici.copy()
	extend_hkbici.update(thread_args[HKBICI])
	extend_hkbici['site'] = HKBICI
	hkbici_consumer = threading.Thread(target=extract, kwargs=extend_hkbici)
	hkbici_consumer.start()
	hkbici_consumer.setName('Extract HKBICI pages')

	return [sis_producer, sis_consumer, hkbici_producer, hkbici_consumer]

if __name__ == "__main__":
	pass
