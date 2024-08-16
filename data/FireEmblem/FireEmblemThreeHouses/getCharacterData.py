from urllib.request import *
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import re,time
import os
import json

cardImageEmotions = {
	"1": "neutral",
	"2": "happy",
	"3": "angry",
	"4": "sad",
	"5": "shock",
	"6": "shy",
	"7": "special1", # wink?
	"8": "special2",
	"9": "special3", # wry?
	"10": "special4", 
	"11": "special5"
}

# TODO: get aliases, e.g. Edelgard changes: https://houses.fedatamine.com/en-uk/characters/2/Edelgard/gallery


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
	
def getPage(url,fileName):
	page = None
	if not os.path.exists(fileName):
		page = openPage(url)
		time.sleep(1)
		with open(fileName, "w") as file:
			file.write(str(page))
	else:
		page = open(fileName).read()
		page = BeautifulSoup(page, 'lxml')
		page = page.find("main")
	return(page)
	
# get list of all characters
# data = json.load(open("data.json"))["text"]
# def walkData(lines):
# 	out = []
# 	for line in lines:
# 		if "CHOICE" in line:
# 			for choice in line["CHOICE"]:
# 				out += [x for x in walkData(choice)]
# 		else:
# 			charName = [x for x in line if not x.startswith("_")][0]
# 			if not charName in out:
# 				out.append(charName)
# 	out = list(set(out))
# 	return(out)
	
charIndexURL = "https://houses.fedatamine.com/en-uk/characters/"
charIndex = openPage(charIndexURL)
charPages = [x["href"] for x in charIndex.find_all("a") if x["href"].startswith("/en-uk/characters/") and x!="/en-uk/characters/"]

charPages = list(set(charPages))

charDetails = {}
imageIndex = {}
for charPage in charPages:
	url = "https://houses.fedatamine.com" + charPage
	fileName = "raw/en-uk/characters/"+charPage.replace("/","_")+".html"
	print(url)
	page = getPage(url,fileName)
	
	charName = page.find("h1").get_text().strip()
	charNumber = charPage[charPage.rindex("/")+1:].strip()
	
	details = page.find("div",{"class":"col-md-4"})
	detailHeadings = [x.get_text().strip() for x in details.find_all("strong")]
	detailData = [x.get_text().strip() for x in details.find_all("p")]
	detailsDict = dict(zip(detailHeadings,detailData))
	detailsDict["charNumber"] = charNumber
	detailsDict["fullName"] = charName

	charShortName = charName
	
	galleryURL = [x["href"] for x in page.find_all("a") if x['href'].endswith("/gallery")]
	if len(galleryURL)>0:
		galleryURL = galleryURL[0]
		galleryFullURL = "https://houses.fedatamine.com" + galleryURL
		galleryFileName = "raw/en-uk/characters/"+galleryURL.replace("/","_")+".html"
		print(galleryURL)
		galleryPage = getPage(galleryFullURL,galleryFileName)
		
		charShortName = galleryURL.split("/")[-2].replace("%20"," ")
		
		cards = galleryPage.find_all("div",{"class":"card"})
		for card in cards:
			cardImg = card.find("img")["src"]
			cardImg = cardImg.replace("https://assets.fedatamine.com/3h/","")
			print(cardImg)
			cardTitleDiv = card.find("div",{"class":"card-body"})
			cardTitle = cardTitleDiv.get_text().strip()
			cardEmotion = ""
			if cardTitle.count("#")>0:
				emotionNumber = cardTitle[cardTitle.index("#")+1:].strip()
				emotionNumber = emotionNumber.replace("(Sunlight)","").strip()
				cardEmotion = cardImageEmotions[emotionNumber]
			part = "I"
			if "Part II" in cardTitle:
				part = "II"
			imageIndex[cardImg] = {"charShortName":charShortName, 
									"part":part,
									"emot":cardEmotion}
	# Some characters are double-listed in the DLC
	if not charShortName in charDetails:
		charDetails[charShortName] = detailsDict
	else:
		for k in detailsDict:
			if not k in charDetails[charShortName]:
				charDetails[charShortName][k] = detailsDict[k]
			
with open('charDetails.json', 'w', encoding='utf-8') as f:
	json.dump(charDetails, f, ensure_ascii=False, indent=4)
with open('charImageDetails.json', 'w', encoding='utf-8') as f:
	json.dump(imageIndex, f, ensure_ascii=False, indent=4)
		

# Create gender json
groups = {}
for charShortName in charDetails:
	if "Gender" in charDetails[charShortName]:
		g = charDetails[charShortName]["Gender"]
		if not g.lower() in groups:
			groups[g.lower()] = []
		groups[g.lower()].append(charShortName)
		
with open('charAutoGender.json', 'w', encoding='utf-8') as f:
	json.dump(groups, f, ensure_ascii=False, indent=4)