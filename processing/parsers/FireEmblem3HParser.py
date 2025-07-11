from bs4 import BeautifulSoup,Tag, NavigableString
import json
import re
import xlrd
import copy
import os
import hashlib

charImageDetails = {}
idTracker = {"SUP":0,"D":0,"STG":0,"STA":0,"LOC":0}
allSeenIds = []

# https://houses.fedatamine.com/en-uk/scenarios/1
# https://houses.fedatamine.com/en-us/monastery/0
	# In this, some choices are duplicated

# TODO: for support, need to add name of character who is affected, associate with previous speaker? with icon number?
#
# TODO: notes?
# TODO: Big images?
# TODO: parse status: e.g. "Ferdinand & Dorothea support level B reached"
# TODO:  Context boxes

# todo. there can be multiple characters in a support link:
# https://houses.fedatamine.com/en-us/monastery/11#event-wc-213-0
# gain and lose support- check which character is gaining, look up number in hyperlink
# Look at character pages, make dictionary of image links to char names

# todo: add -- after section ends?

# TODO: Filtering seen dialogue (seenSubsections) won't work with new ids.

# TODO: are some sections mutually exclusive for silver snow, azure moon etc.?
#  https://houses.fedatamine.com/en-us/monastery/7#event-base-13-0

# Scenario
# 
# Section  				<div class="col-12 p-0">
# 	Event	id="event-108" [subsection]
# 		a text-muted
# 		div py-2
# 	Event
# 		a text-muted
# 		event-notification
# 	Tab Group class="tab-group-0" [subsection]
# 		ul
# 			li
# 				a (text of choice)
# 		tab-content
# 			div id =group0 [section]
# 				event [subsection]
# 				event
# 				div class=tab-group 1 [subsection]
# 					ul
# 					tab-content
#
# monestary
# 
# Section					Bare div
# 	h3
# 	event base			id="event-base-2-3"
# 		a text-muted
# 		div py2 q`
# 		div py2
# 			div
# 				img
# 			div px3
# 				a
# 				div listen
# 				p (dialogue)
# 	event base
# 		a
# 		div py2
# 		ul
# 		div tab-content
	

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
	txt = txt.replace('\u205f'," ")
	txt = re.sub(" +"," ",txt)
	txt = re.sub("(\\.\\.\\.+)","\\1 ",txt)
	return(txt)
	
def parsePage(html,lang="en-uk",idprefix="",folder="",fileName=""):
	global seenSubsections
	seenSubsections = []
	
	out = []
	scenarioTitle = html.find("h1").get_text()
	out.append({"LOCATION": (folder + ": " + scenarioTitle).strip()})
	
	sections = html.find_all(["div","h3"],recursive=False)
	for section in sections:
		if not (section.has_attr("class") and "row" in section["class"]):
			ret = parseSection2(section,idprefix,folder,fileName)
			if not ret is None:
				if type(ret) == list:
					out += ret
				else:
					out.append(ret)
			if len(out) > 0 and out[-1] != {"ACTION": "---"}:
				out.append({"ACTION": "---"})
	return(out)
		
		
def parseSection2(section,idprefix="",folder="",fileName=""):
	# Iterate over subsections
	#  (event, event base or tab group)
	# but doesn't really matter?
	out = []
	for subsection in section.findChildren(recursive=False):
		ret = parseSubsection2(subsection,idprefix,folder,fileName)
		if not ret is None:
			if not ret in seenSubsections: # TODO: this filters repeated dialogue, but won't work with new IDs
				seenSubsections.append(ret)
				if type(ret) == list:
					out += ret
				else:
					out.append(ret)
			#if len(out) > 0 and out[-1] != {"ACTION": "---"}:
			#	out.append({"ACTION": "---"})
	return(out)
		
def parseSubsection2(subsection,idprefix="",folder="",fileName=""):
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
			ret = parsePy2(part,idprefix,folder,fileName)
			if not ret is None:
				out.append(ret)
		elif isTabGroup(part):
			ret = parseSubsection2(part,idprefix,folder,fileName)
			if not ret is None:
				out.append(ret)
		elif part.has_attr("class") and "event-notification" in part["class"]:
			out.append({"ACTION": cleanDialogue(part.get_text())})
		elif part.has_attr("class") and "text-center" in part.get("class"):
			ret = parseCenterDiv(part)
			if not ret is None:
				out.append(ret)
		elif not part.find("div",{"class":"opinion-img"}) is None:
			ret = parseCenterDiv(part)
			if not ret is None:
				out.append(ret)
		elif part.name == "ul" and part.has_attr("class"):
			options = part.find_all("li")
			responseDiv = subsection[i+1]
			choices = parseDecisions2(options,responseDiv)
			out.append(choices)
			i += 1 # Skip next div
		elif isSupportEvent(part):
			return(parseSupport(part)) # Not reached?
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
	sup = mainDiv.find("div",{"class":"positive-background"})
	return(not sup is None)

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

