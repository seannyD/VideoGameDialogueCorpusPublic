from urllib.request import urlopen
from bs4 import BeautifulSoup
import time

page = "https://game-scripts.fandom.com/wiki/Horizon_Zero_Dawn"
#html = urlopen(page).read().decode('utf-8')
#time.sleep(2)
#o = open("raw/page01.html",'w')
#o.write(html)
#o.close()


# Datapoints

#indexpage = "https://horizon.fandom.com/wiki/Datapoints"
# Updated index page since Horizon Forbidden West
#  This is untested, and includes links to the Frozen Wilds DLC
indexpage = "https://horizon.fandom.com/wiki/List_of_datapoints_in_Horizon_Zero_Dawn"

html = urlopen(indexpage).read().decode('utf-8')
time.sleep(2)

soup = BeautifulSoup(html,'html5lib')
content = soup.find("div",{"class":"mw-parser-output"})

ols = content.findAll("ol", recursive=True)

startPos = '<span class="mw-headline" id="Content">Content</span>'
endPos = '<i>Horizon Zero Dawn</i> Datapoints'


# (only audio and hologram)
pcount = 2
for ol in ols[:2]:
	links = ol.find_all("a")
	for link in links:
		url = "https://horizon.fandom.com" + link["href"]
		t = link["title"]
		print("Extracting datapoint "+t)
		datapointContent = urlopen(url).read().decode("utf-8")
		time.sleep(2)
		
		toSave = "DATAPOINT\t"+t.strip()+"\n"+datapointContent[datapointContent.index(startPos):datapointContent.index(endPos)]
		o = open("raw/page"+"{:02d}".format(pcount)+".html",'w')
		o.write(toSave)
		o.close()
		pcount += 1
