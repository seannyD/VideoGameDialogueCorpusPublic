from urllib.request import *
from bs4 import BeautifulSoup
import re,time
from os import path

baseURL = 'https://hyouta.com/vesperia/'

def openPage(url):
	req = Request(
		url, 
		data=None, 
		headers={
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
		}
	)
	html = urlopen(req).read().decode('utf-8')
	return(html)

# MAIN STORY

mainStoryIndexURL = "https://hyouta.com/vesperia/?version=ps3p&locale=jp&compare=c2&section=scenario-index"
mainStoryIndexFileName = "raw/mainStoryIndex.txt"

if not path.exists(mainStoryIndexFileName):
	mainStoryIndexPage = openPage(mainStoryIndexURL)
	time.sleep(2)
	with open(mainStoryIndexFileName,'w') as wx:
		wx.write(mainStoryIndexPage)
else:
	mainStoryIndexPage = open(mainStoryIndexFileName).read()

soup = BeautifulSoup( mainStoryIndexPage, 'html5lib')

mainStoryIndexList = soup.find("div",{"class":"scenario-index"}, recursive=True)
mainStoryHREFs = mainStoryIndexList.find_all("a",recursive=True,href=True)
pnum = 1
for href in mainStoryHREFs:
	#print(href)
	hName = href['href']
	hName = hName[hName.index("name=")+5:].strip()
	print(hName)
	#fileName = "raw/page_"+str(pnum).zfill(5)+".html"
	fileName = "raw/page_"+ str(pnum).zfill(5)+"_"+ hName + ".html"
	if not path.exists(fileName):
		url = baseURL+href['href']
		page = openPage(url)
		time.sleep(2)
		with open(fileName, 'w') as fx:
			fx.write(page)
	pnum += 1

# SKITS
print("SKITS")

skitIndexURL = "https://hyouta.com/vesperia/?version=ps3p&locale=jp&compare=c2&section=skit-index"
skitIndexFileName = "raw/skitIndex.txt"
if not path.exists(skitIndexFileName):
	skitIndexPage = openPage(skitIndexURL)
	time.sleep(2)
	with open(skitIndexFileName,'w') as wx:
		wx.write(skitIndexPage)
else:
	skitIndexPage = open(skitIndexFileName).read()
	
	
soup = BeautifulSoup( skitIndexPage, 'html5lib')

skitTable = soup.find("div",{"id":"content"}).find("table").find("tbody")
skitIndexList = []
for row in skitTable.find_all("tr"):
	trs = row.find_all("td")
	rowType = trs[0].get_text()
	href = trs[2].find("a")['href']
	if not href in skitIndexList:
		if not href in mainStoryHREFs:
			skitIndexList.append(href)



print(len(skitIndexList))
pnum = 10000
for href in skitIndexList:
	hName = href
	hName = hName[hName.index("name=")+5:].strip()
	#fileName = "raw/page_"+str(pnum).zfill(5)+".html"
	fileName = "raw/page_Skit_"+ str(pnum).zfill(5) + "_" + hName +".html"
	print(fileName)
	if not path.exists(fileName):
		url = baseURL+href
		page = openPage(url)
		time.sleep(2)
		with open(fileName, 'w') as fx:
			fx.write(page)
	pnum += 1

		
# SIDEQUESTS
print("SIDEQUESTS")

sqURL = "https://hyouta.com/vesperia/?version=ps3p&locale=jp&compare=c2&section=sidequest-index"

sqIndexFileName = "raw/sqIndex.txt"
if not path.exists(sqIndexFileName):
	sqIndexPage = openPage(sqURL)
	time.sleep(2)
	with open(sqIndexFileName,'w') as wx:
		wx.write(sqIndexPage)
else:
	sqIndexPage = open(sqIndexFileName).read()
	
	
soup = BeautifulSoup( sqIndexPage, 'html5lib')

sqIndexList = soup.find("div",{"class":"scenario-index"}, recursive=True)
pnum = 20000
for href in sqIndexList.find_all("a",recursive=True,href=True):
	print(href)
	hName = href['href']
	hName = hName[hName.index("name=")+5:].strip()
	fileName = "raw/page_"+str(pnum).zfill(5) + "_"+ hName+".html"
	if not path.exists(fileName):
		url = baseURL+href['href']
		page = openPage(url)
		time.sleep(2)
		with open(fileName, 'w') as fx:
			fx.write(page)
	pnum += 1