def parsePy2(mainDiv,idprefix="",folder="",fileName=""):
	global charImageDetails
	
	if mainDiv is None:
		return(None)
	
	mainDivID = "XX"
	if not mainDiv.get("href") is None:
		mainDivID = mainDiv["href"].replace("#","") #X TODO: add location id?
	mainDivID = folder +"/" + fileName.replace(".html","") + "/"+mainDivID
	
	if isActionEvent(mainDiv):
		return({"ACTION": mainDiv.get_text()}) #X
	elif isSupportEvent(mainDiv):
		return(parseSupport(mainDiv))
	elif mainDiv.get_text().strip() == "link":
		return(None)
	elif isQuestEvent(mainDiv):
		return({"ACTION": "QUEST: "+mainDiv.get_text().strip()}) #X
	elif isNoteDiv(mainDiv):
		return({"ACTION": "NOTE: " + mainDiv.get_text().strip()}) #X
	else:


		dialogueDiv = mainDiv.find("div",{"class":"px-3"})
		charName = ""
		dialogue = ""
		if dialogueDiv is None:
			charName = "Byleth"
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
		ret = {charName: dialogue}	#X
		
		# Add other information
		if True:
			im = mainDiv.find("img")
			imsrc = im["src"]
			if imsrc.startswith("https://assets.fedatamine.com/3h/"):
				imsrc = imsrc.replace("https://assets.fedatamine.com/3h/","")
			ret["_img"] = imsrc
			
			if imsrc in charImageDetails:
				emotion = charImageDetails[imsrc]["emot"]
				ret["_emot"] = emotion
			listen = mainDiv.find("div",{"class":"listen"})
			if not listen is None:
				audio = listen["data-key"]
				ret["_audio"] = audio;
				ret["_id"] = audio.replace("/audio/","").replace("%3D","").strip()
		
		if not "_id" in ret:
			ret["_id"] = mainDivID
		
		return(ret)

def parseSupport(mainDiv):
	global idTracker
		
	supportText = mainDiv.get_text().strip()
	if supportText == "":
		opinionDiv = mainDiv.find("div",{"class":"opinion-img"})
		if not opinionDiv is None:
			supportText = "SUPPORT: Gain support points"
			if not "like" in opinionDiv["class"]:
				supportText = "SUPPORT: Lose support points"
		portrait = mainDiv.find("img",{"class":"img-fluid"})
		if not portrait is None:
			src = portrait["src"]
			src = src[src.index("face_school"):]
			if src in charImageDetails:
				supportText += " with "+charImageDetails[src]["charShortName"]
	
	idx = "SUP"
	if supportText.count(" with ")>0:
		charName = supportText[supportText.index(" with ")+5:].strip()
		idx += "_"+charName.replace(" ","-")
	
	idx += "_"+str(idTracker["SUP"])
	idTracker["SUP"] += 1
	
	return({"ACTION": supportText,"_sup":"Y","_id":idx}) 	#X
	
def parseDecisions2(options,responseDiv):
	optionCode = [x.find("a")["href"].replace("#","") for x in options]
	optionDict = dict(zip(optionCode,[x.get_text() for x in options]))

	responseGroups = responseDiv.find_all("div", recursive = False)
	responseGroupCodes = [x["id"] for x in responseGroups]
	responseGroupDict = dict(zip(responseGroupCodes,responseGroups))

	choices = []
	for opCode in optionDict:
		# Starts by assuming that Byleth is talking, but it's not always a 
		#  dialogue choice
		speaker = "Byleth"
		if isStatus(optionDict[opCode]) or "Else" in optionDict:
			speaker = "STATUS"
		choice = [{speaker: optionDict[opCode]}]
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
	
