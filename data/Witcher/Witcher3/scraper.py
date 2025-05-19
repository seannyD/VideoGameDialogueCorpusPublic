from urllib.request import *
from urllib.error import HTTPError
#from bs4 import BeautifulSoup
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
	#html = BeautifulSoup(html, 'lxml')
	#html = html.find("main")
	return(html)
	

url = "https://raw.githubusercontent.com/thetobysiu/witcher-3-data-pre-processing/refs/heads/master/w3dialog_id.txt"

html = openPage(url)

o = open("raw/w3dialog_id.txt",'w')
o.write(html)
o.close()