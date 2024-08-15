from bs4 import BeautifulSoup,Tag, NavigableString
import json
import re
import xlrd
import copy
import os

# https://houses.fedatamine.com/en-uk/scenarios/1
# https://houses.fedatamine.com/en-us/monastery/0
	# In this, some choices are duplicated

# TODO: Choice is not unpacking
	

# Functions for human sorting	
def tryint(s):
    try:
        return int(s)
    except ValueError:
        return s

def alphanum_key(s):
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]
	
def cleanDialogue(txt):
	txt = txt.replace("\n"," ")
	txt = re.sub(" +"," ",txt)
	return(txt)
	
def parsePage(html,lang="en-uk",idprefix=""):
	global seenSubsections
	seenSubsections = []
	
	out = []
	scenarioTitle = html.find("h1").get_text()
	out.append({"LOCATION":scenarioTitle})
	
	sections = html.find_all(["div","h3"],recursive=False)
	for section in sections:
		if not (section.has_attr("class") and "row" in section["class"]):
			ret = parseSection2(section)
			if not ret is None:
				if type(ret) == list:
					out += ret
				else:
					out.append(ret)
			if len(out) > 0 and out[-1] != {"ACTION": "---"}:
				out.append({"ACTION": "---"})
	return(out)
		
		
def parseSection2(section):
	# Iterate over subsections
	#  (event, event base or tab group)
	# but doesn't really matter?
	out = []
	for subsection in section.findChildren(recursive=False):
		ret = parseSubsection2(subsection)
		if not ret is None:
			if not ret in seenSubsections:
				seenSubsections.append(ret)
				if type(ret) == list:
					out += ret
				else:
					out.append(ret)
			#if len(out) > 0 and out[-1] != {"ACTION": "---"}:
			#	out.append({"ACTION": "---"})
	return(out)
		
def parseSubsection2(subsection):
	global seenSubsections
	# <a>, <div py-2>, <div event-notification> etc.
		
	if isinstance(subsection,NavigableString):
		return(None)
		
	if subsection.name == "h3":
		return([{"LOCATION": subsection.get_text().strip()}])
		
	out = []
	i =0
	subsection = [x for x in subsection.findChildren(recursive=False)];
	while i<len(subsection):
		part = subsection[i]
		if type(part) == str:
			pass
		elif part.has_attr("class") and "py-2" in part["class"]:
			ret = parsePy2(part)
			if not ret is None:
				out.append(ret)
		elif isTabGroup(part):
			ret = parseSubsection2(part)
			if not ret is None:
				out.append(ret)
		elif part.has_attr("class") and "event-notification" in part["class"]:
			out.append({"ACTION": cleanDialogue(part.get_text())})
		elif part.name == "ul":
			options = part.find_all("li")
			responseDiv = subsection[i+1]
			choices = parseDecisions2(options,responseDiv)
			out.append(choices)
			i += 1 # Skip next div
		i += 1	
	return(out)

	

def isEvent(div):
	if not "id" in event.attrs:
		return(False)
	return(event.attrs['id'].startswith("event"))

def isTabGroup(div):
	if not div.has_attr("class"):
		return(False)
	return(any([x.startswith("tab-group") for x in div.attrs["class"]]))
	
def isEventBase(div):
	if not div.has_attr("id"):
		return(False)
	return(div.attrs['id'].startswith("event-base"))

def isActionEvent(mainDiv):
	x = mainDiv.find("div")
	if x is None:
		return(False)
	return(x.has_attr("class") and "event-notification" in x.get("class"))
	
def isSupportEvent(mainDiv):
	subDiv = mainDiv.find("div")
	if subDiv is None:
		return(False)
	if not subDiv.has_attr("class"):
		return(False)
	return(any([x in subDiv.attrs["class"] for x in ["negative-background","positive-background"]]))

def isQuestEvent(mainDiv):
	return(mainDiv.get_text().count("Quest")>0)
	
def isCenterDiv(mainDiv):
	return(mainDiv.has_attr("class") and "text-center" in mainDiv.get("class"))

def isBylethDiv(mainDiv):
	return(mainDiv.has_attr("class") and "byleth-text" in mainDiv.get("class"))
	
def isLetter(mainDiv):
	return(mainDiv.has_attr("class") and "text-light" in mainDiv.get("class"))
	
def isNoteDiv(mainDiv):
	elems = [x.name for x in mainDiv if not x.name is None]
	return(elems == ["p"] or elems == ["strong"])
	
#def isWarning(mainDiv):
#	return(mainDiv.has_attr("class") and "alert-warning" in mainDiv.get("class"))

