from urllib.request import *
from bs4 import BeautifulSoup, NavigableString, Tag
import csv, re, time, os

page = "https://masseffect.fandom.com/wiki/Morality_Guide"
baseURL = "https://masseffect.fandom.com"
tmpFolder = "raw/morality/"

if not os.path.isdir(tmpFolder):
	os.mkdir(tmpFolder)

def getGender(page):
	print("Requesting ... " + page)
	fileName = tmpFolder + page[page.rindex("/")+1:] + ".html"
	if not os.path.isfile(fileName):
		req = Request(baseURL + page, data=None, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})
		html = urlopen(req).read()
		time.sleep(2)
		o = open(fileName,'wb')
		o.write(html)
		o.close()
	o = open(fileName)
	html = o.read()
	o.close()
	html = BeautifulSoup(html, 'html5lib')
	genderRow = html.find("div",attrs={"data-source":"gender"})
	if not genderRow is None:
		genderText = genderRow.find("div").get_text()
		genderText = genderText.lower().strip()
		if len(genderText)>0:
			print("   Success: "+genderText)
			return(genderText)
	return("")


mainPageFile = "raw/morality/MainPage.html"
if not os.path.isfile(mainPageFile):
	req = Request(page, data=None, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})
	html = urlopen(req).read()#.decode('cp1252').encode('utf-8')#.decode('ISO-8859-1')
	time.sleep(2)
	o = open(mainPageFile,'wb')
	o.write(html)
	o.close()

html = open(mainPageFile).read()
html = html[:html.index('<span class="mw-headline" id="Total_Possible">Total Possible</span>')]
soup = BeautifulSoup(html, 'html5lib')

data = soup.find("div",{"class":"mw-parser-output"})

currentChar = ""
genderLinks = []
skipNext = False

paragonMatcher = re.compile("([0-9]+) ?Paragon")
renegadeMatcher = re.compile("([0-9]+) ?Renegade")

out = [["Mission","Character","AutoGender","ShepardGender","Paragon","Renegade","Text"]]

started = False
for child in data:
	if child.name=="h2":
		mission = child.get_text()
		genderLinks = []
		started = True
	if started:
		if child.name == "p" or child.name=="h3":
			links = child.find_all("a")
			genderLinks = []
			for link in links:
				#try:
					gender = getGender(link.get("href"))
					genderLinks.append(link.get_text() + "::" + gender)
				#except:
				#	pass
			currentChar = child.get_text()
		elif child.name == "dl":
			genderLinks = []
			if child.get_text().count("Total")>0:
				skipNext = True
		elif child.name=="ul":
			if not skipNext:
				bits = child.find_all("li")
				for bit in bits:
					bitTxt = bit.get_text()
					paragon = ""
					renegade = ""
					par = paragonMatcher.search(bitTxt)
					if not par is None and  len(par.groups())>0:
						paragon = par.group(1)
					ren = renegadeMatcher.search(bitTxt)
					if not ren is None and len(ren.groups())>0:
						renegade = ren.group(1)
					shepGenderCondition = ""
					if bitTxt.lower().count("if shepard is female")>0:
						shepGenderCondition = "female"
					if bitTxt.count("if shepard is male")>0:
						shepGenderCondition = "male"
					genderOut = "; ".join(genderLinks)
					out.append([mission,currentChar,genderOut,shepGenderCondition,paragon,renegade,bit.get_text()])
			skipNext = False
		
with open('conversationRewards.csv', 'w', encoding='UTF8') as f:
	writer = csv.writer(f)
	writer.writerows(out)