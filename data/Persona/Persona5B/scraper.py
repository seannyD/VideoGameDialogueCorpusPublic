import re, time
from bs4 import BeautifulSoup
from urllib.request import urlopen


avoidPages = ["https://lparchive.org/Persona-5/Update%20113/", "https://lparchive.org/Persona-5/Update%20114/",
"https://lparchive.org/Persona-5/Update%20115/"]

indexPage = "https://lparchive.org/Persona-5/"

html = urlopen(indexPage).read().decode('utf-8')
time.sleep(3)
pageLinks = re.findall('href="(Update.+?)"',html)

pageLinksUnique = []
for p in pageLinks:
	if not p in pageLinksUnique:
		pageLinksUnique.append(p)

pageNum = 1
for pageLink in pageLinksUnique:
	filename = "raw/page" + str(pageNum).zfill(3)+".html"
	url = "https://lparchive.org/Persona-5/"+pageLink
	if not url in avoidPages:
		html = urlopen(url).read().decode('utf-8')
		time.sleep(2)
	
		soup = BeautifulSoup( html, "html5lib")
		cont = soup.find("div",{"id":"content"})
		towrite = pageLink + "\n" + str(cont)
	
		o = open(filename,'w')
		o.write(towrite)
		o.close()
		pageNum += 1