def parsePy2(mainDiv):
	if mainDiv is None:
		return(None)
		
	#print("____")
	#print(mainDiv)	
	if isActionEvent(mainDiv):
		return({"ACTION": mainDiv.get_text()})
	elif isSupportEvent(mainDiv):
		supportText = mainDiv.get_text().strip()
		if supportText == "":
			if "positive-background" in mainDiv["class"]:
				supportText = "Gain Support"
			else:
				supportText = "Lose Support"
		return({"ACTION": supportText,"_sup":"Y"})
	elif mainDiv.get_text().strip() == "link":
		return(None)
	#elif mainDiv.name == "ul":
	#	choices = [{"PC":cleanDialogue(x.get_text())} for x in mainDiv.find_all("li")]
	#	return({"CHOICE":choices})
	#elif mainDiv.has_attr("class") and "tab-content" in mainDiv["class"]:
	#	pass
	elif isQuestEvent(mainDiv):
		return({"ACTION": "QUEST: "+mainDiv.get_text().strip()})
	elif isNoteDiv(mainDiv):
		return({"ACTION": "NOTE: " + mainDiv.get_text().strip()})
	else:


		dialogueDiv = mainDiv.find("div",{"class":"px-3"})
		charName = ""
		dialogue = ""
		if dialogueDiv is None:
			charName = "PC"
			dialogue = mainDiv.find("div",{"class":"byleth-text"})
			if dialogue is None:
				dialogue = mainDiv
		else:
			charA = dialogueDiv.find("a")
			charName = charA.get_text()
			dialogue = dialogueDiv.find_all("p",recursive = False)
		# Sometimes dialogue is inside p, sometimes it's a raw text
		if len(dialogue)==0:
			dialogue = dialogueDiv.find_all(text = True, recursive = False)
		dialogue = " ".join([x.get_text() for x in dialogue]).strip()
		dialogue = cleanDialogue(dialogue)
		ret = {charName: dialogue}
		
		# Add other information
		if False:
			im = mainDiv.find("img")
			imsrc = im["src"]
			if imsrc.startswith("https://assets.fedatamine.com/3h/face_school/"):
				imsrc = imsrc[45:]
			ret["img"] = imsrc
			listen = mainDiv.find("div",{"class":"listen"})
			if not listen is None:
				audio = listen["data-key"]
				ret["audio"] = audio
		return(ret)
	
def parseDecisions2(options,responseDiv):
	optionCode = [x.find("a")["href"].replace("#","") for x in options]
	optionDict = dict(zip(optionCode,[x.get_text() for x in options]))

	responseGroups = responseDiv.find_all("div", recursive = False)
	responseGroupCodes = [x["id"] for x in responseGroups]
	responseGroupDict = dict(zip(responseGroupCodes,responseGroups))

	choices = []
	for opCode in optionDict:
		choice = [{"PC": optionDict[opCode]}]
		# TODO: recursion?
		subsections = responseGroupDict[opCode]
		for subsection in subsections:
			parsedSubsection = None
			if isinstance(subsection,NavigableString):
				parsedSubsection = None
			elif subsection.has_attr("class") and "py-2" in subsection["class"]:
				parsedSubsection = parsePy2(subsection)		
			else:
				parsedSubsection = parseSubsection2(subsection)					
			if not parsedSubsection is None:
				if type(parsedSubsection) == list:
					choice += parsedSubsection
				else:
					choice.append(parsedSubsection)
				
		choice = [cx for cx in choice if not cx is None]
		if len(choice)>0:
			choices.append(choice)
	out = {"CHOICE":choices}
	return(out)	
		
	
def parseCenterDiv(div):
	img = div.find("img")
	if not img is None:
		return({"ACTION": "IMG: "+img["src"]})

	# Never get here?
	spans = div.find("span",{"class":"support-change-text"})
	if not spans is None:
		return({"ACTION": "SUPPORT: "+div.get_text().strip()})

	#print("ERROR")
	#print(div)
	return(None)
	

def parseFile(fileName,parameters={},asJSON=False):
	# The raw files are grouped by type within subfolders
	# so there's just one dummy file and the parseFile function
	# loops through the subfolder contents
	
	out = []
	rawFolderPath = fileName[:fileName.rindex("/")]
	langs = ["en-uk"]
	for lang in langs:
		folders = ["scenarios","monastery"]
		for folder in folders:
			out.append({"LOCATION":"FOLDER: "+folder})
			folderPath = rawFolderPath+"/"+lang+"/"+folder+"/"
			htmlFiles = [x for x in os.listdir(folderPath) if x.endswith('html')]
		
			# TODO: Sort by actual number
			htmlFiles.sort(key=alphanum_key)
			for htmlFile in htmlFiles:
				o = open(folderPath+htmlFile)
				d = o.read()
				o.close()
	
				if len(d) > 100:
					# We only scraped the 'main' tag, but the saving
					#  function puts a html structure around it
					idPrefix = folder[0]+htmlFile.replace(".html","")
					html = BeautifulSoup(d, 'lxml')
					html = html.find("main")
					print("\t\t\t"+folderPath+htmlFile)
					out.append({"LOCATION":"PAGE: "+idPrefix})
					out += parsePage(html,idprefix=idPrefix)
	
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)
	
def postProcessing(out):
	out2 = []
	for line in out:
		if type(line) == list:
			out2 += line
		else:
			out2.append(line)
	return(out2)
