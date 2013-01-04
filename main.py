# -*- coding: utf-8 -*-
"""main.py

Main fucntion of this project.

Using multi-thread technique. 
Obviously, this is a traditional producer/consumer model. Use
semaphore can implement this model.

"""
import threading
import classify
import fetch

SHARE_SIZE = 100

if __name__ == "__main__":
	# Fetch web pages & Extract records.
	thread_args = {}

	sis = {}
	sis['record_empty_semaphore'] = threading.Semaphore(SHARE_SIZE)
	sis['record_full_semaphore'] = threading.Semaphore(0)
	sis['record_share_buffer'] = []
	sis['end_event'] = threading.Event()
	thread_args['sis'] = sis

	hkbici = {}
	hkbici['record_empty_semaphore'] = threading.Semaphore(SHARE_SIZE)
	hkbici['record_full_semaphore'] = threading.Semaphore(0)
	hkbici['record_share_buffer'] = []
	hkbici['end_event'] = threading.Event()
	thread_args['hkbici'] = hkbici

	threads = []
	t = fetch.fetchThreadings(thread_args)
	threads.extend(t)
	t = classify.classifyThreadings(thread_args)
	threads.extend(t)
	
	for t in threads:
		print 'Waiting:', t.getName()
		t.join()
		print 'Finish:', t.getName()
