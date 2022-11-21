from urllib.request import urlopen
import time
from os import path
import re


pages = ["http://auronlu.istad.org/ffx-script/chapter-i-into-spira/","http://auronlu.istad.org/ffx-script/chapter-ii-besaid-island/","http://auronlu.istad.org/ffx-script/chapter-iii-kilika-ferries/","http://auronlu.istad.org/ffx-script/chapter-iv-luca/","http://auronlu.istad.org/ffx-script/chapter-v-operation-miihen-djose/","http://auronlu.istad.org/ffx-script/chapter-vi-the-moonflow/","http://auronlu.istad.org/ffx-script/chapter-vii-guadosalam-thunder-plains/",'http://auronlu.istad.org/ffx-script/chapter-viii-macalania/',"http://auronlu.istad.org/ffx-script/chapter-ix-bikanel-island/","http://auronlu.istad.org/ffx-script/chapter-x-bevelle/","http://auronlu.istad.org/ffx-script/chapter-xi-the-calm-lands/","http://auronlu.istad.org/ffx-script/chapter-xii-mt-gagazet/","http://auronlu.istad.org/ffx-script/chapter-xiii-zanarkand/",'http://auronlu.istad.org/ffx-script/chapter-xiv-mika-baaj-fayth/','http://auronlu.istad.org/ffx-script/chapter-xv-showdown-with-sin/']

extra = ["http://auronlu.istad.org/ffx-script/ffx-sidequests/","http://auronlu.istad.org/ffx-script/jecht-spheres-and-other-spheres/"]

pageNum = 0
for page in pages + extra:
	print(page)
	pageNum += 1
	fileName = "raw/page_"+str(pageNum).zfill(3)+".html"
	if not path.exists(fileName):
		html = urlopen(page).read().decode('utf-8')
		o = open(fileName,'w')
		o.write(html)
		o.close()
		time.sleep(2)


