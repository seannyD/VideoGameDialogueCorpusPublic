# The https://ffxiv.gamerescape.com wiki has quest logs 
#  for Main Scenario Quests listed on a category page.
#  Load the category pages, then download each link within it.

from urllib.request import *
import time
from os import path
import re

from bs4 import BeautifulSoup

def loadPage(page):
	req = Request(
		page, 
		data=None, 
		headers={
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
		}
	)

	html = urlopen(req).read().decode('utf-8')
	return(html)


# test: https://ffxiv.gamerescape.com/wiki/A_Final_Temptation#Dialogue

base = "https://ffxiv.gamerescape.com"
# downloaded view-source:https://ffxiv.gamerescape.com/wiki/Category:Main_Scenario_Quest

indexPages = [
	"https://ffxiv.gamerescape.com/wiki/Category:Main_Scenario_Quest",
	"https://ffxiv.gamerescape.com/w/index.php?title=Category:Main_Scenario_Quests&pagefrom=Devourer+of+Worlds#mw-pages",
	"https://ffxiv.gamerescape.com/w/index.php?title=Category:Main_Scenario_Quests&pagefrom=Migrant+Marauders#mw-pages",
	"https://ffxiv.gamerescape.com/w/index.php?title=Category:Main_Scenario_Quests&pagefrom=The+Key+to+Victory#mw-pages"]


# Save all category pages to single index file
if not path.exists("raw/indexPage.txt"):
	print("Downloading index pages ...")
	iText= ""
	for iPage in indexPages:
		iText += loadPage(iPage)
		time.sleep(2)
	o = open("raw/indexPage.txt",'w')
	o.write(iText)
	o.close()

# Open index page
o = open("raw/indexPage.txt")
categoryPage = o.read()
o.close()

catSoup = BeautifulSoup(categoryPage, "html.parser")
catSoup = catSoup.find_all("div",{"id":"mw-pages"})
catSoup = "\n".join([str(x) for x in catSoup])

pages = re.findall('href="(/wiki/.+?)"',catSoup)
pages = list(set(pages))

for page in pages:
	print(page)
	fileName = "raw/page_"+page.replace("/","#")+".html"
	if not path.exists(fileName):
		html = loadPage(base+page)
		time.sleep(3)
		dialogue = ""
		if html.count('class="bubble"')>0:
			soup = BeautifulSoup(html, 'html.parser')	
			dialogue = soup.find("div", {"id":"mw-content-text"})
		# Write the file no matter what, so we know we processed it
		o = open(fileName,'w')
		o.write(str(dialogue))
		o.close()
		
