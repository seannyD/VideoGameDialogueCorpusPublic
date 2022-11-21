import re, time, os
from bs4 import BeautifulSoup
from urllib.request import urlopen

indexPage = "https://lparchive.org/Persona-4/"

html = urlopen(indexPage).read().decode('utf-8')
time.sleep(3)
pageLinks = re.findall('href="(Update.+?)"',html)

pageLinksUnique = []
for p in pageLinks:
	if not p in pageLinksUnique:
		pageLinksUnique.append(p)
	# Don't capture info entries
	if p == "Update%20106/":
		break

pageLinksUnique += ["Update%20108/","Update%20109/"]

pageNum = 1
for pageLink in pageLinksUnique:
	filename = "raw/page" + str(pageNum).zfill(3)+".html"
	if not os.path.isfile(filename):
		url = indexPage+pageLink
		html = urlopen(url).read().decode('utf-8')
		time.sleep(2)
	
		soup = BeautifulSoup( html, "html5lib")
		cont = soup.find("div",{"id":"content"})
		towrite = pageLink + "\n" + str(cont)
	
		o = open(filename,'w')
		o.write(towrite)
		o.close()
	pageNum += 1
