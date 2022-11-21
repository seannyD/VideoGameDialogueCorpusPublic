from urllib.request import urlopen
import time


# test: https://ffxiv.gamerescape.com/wiki/A_Final_Temptation#Dialogue


pages = ["https://thelifestream.net/final-fantasy-xv-lore/final-fantasy-xv-chapter-by-chapter-lore-exposition-and-development/final-fantasy-xv-chapter-by-chapter-lore-exposition-and-development-part-1/","https://thelifestream.net/final-fantasy-xv-lore/final-fantasy-xv-chapter-by-chapter-lore-exposition-and-development/final-fantasy-xv-chapter-by-chapter-lore-exposition-and-development-part-2/","https://thelifestream.net/final-fantasy-xv-lore/final-fantasy-xv-chapter-by-chapter-lore-exposition-and-development/final-fantasy-xv-chapter-by-chapter-lore-exposition-and-development-part-3/","https://thelifestream.net/final-fantasy-xv-lore/final-fantasy-xv-chapter-by-chapter-lore-exposition-and-development/final-fantasy-xv-chapter-by-chapter-lore-exposition-and-development-part-4/"]
pageNum = 0
for page in pages:
	pageNum += 1
	html = urlopen(page).read().decode('utf-8')
	print(page)
	fileName = "raw/page_"+str(pageNum).zfill(3)+".html"
	o = open(fileName,'w')
	o.write(html)
	o.close()
	time.sleep(2)
