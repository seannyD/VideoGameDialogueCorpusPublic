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
	html = html.find("div",{"id":"mw-content-text"})
	return(html)
	
# In order
pages = [
	"https://aceattorney.fandom.com/wiki/The_Lost_Turnabout_-_Transcript",
	
	"https://aceattorney.fandom.com/wiki/Reunion,_and_Turnabout_-_Transcript_-_Part_1",
	"https://aceattorney.fandom.com/wiki/Reunion,_and_Turnabout_-_Transcript_-_Part_2",
	"https://aceattorney.fandom.com/wiki/Reunion,_and_Turnabout_-_Transcript_-_Part_3",
	"https://aceattorney.fandom.com/wiki/Reunion,_and_Turnabout_-_Transcript_-_Part_4",
	
	"https://aceattorney.fandom.com/wiki/Turnabout_Big_Top_-_Transcript_-_Part_1",
	"https://aceattorney.fandom.com/wiki/Turnabout_Big_Top_-_Transcript_-_Part_2",
	"https://aceattorney.fandom.com/wiki/Turnabout_Big_Top_-_Transcript_-_Part_3",
	"https://aceattorney.fandom.com/wiki/Turnabout_Big_Top_-_Transcript_-_Part_4",
	
	"https://aceattorney.fandom.com/wiki/Farewell,_My_Turnabout_-_Transcript_-_Part_1",
	"https://aceattorney.fandom.com/wiki/Farewell,_My_Turnabout_-_Transcript_-_Part_2",
	"https://aceattorney.fandom.com/wiki/Farewell,_My_Turnabout_-_Transcript_-_Part_3",
	"https://aceattorney.fandom.com/wiki/Farewell,_My_Turnabout_-_Transcript_-_Part_4"
]

pageNum = 0
for page in pages:
	print(page)
	pageNum += 1
	fname = "raw/p" + f"{pageNum:02d}" + "_" + page[page.rindex("/")+1:] + ".html"
	fname = fname.replace(",","")
	if not os.path.isfile(fname):
		html = openPage(page)
		o = open(fname, "w")
		o.write(str(html))
		o.close()
		time.sleep(2)