def isStatus(txt):
	if txt == "Else" or txt == "Unknown" or txt == "Condition met":
		return(True)
	if txt in ["Byleth (Male)","Byleth (Female)"]:
		return(True)
	if txt.endswith("is alive & recruited") or txt.endswith("is alive") or txt.endswith("is recruited"):
		return(True)
	if txt.startswith("All dead") or txt.startswith("Not All dead"):
		return(True)
	if re.search("support level .+?reached",txt):
		return(True)
	if txt.endswith(" Victory") and len(txt)<25: #"Black Eagles Victory"
		return(True)
	if txt.endswith(" won") and txt.count(" ")==1: # "Edelgard won"
		return(True)
	if txt.startswith("If ") and (not txt.strip()[-1] in [".", "!", "-", "?"]):
		return(True)
	if txt in ["Part I","Part II"]:
		return(True)
	if txt in ["Silver Snow","Azure Moon","Verdant Wind","Crimson Flower", "Cindered Shadows"]:
		return(True)
	return(False)
		
	
def parseCenterDiv(div):
	opinionDiv = div.find("div",{"class":"opinion-img"})
	if not opinionDiv is None:
		return(parseSupport(div))
#		polarity = "Gain support"
#		if not "like" in opinionDiv["class"]:
#			polarity = "Lose support"
#		return({"ACTION": "SUPPORT: "+polarity,"_sup":"Y"}) 	#X

	spans = div.find("span",{"class":"support-change-text"})
	if not spans is None:
		return({"ACTION": "SUPPORT: "+div.get_text().strip(),"_sup":"Y"})	#X
		
	img = div.find("img")
	if not img is None:
		src = img["src"]
		idx = src.replace("https://assets.fedatamine.com/3h","").replace("/","_").replace(".png","")
		return({"ACTION": "IMG: "+img["src"], "_id":idx})	#X

	#print("ERROR")
	#print(div)
	return(None)

def getTeaFinalComments(finalCommentsFile):
	o = open(finalCommentsFile)
	d = o.read()
	o.close()
	
	html = BeautifulSoup(d,'lxml')
	html = html.find_all("table")[2]
	rows = html.find_all("tr")[1:]
	pref = {}
	for row in rows:
		dialogue = cleanDialogue(row.find("td").get_text())
		dialogue = dialogue.replace("’","'").replace("…","... ")
		preferences = [x.get_text() for x in row.find_all("td")[1:]]
		preferences = [x for x in preferences if x!="–"]
		pref[dialogue] = preferences
	return(pref)

def parseTeaConversations(baseFolder):
	# the FEDataMine website only includes the lines, not which
	#  lines are 'final comments' which can gain support if the player
	#  chooses the right option. 
	#  So we collect extra info from https://serenesforest.net/three-houses
	teaFolder = baseFolder + "tea/"
	teaFiles = [x for x in os.listdir(teaFolder) if x.count("_FinalComments")==0 and x.endswith(".html")]

	out = []
	for teaFile in teaFiles:
	
		teaPreferences = getTeaFinalComments(teaFolder+teaFile.replace(".html","_FinalComments.html"))
	
		o = open(teaFolder+teaFile)
		d = o.read()
		o.close()
		
		charName = teaFile.split("_")[1].replace(".html","")
		out.append({"LOCATION": "TEA TIME - "+charName})
		
		soup = BeautifulSoup(d, 'lxml')
		html = soup.find("main")
		# (there are two embedded tab-pane active divs)
		html = html.find("div",{"class":"tab-pane active"}).find("div",{"class":"tab-pane active"})
		
		idPrefix = "tea_"+teaFile.replace(".html","")
		folder = "tea"
		
		bits = html.find_all(["ul","h3","h5"])
		sectionDict = {}
		sectionName = "X"
		for bit in bits:
			if bit.name in ["h3","h5"]:
				sectionName = bit.get_text().strip()
			else:
				# Is a UL (though might not be dialogue)
				dialogue = cleanDialogue(bit.get_text()).replace("volume_up","").strip()
				ret = {charName: dialogue, "_tea":"Y"}
				audioBit = bit.find("div",{"class":"listen"})
				if not audioBit is None:
					audio = bit.find("div")["data-key"]
					ret["_audio"] = audio;
					ret["_id"] = audio.replace("/audio/","").replace("%3D","").strip()
				
				if not sectionName in sectionDict:
					sectionDict[sectionName] = []
				sectionDict[sectionName].append(ret)
		
		# Split talk into final comment and observe lines
		sectionDict["Final Comment"] = []
		sectionDict["Observe"] = []
		for line in sectionDict["Talk"]:
			dialogue = line[charName]
			if dialogue in teaPreferences:
				pref = " or ".join(teaPreferences[dialogue])
				cx = [line,{"CHOICE":[
					[{"STATUS": "Player chooses "+pref},
					 {"ACTION": "Gain support points with "+charName,"_sup":"Y"}
					],[{"STATUS": "Else"}]]},{"ACTION":"---"}]
				sectionDict["Final Comment"].append(cx)
			else:
				sectionDict["Observe"].append(line)
				
		del sectionDict["Talk"]
		del sectionDict["Likes"]
		del sectionDict["Favorite"]
		
		for sectionName in sectionDict:		
			out.append({"ACTION": "Tea time "+sectionName+ " - "+charName})
			for bit in sectionDict[sectionName]:
				if isinstance(bit, list):
					out += bit
				else:
					out.append(bit)
					out.append({"ACTION":"---"})
	return(out)
		
	

