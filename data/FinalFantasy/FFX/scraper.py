from urllib.request import urlopen
import time
from os import path
import re

base = "http://www.finalfantasyquotes.com"
indexPage = "http://www.finalfantasyquotes.com/ffx/script/Zanarkand"
index = urlopen(indexPage).read().decode('utf-8')
pages = re.findall("href=['\"](/ffx/script/.*?)['\"]>",index)

pages = [x.replace("&amp;","&") for x in pages]

pageNum = 0
for page in pages:
	print(page)
	pageNum += 1
	fileName = "raw/page_"+str(pageNum).zfill(3)+".html"
	if not path.exists(fileName):
		html = urlopen(base+page).read().decode('utf-8')
		o = open(fileName,'w')
		o.write(html)
		o.close()
		time.sleep(2)

