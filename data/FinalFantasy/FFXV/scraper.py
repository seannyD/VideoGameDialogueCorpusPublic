from urllib.request import *
import time


# test: https://ffxiv.gamerescape.com/wiki/A_Final_Temptation#Dialogue

def getPage(url):
	req = Request(
		page, 
		headers={
			'User-Agent': 'XYZ/3.0'
		}
	)

	html = urlopen(req, timeout=10).read().decode('utf-8')
	return(html)

pages = ["https://thelifestream.net/final-fantasy-xv-lore/final-fantasy-xv-chapter-by-chapter-lore-exposition-and-development/final-fantasy-xv-chapter-by-chapter-lore-exposition-and-development-part-1/","https://thelifestream.net/final-fantasy-xv-lore/final-fantasy-xv-chapter-by-chapter-lore-exposition-and-development/final-fantasy-xv-chapter-by-chapter-lore-exposition-and-development-part-2/","https://thelifestream.net/final-fantasy-xv-lore/final-fantasy-xv-chapter-by-chapter-lore-exposition-and-development/final-fantasy-xv-chapter-by-chapter-lore-exposition-and-development-part-3/","https://thelifestream.net/final-fantasy-xv-lore/final-fantasy-xv-chapter-by-chapter-lore-exposition-and-development/final-fantasy-xv-chapter-by-chapter-lore-exposition-and-development-part-4/"]
pageNum = 0
print("  downloading pages ...")
for page in pages:
	pageNum += 1
	print(page)
	#html = urlopen(page).read().decode('utf-8')
	html = getPage(page)
	fileName = "raw/page_"+str(pageNum).zfill(3)+".html"
	o = open(fileName,'w')
	o.write(html)
	o.close()
	time.sleep(2)