def parseFile(fileName,parameters={},asJSON=False):
	global charImageDetails
	# The raw files are grouped by type within subfolders
	# so there's just one dummy file and the parseFile function
	# loops through the subfolder contents
	rawFolderPath = fileName[:fileName.rindex("/")]
		
	charImageDetails = json.load(open(rawFolderPath + "/../charImageDetails.json"))
	
	
	out = []
	langs = ["en-uk"]
	for lang in langs:
		folders = ["scenarios","monastery","supports","battles"]
		for folder in folders:
			out.append({"LOCATION":"FOLDER: "+folder})
			folderPath = rawFolderPath+"/"+lang+"/"+folder+"/"
			htmlFiles = [x for x in os.listdir(folderPath) if x.endswith('html')]
		
			# Human sort number 
			htmlFiles.sort(key=alphanum_key)
			for htmlFile in htmlFiles:
				o = open(folderPath+htmlFile)
				d = o.read()
				o.close()
	
				if len(d) > 100:
					# We only scraped the 'main' tag, but the saving
					#  function puts a html structure around it
					idPrefix = folder[0]+htmlFile.replace(".html","")
					soup = BeautifulSoup(d, 'lxml')
					html = soup.find("main")
					#print("\t\t\t"+folderPath+htmlFile)
					out.append({"LOCATION":"PAGE: "+idPrefix}) 
					
					if folder == "battles":
						# The battle dialogue needs to be embedded in a lower level
						for elem in html:
							if elem.name=="div" and elem.has_attr("id") and elem["id"].startswith("event-script"):
								elem.wrap(soup.new_tag("div"))
					
					out += parsePage(html,idprefix=idPrefix,folder=folder,fileName=htmlFile)
	
		# Tea time conversatinos
		out.append({"LOCATION":"FOLDER: Tea Time"})
		out += parseTeaConversations(rawFolderPath+"/"+lang+"/")
	
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
			
	def getHash(txt):
		return(hex(hash(txt))[2:])
	
	def checkIDs(lines):
		global idTracker
		global allSeenIds
		
		for line in lines:
			charName = [x for x in line.keys() if not x.startswith("_")][0]
			if charName == "CHOICE":
				for choice in line["CHOICE"]:
					checkIDs(choice)
			else:
				if not "_id" in line:
					txt = line[charName]
					idCategory = "D"
					if txt.startswith("SUPPORT:"):
						idCategory = "SUP"
					elif txt.count("the scene")>0:
						idCategory = "STG"
					elif charName == "STATUS":
						idCategory = "STA"
					elif charName == "LOCATION":
						idCategory = "LOC"
					
					
					if idCategory == "SUP":
						idx = "SUP"
						if txt.count(" with ")>0:
							charName = txt[txt.index(" with ")+5:].strip()
							idx += "_"+charName.replace(" ","-")
						idx += "_"+str(idTracker[idCategory])
						line["_id"] = idx
						idTracker[idCategory] += 1
						
					else:
						h = getHash(txt)
						idx = idCategory+"_"+h
						if idx in allSeenIds:
							idx = idCategory+"_"+str(idTracker[idCategory])
							idTracker[idCategory] += 1
						line["_id"] = idx
				
				allSeenIds.append(line["_id"])
					
	checkIDs(out2)
		
	return(out2)
