from bs4 import BeautifulSoup
import json
import re
import xlrd
import copy
import os

# https://houses.fedatamine.com/en-uk/scenarios/1
# https://houses.fedatamine.com/en-us/monastery/0
	# In this, some choices are duplicated

# TODO: parse quest events, 
# TODO: DLC dialogue (e.g. "Monk") is not parsed correctly - there is no subsection layer
# TODO: No subsection layer in scenarios (see TODO below)
	

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
	
def parseScenario(html,lang="en-uk",idprefix=""):
	global seenEventBases
	
	out = []
	seenEventBases = []
	scenarioTitle = html.find("h1").get_text()
	#print("\n\n")
	#print(scenarioTitle)
	out.append({"LOCATION":scenarioTitle})
	sections = html.find_all("div",recursive=False)
	for section in sections:
		if section.has_attr("class") and "row" in section["class"]:
			pass
		else:
			sectionTitle = section.find("h3",recursive=False)
			if not sectionTitle is None:
				out.append({"LOCATION": sectionTitle.get_text().strip()})
			subsections = section.find_all("div", recursive=False)
			for subsection in subsections:
				# event, event-base or tab-group (decision)
				parsedSubsection = parseSubsection(subsection,lang,idprefix)					
				if not parsedSubsection is None:
					if type(parsedSubsection) == list:
						out += parsedSubsection
					else:
						out.append(parsedSubsection)
				out.append({"ACTION":"---"})
			out.append({"ACTION":"---"})
	out.append({"ACTION":"---"})
	return(out)
	
	
def parseSubsection(subsection,lang="",idprefix=""):
	global seenEventBases
	if isDecisionEvent(subsection):
		choices = parseDecision(subsection)
		return(choices)
	elif isEventBase(subsection):
		events = parseEventBase(subsection)
		# The web content seems to duplicate some event bases
		if not events in seenEventBases:
			seenEventBases.append(events)
			return(events) # is list
		else:
			return(None)
	elif isQuestEvent(subsection):
		return({"ACTION": "QUEST " + subsection.get_text()})
	else:	
		subsectionDivID = idprefix+"X"
		if subsection.has_attr("id"):
			subsectionDivID = idprefix+"_"+subsection["id"].replace("event","e")
			
		subsectionDivs = subsection.find_all("div", recursive=False)
		for subsectionDiv in subsectionDivs:
			#print("\n\n\n")
			#print(subsectionDiv)
			if subsectionDiv.has_attr("py-2") and "py-2" in subsectionDiv.attrs["class"]:
				parsedEvent = parsePy2(subsectionDiv)	
				parsedEvent["_id"] = subsectionDivID
				return(parsedEvent)
			elif isActionEvent(subsectionDiv):
				action = {"ACTION": cleanDialogue(subsectionDiv.get_text())}
				return(action)
			elif isCenterDiv(subsectionDiv):
				parsedEvent = parseCenterDiv(subsectionDiv)
				if not parsedEvent is None:
					return(parsedEvent)
				else:
					return(None)
			elif isBylethDiv(subsectionDiv):
				parsedEvent = {"PC": cleanDialogue(subsectionDiv.get_text())}
				parsedEvent["_id"] = subsectionDivID
				return(parsedEvent)
			elif isLetter(subsectionDiv):
				parsedEvent = {"ACTION": "LETTER: " + cleanDialogue(subsectionDiv.get_text())}
				parsedEvent["_id"] = subsectionDivID
				return(parsedEvent)
			else:
				#print("ERROR X:")
				#print(subsectionDiv)
				return(None)						

	

def isDecisionEvent(event):
	if not event.has_attr("class"):
		return(False)
	return(any([x.startswith("tab-group") for x in event.attrs["class"]]))
	
def isEventBase(event):
	if not "id" in event.attrs:
		return(False)
	return(event.attrs['id'].startswith("event-base"))

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
		
	print("____")
	print(mainDiv)

		
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
	elif mainDiv.name == "ul":
		choices = [{"PC":cleanDialogue(x.get_text())} for x in mainDiv.find_all("li")]
		return({"CHOICE":choices})
	elif mainDiv.has_attr("class") and "tab-content" in mainDiv["class"]:
		pass
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
		
def parseDecision(tabGroup):
	options = tabGroup.find("ul").find_all("li")
	responseDiv = tabGroup.find("div") # Tab content
	return(parseDecisions2(options,responseDiv))
	
	
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
		subsections = responseGroupDict[opCode].find_all("div",recursive=False)
		for subsection in subsections:
			parsedSubsection = parseSubsection(subsection)					
			if not parsedSubsection is None:
				if type(parsedSubsection) == list:
					choice += parsedSubsection
				else:
					choice.append(parsedSubsection)
		
		#py2s = responseGroupDict[opCode].find_all("div",{"class":"py-2"},recursive=False)
		py2s = responseGroupDict[opCode].find_all("div",recursive=False)
		choice += [parsePy2(py2) for py2 in py2s]
		choice = [cx for cx in choice if not cx is None]
		if len(choice)>0:
			choices.append(choice)
	out = {"CHOICE":choices}
	return(out)	
		
def parseEventBase(event):
	seenChoices = []
	subEvents = [x for x in event.find_all(["div","ul"],recursive=False)]
	out = []
	i = 0
	while i<len(subEvents):
		subsection = subEvents[i]
		# Can be any py-2s or tabgroups (but not events!)
		if isDecisionEvent(subsection):
			choices = parseDecision(subsection)
			out.append(choices)
		elif subsection.name == "ul":
			# TODO: Some decisions are not embedded in a tab group?
			#  but a raw 'ul'. Sometimes this has no effect on the outcome
			#  but sometimes there's a following tab-content element
			#  So need to detect this, take the next element and pass it to the decision parser
			#   then remove the tab-content element from the subEvents list
			options = subsection.find_all("li")
			responseDiv = subEvents[i+1]
			choices = parseDecisions2(options,responseDiv)
			if not choices in seenChoices:
				seenChoices.append(choices)
				out.append(choices)
			i += 1 # Skip next div
		elif isEventBase(subsection):
			events = parseEventBase(subsection)
			out += events
		else:
			subOut = parsePy2(subsection)
			if not subOut is None:
				out.append(subOut)
		i += 1
	return(out)
	
def parseCenterDiv(div):
	img = div.find("img")
	if not img is None:
		return({"ACTION": "IMG: "+img["src"]})

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
		folders = ["scenarios"]#["scenarios","monastery"]
		for folder in folders:
			out.append({"LOCATION":"FOLDER: "+folder})
			folderPath = rawFolderPath+"/"+lang+"/"+folder+"/"
			htmlFiles = [x for x in os.listdir(folderPath) if x.endswith('html')]
		
			# TODO: Sort by actual number
			htmlFiles.sort(key=alphanum_key)
			for htmlFile in htmlFiles[:1]:
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
					out += parseScenario(html,idprefix=idPrefix)
	
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)
	
def postProcessing(out):
	return(out)
