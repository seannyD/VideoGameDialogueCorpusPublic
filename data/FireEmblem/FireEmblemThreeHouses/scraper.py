from urllib.request import *
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import re,time
import os


def openPage(url):
	req = Request(
		url, 
		data=None, 
		headers={
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
		}
	)
	html = urlopen(req).read().decode('utf-8')
	html = BeautifulSoup(html, 'lxml')
	html = html.find("main")
	return(html)
	


# Dummy file for parser
with open("raw/dummyFile.html", "w") as file:
	file.write("dummy")

# Download scenarios
baseURL = "https://houses.fedatamine.com/en-uk/"
rawFolder = "raw/en-uk/"

pageCategories = [("scenarios",370),("monastery",84)]

for cat,maxi in pageCategories:
	folder = rawFolder + cat+"/"
	if not os.path.exists(folder):
		os.mkdir(folder)
	for i in range(maxi):
		fileName = folder + str(i)+".html"
		print(fileName)
		if not os.path.exists(fileName):
			pageURL = baseURL + cat + "/"+ str(i)
			try:
				data = openPage(pageURL)
				with open(fileName, "w") as file:
					file.write(str(data))
			except HTTPError:
				print("ERROR " + pageURL)
				with open(fileName, "w") as file:
					file.write("")				
			time.sleep(2)
	
# Support conversations
allLinks = []
supportLinksFile = "raw/en-uk/links/supportLinks.txt"
if not os.path.exists(supportLinksFile):
	supportIndex = openPage("https://houses.fedatamine.com/en-uk/supports/")
	links = supportIndex.find_all("a")
	links = [x["href"] for x in links if x["href"].startswith("/en-uk/supports/")]
	links = list(set(links))

	allLinks = []
	for link in links:
		html = ""
		blinkFileName = "raw/en-uk/links/"+link.replace("/","_")[1:]
		if os.path.exists(blinkFileName):
			p = open(blinkFileName).read()
			linkIndex = BeautifulSoup(p, 'lxml')
			linkIndex = linkIndex.find("main")
		else:
			print("https://houses.fedatamine.com" + link)
			linkIndex = openPage("https://houses.fedatamine.com" + link)
			time.sleep(2)
			with open(blinkFileName, "w") as file:
				file.write(str(linkIndex))				
		bLinks= linkIndex.find_all("a")
		allLinks += [x["href"] for x in bLinks if x["href"].startswith("/en-uk/supports/")]
	allLinks = list(set(allLinks))
	with open(supportLinksFile, "w") as file:
		file.write("\n".join(allLinks))
else:
	allLinks = open(supportLinksFile).read().split("\n")

print("Downloading support pages")
for link in allLinks:
	fileName = "raw/en-uk/supports/"+link.replace("/","_")[1:]+".html"
	if not os.path.exists(fileName):
		print(link)
		supportPage = openPage("https://houses.fedatamine.com" + link)
		time.sleep(1)
		with open(fileName, "w") as file:
			file.write(str(supportPage))	

# Battles
battleIndexURL = "https://houses.fedatamine.com/en-uk/battles/"
battleIndex = openPage(battleIndexURL)
battleLinks = [x['href'] for x in battleIndex.find_all("a") if x['href'].startswith("/en-uk/battles/")]

print("Downloading battle pages")
for link in battleLinks:
	battleFileName = "raw/en-uk/battles/"+link.replace("/","_")[1:]+".html"
	battlePage = None
	if not os.path.exists(battleFileName):
		print("https://houses.fedatamine.com" + link)
		battlePage = openPage("https://houses.fedatamine.com" + link)
		time.sleep(2)
		with open(battleFileName, "w") as file:
			file.write(str(battlePage))				
	

# Tea (part of the character sheet)
# (to get this info, we need to know the character name and number)
# (and only for main characters, not "Speaking NPCs")
# (this info is already downloaded in the 'characters' folder, but we need to filter out the speaking NPCs)
print("Downloading Tea")
charIndexURL = "https://houses.fedatamine.com/en-uk/characters/"
charIndex = openPage(charIndexURL)
charIndex.find("div", {"id":"group-0-5"}).extract()
charPages = [x["href"] for x in charIndex.find_all("a") if x["href"].startswith("/en-uk/characters/") and x!="/en-uk/characters/"]

charPages = list(set(charPages))
mainCharNumbers = [x.replace("/en-uk/characters/","") for x in charPages]

if not os.path.isdir("raw/en-uk/tea/"):
	os.mkdir("raw/en-uk/tea/")
	
charAndNumbers = os.listdir("raw/en-uk/characters/")
charAndNumbers = [x for x in charAndNumbers if x.endswith("_gallery.html")]
charAndNumbers = [x.split("_")[3:5] for x in charAndNumbers]
charAndNumbers = [x for x in charAndNumbers if x[0] in mainCharNumbers]
charAndNumbers = [x for x in charAndNumbers if x[1]!="Byleth"]


for charNumber,charName in charAndNumbers:
	teaPageURL = "https://houses.fedatamine.com/en-uk/characters/" + charNumber + "/" + charName + "/activities/tea"
	fileName = "raw/en-uk/tea/"+charNumber + "_" + charName+".html"
	if not os.path.exists(fileName):
		print(teaPageURL)
		teaPage = openPage(teaPageURL)
		time.sleep(2)
		with open(fileName, "w") as file:
			file.write(str(teaPage))		

# We also need to know which lines are the 'good' choices, which
#  only exists in another site:

sfSiteBase = "https://serenesforest.net/three-houses/monastery/tea-party/"

for charNumber,charName in charAndNumbers:
	fileName = "raw/en-uk/tea/"+charNumber + "_" + charName+"_FinalComments.html"
	if not os.path.exists(fileName):
		teaPageURL = sfSiteBase+charName.lower()+"/"
		print(teaPageURL)
		req = Request(
			teaPageURL, 
			data=None, 
			headers={
				'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
			}
		)
		time.sleep(2)
		html = urlopen(req).read().decode('utf-8')
		html = BeautifulSoup(html, 'lxml')
		html = html.find("div",{"class":"entry"})

		with open(fileName, "w") as file:
			file.write(str(html))		