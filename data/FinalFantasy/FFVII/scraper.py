from urllib.request import urlopen
import time
from os import path

base = "http://www.yinza.com/Fandom/Script/"

pageNum = 1
for pageNum in range(48):
	pageNum += 1
	urlx = "http://www.yinza.com/Fandom/Script/" + str(pageNum).zfill(2) + ".html"
	fileName = "raw/page_"+str(pageNum).zfill(2)+".html"
	if not path.exists(fileName):
		html = urlopen(urlx).read().decode('utf-8')
		o = open(fileName,'w')
		o.write(html)
		o.close()
		time.sleep(2)

