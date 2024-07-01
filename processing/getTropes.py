# TODO: Morrowind isn't picking up all characters (e.g. Radd Hard-Heart?)
# https://tvtropes.org/pmwiki/pmwiki.php/Characters/TheElderScrollsIIIMorrowind
# Currently assuming one char per folder. Some pages have multiple characters per folder.

import os,sys,json,csv,time,re
from bs4 import BeautifulSoup

from urllib.request import *

gameFolders = [root+os.sep for root,dirs,files in os.walk("../data/") if "meta.json" in files]

# Allow parsing of just one game
if len(sys.argv)>1:
	fx = sys.argv[-1]
	if not fx.endswith(os.sep):
		fx += os.sep
	gameFolders = [fx]
	
def parseTropeSource(filepath):
	with open(filepath, 'r') as file:
		reader = csv.reader(file)
		header = None
		data = []
		for row in reader:
			if header is None:
				header = row
			else:
				dx = dict(zip(header,row))
				if "url" in dx and len(dx['url'])>0:
					data.append(dx)
	return(data)

def downloadTropePage(folder,url):
	print("Getting "+url)
	tropeFolder = folder
	if not tropeFolder.endswith("/"):
		tropeFolder += "/"
	tropeFolder += "raw/tropes/"
	if not os.path.isdir(tropeFolder):
		os.mkdir(tropeFolder)
	
	charFile = url
	if charFile.endswith("/"):
		charFile = charFile[:-1]
	charFile = tropeFolder + charFile[charFile.rindex("/")+1:] + ".csv"
	if not os.path.isfile(charFile):
		req = Request(
			url, 
			data=None, 
			headers={
				'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})
		html = urlopen(req).read().decode('utf-8')
		time.sleep(3)
		o = open(charFile,'w')
		o.write(html)
		o.close()
	return(charFile)
	
	
def cleanTropeNotes(t):
	t = re.sub('<a.+?href="(.+?)".*?>(.+?)</a>','[\\2](\\1)',t)
	if t.startswith("<li>"):
		t = t[4:]
	if t.endswith("</li>"):
		t = t[:-5]
	t = t.replace("<li>","\n-  ").replace("</li>","")
	t = t.replace('<span class="spoiler" title="you can set spoilers visible by default on your profile">',' (SPOILER) ')
	t = re.sub('<span.*?>',' ',t)
	t = t.replace('</span>',' ')
	t = t.replace('<div class="indent">',"\nQUOTE ")
	t = t.replace('</div>',"\n")
	t = t.replace("<strong>","**").replace("</strong>","**")
	t = t.replace("<br/>","\n")
	t = t.replace('<em>',"*").replace('</em>',"*")
	return(t)
	

def parseUL(ul,gameFolder,gameName,VGDCName="",TvTName=""):
	tropes = []
	for li in ul.find_all("li",recursive=False):
		firstLink = li.find("a", {"class":"twikilink"})
		if not firstLink is None:
			tropeName = firstLink.get_text()
			tropeURL = firstLink['href']
		else:
			tropeName = li.text.replace(".",":")+":"
			tropeName = tropeName[:tropeName.index(":")].strip()
			tropeURL = ""
		tropeName = tropeName.strip()
		#tropeNotes = li.get_text() # Just text
		tropeNotes = str(li) # Full HTML
		tropeNotes = cleanTropeNotes(tropeNotes)
		tnl = tropeNotes.lower()
		subverted = 0 + any([tnl.count(x)>0 for x in ["subvert","subversion"]])
		tropes.append([gameFolder,gameName,VGDCName,TvTName,tropeName,subverted,tropeNotes,tropeURL])
	return(tropes)
	
def parseMainCharacterTropePage(charFile,gameFolder,pageDetails):
	gameName = pageDetails["gameName"]
	VGDCName = pageDetails["VGDCName"]
	TvTName = pageDetails["TvTName"]
	with open(charFile) as o:
		html = o.read()
	soup = BeautifulSoup(html, "html5lib")
	mainArticle = soup.find("div",{"id": "main-article"})
	folders = mainArticle.find_all("div",{"class": "folder"})
	tropes = []
	for folder in folders:
		ul = folder.find("ul")
		if not ul is None:
			tropes += parseUL(ul, gameFolder,gameName,VGDCName,TvTName)
	return(tropes)
			
def parseMinorCharacterTropePage(charFile,gameFolder,pageDetails):
	# NPC pages with multiple characters
	gameName = pageDetails["gameName"]
	with open(charFile) as o:
		html = o.read()
	soup = BeautifulSoup(html, "html5lib")
	mainArticle = soup.find("div",{"id": "main-article"})
	# Find character folder
	# Some pages have multiple characters per folder.
	# And some have no wmglead within the folder class.
	# So iterate over items 
	currentCharName = ""
	tropes = []
	for item in mainArticle:
		if item.name == "div":
			if "folderlabel" in item["class"]:
				currentCharName = item.get_text().strip()
			elif "folder" in item["class"]:
				wmglead = item.find("div",{"class": "wmglead"})
				if not wmglead is None:
					currentCharName = wmglead.get_text().strip()
				for part in item:
					if part.name == "h2":
						currentCharName = part.get_text().strip()
					elif part.name == "ul":
						tropes += parseUL(part, gameFolder,gameName,currentCharName,currentCharName)
	
	return(tropes)
	
def autoMapCharNames(tropes, gameCharGroups):
	VGDCCharNames = []
	for group in gameCharGroups:
		VGDCCharNames += gameCharGroups[group]
	VGDCCharNames = list(set(VGDCCharNames))
	
	header = tropes[0]
	
	# Skip first line of tropes object, because it's a header
	allTvTCharNames = list(set([x[header.index("TvTName")] for x in tropes[1:]]))
	allTvTCharNames = [x.strip() for x in allTvTCharNames if len(x.strip())>0]
	TvT_to_VGDC = {}
	for TvTName in allTvTCharNames:
		if TvTName in VGDCCharNames:
			TvT_to_VGDC[TvTName] = TvTName
		else:
			# remove "Dr."
			if TvTName.count("Dr.")>0:
				x = TvTName.replace("Dr.","").strip()
				if x in VGDCCharNames:
					print(TvTName + " -> " + x)
					TvT_to_VGDC[TvTName] = x
					break
			elif len(TvTName) > 6 and all([TvTName.count(x)==0 for x in ["&"," and ","'s "]]):
				# (avoid multiple chars and posessives like "Johnny's parents")
				# "Ambassador Donnel Udina" -> "Donnel Udina",
				# TODO: really, this should split by names and find overlaps
				# But either may confuse people with the same surname?
				candidates = [x for x in VGDCCharNames if TvTName.count(x)>0]
				candidates = sorted(candidates, key=len,reverse=True)
				filterGenericNames = ["Guard","Girl","Boy","Man","Woman","Captain",
										"Princess", "Prince", "King", "Queen", "Chocobo",
										"Soldier", "Judge", "Shepard", "Mother", "Father", "Child"]
				candidates = [x for x in candidates if not x in filterGenericNames]
				if len(candidates)>0:
					print(TvTName + " -> " + candidates[0])
					TvT_to_VGDC[TvTName] = candidates[0]
	
	# Make replacements
	for trope in tropes:
		TvTName = trope[header.index("TvTName")]
		if TvTName in TvT_to_VGDC:
			trope[header.index("VGDCName")] = TvT_to_VGDC[TvTName]
	
	return(tropes)

# These are game folders
for gameFolder in gameFolders:
	# Check if we have a tropesource file
	tropeSourcePath = gameFolder+"tropeSources.csv"
	if os.path.isfile(tropeSourcePath):
		print("\n\n\n\n")
		print(gameFolder)
		with open(gameFolder+"meta.json") as json_file:
			meta = json.load(json_file)
		gameName = meta["game"]
		tropes = [["folder","game","VGDCName","TvTName","tropeName","subverted","tropeNotes","tropeURL"]]
		d = parseTropeSource(tropeSourcePath)
		for page in d:
			page["gameName"] = gameName
			pageFilepath = downloadTropePage(gameFolder,page["url"])
			if page["type"]=="main":
				tropes += parseMainCharacterTropePage(pageFilepath,gameFolder,page)
			elif page["type"]=="minor":
				tropes += parseMinorCharacterTropePage(pageFilepath,gameFolder,page)
		
		# Attempt to automatically map character names
		tropes = autoMapCharNames(tropes, meta["characterGroups"])
		
		# Change character names
		charMapFile = gameFolder+"tropeCharMap.json"
		if not os.path.isfile(charMapFile):
			# No char map file yet - let's make a template
			gameCharNames = []
			for group in meta["characterGroups"]:
				gameCharNames += meta["characterGroups"][group]
		
			charMap = {}
			if len(tropes)>1:
				for trope in tropes[1:]:
					VGDCName = trope[2]
					TvTName = trope[3]
					if not VGDCName in gameCharNames:
						VGDCName = "!"+VGDCName
					if TvTName != VGDCName:
						charMap[TvTName] = VGDCName
				json_object = json.dumps(charMap, indent=4)
				with open(charMapFile,'w') as o:
					o.write(json_object)
		else:
			# Load a char map and apply the changes
			with open(charMapFile) as json_file:
				charMap = json.load(json_file)
			for trope in tropes[1:]:
				TvTName = trope[3]
				if TvTName in charMap:
					VGDCName = charMap[TvTName]
					if not VGDCName.startswith("!"):
						trope[2] = VGDCName
		
		# Write the data	
		with open(gameFolder+"tropeData.csv","w") as o:
			csvwriter = csv.writer(o)
			csvwriter.writerows(tropes)
		