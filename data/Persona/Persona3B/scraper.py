from urllib.request import *
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import re,time
import os


def openPage(url):
	req = Request(
		url, 
		data=None, 
		headers={
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
		}
	)
	html = urlopen(req).read().decode('utf-8')
	html = BeautifulSoup(html, 'lxml')
	html = html.find("div",{"id":"faqtext"})
	return(html)
	

page = "https://gamefaqs.gamespot.com/ps2/932312-shin-megami-tensei-persona-3/faqs/50852"

html = openPage(page)
txt = html.get_text()

o = open("raw/p3.txt",'w')
o.write(txt)
o.close()