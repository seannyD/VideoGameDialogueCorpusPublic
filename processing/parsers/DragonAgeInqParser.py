# https://www.youtube.com/watch?v=xyt8dqqmTbI
# TODO: dealing with SeenIDs - fix at the end

# TODO: deal with not being able to find lines

# TODO: check if is dialogue being re-joined properly? (find video or follow links)
#[
#	{"ACTION": "IF (e2c262e7-7591-481f-a5e5-297141f401d3 # nullptr = True)"},
#	{"FollowerPlots/Odette/odt_comte": "What a pleasure to meet you, my lady. Seeing the same faces at every event becomes so tiresome.", "_sid": "857ecc32-a0b6-07f8-e8bc-80907a848732", "_lid": "86206692-94aa-44f9-855f-416a8aaac56c"},
#	{"FollowerPlots/Odette/odt_comte": "So you must be a guest of Madame de Fer. Or are you here for Duke Bastien?", "_sid": "857ecc32-a0b6-07f8-e8bc-80907a848732", "_lid": "f536bca2-9aa3-4cf5-ad2d-6028ec1046c0"}],
#[
#	{"FollowerPlots/Odette/odt_comte": "A pleasure, ser. We so rarely have a chance to meet anyone new. It is always the same crowd at these parties.", "_sid": "857ecc32-a0b6-07f8-e8bc-80907a848732", "_lid": "fbd7b993-9a36-4356-9ae3-3aa5711d14d2"},
#	{"FollowerPlots/Odette/odt_comte": "So you must be a guest of Madame de Fer. Or are you here for Duke Bastien?", "_sid": "857ecc32-a0b6-07f8-e8bc-80907a848732", "_lid": "f536bca2-9aa3-4cf5-ad2d-6028ec1046c0"},
#	{"FollowerPlots/Odette/odt_comtess": "Are you here on business?", "_sid": "c5355ad9-3bf4-d0e6-f1c9-270c5e5eb77f", "_lid": "976ebd10-fb67-4112-aca4-b9721afe9735"},
#	{"FollowerPlots/Odette/odt_comtess": "I have heard the most curious tales of you. I cannot imagine half of them are true.", "_sid": "c5355ad9-3bf4-d0e6-f1c9-270c5e5eb77f", "_lid": "7f0c3eee-f63d-4946-8cef-4daca9fb6559"},


import json, csv, re,os
from bs4 import BeautifulSoup

da3 = {}
lineDict = {}
charDict = {}
plotFlags = {}
finalSeenIDs = []

conditionDict = {
	"e2c262e7-7591-481f-a5e5-297141f401d3": "PC is female"
#	 E762C2E2 9175 1F48 A5E5 297141F401D3
#	 A86805E9 6A2A A447 BCF3 258B543D014D
}

def cleanString(txt):
	txt = txt.replace("\x19s","'")
	txt = txt.replace("\u0014"," - ")
	# TODO: deal with multiple quotes properly.
	txt = re.sub('^"(.+)"$', "\\1",txt)
	txt = txt.strip()
	if(len(txt.replace('"',''))==0):
		txt = ""
	return(txt)

def parseFile(fileName,fileType,asJSON=False):
	# This method just loads the text strings
	# from the StringList_en.csv file
	#Êsee post processing for recursive search 
	#  through the conversation files




	firstLine=True
	for line in open(fileName, encoding='latin-1'):
		if firstLine:
			line = "."+line
			firstLine = False
		line = line[1::2].strip()
		if len(line)>0:
			stringID,text = line.split(",",1)
			text = cleanString(text)
			da3[stringID] = text
	
	plotFlags = loadPlotFlags('../data/DragonAge/DragonAgeInquisition_B/plotFlagsA.csv')
	plotFlagsB = loadPlotFlags('../data/DragonAge/DragonAgeInquisition_B/plotFlagsB.csv')
	plotFlags.update(plotFlagsB)
	
	out = []
	
	if asJSON:
		print(json.dumps({"text":out}, indent = 4))
		return(json.dumps({"text":out}, indent = 4))
	return(out)

	
###############

def postProcessing(out):
	
	files = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser("../data/DragonAge/DragonAgeInquisition_B/raw/Conversations/")) for f in fn]
	
	files = [x for x in files if x.endswith(".xml")]
	
	for file in files:
		#print(">>>")
		print(file)
		txt = open(file).read()
		out += processXMLFile(txt)
		
	writeCharData()
	
	return out


def processXMLFile(txt):
	global lineDict
	soup = BeautifulSoup(txt, "lxml")
	
	lines = soup.find_all("conversationline")
	plines = processLines(lines)
	
	links = soup.find_all("conversationlink")
	plines += processLines(links)
	
	# Make a dictionary for easy reference
	lineDict = {}
	for lx in plines:
		lineDict[lx["id"]] = lx
	
	# "Conversation" tags start conversation
	conversations = soup.find_all("conversation")
	
	out = []
	#seenIDs = []
	
	# Build the conversation structure 
	# (need recursive function)
	for conv in conversations:
		out.append({"LOCATION": conv.find("name").get_text() })
		primarySpeaker = ""
		ps = conv.find("primaryspeaker")
		if ps:
			primarySpeaker = ps.get_text()
		#print(conv["guid"])
		childIDs = getChildNodes(conv)
		for childID in childIDs:
			out += walkStructure(lineDict[childID],primarySpeaker)
	
	
# 	out = [{"CHOICE": [
# 		[
# 			{"ACTION": "IF (e2c262e7-7591-481f-a5e5-297141f401d3 # nullptr = True)"},
# 			{"FollowerPlots/Odette/odt_comte": "What a pleasure to meet you, my lady. Seeing the same faces at every event becomes so tiresome.", "_ID": "86206692-94aa-44f9-855f-416a8aaac56c"},
# 			{"FollowerPlots/Odette/odt_comte": "So you must be a guest of Madame de Fer. Or are you here for Duke Bastien?", "_ID": "f536bca2-9aa3-4cf5-ad2d-6028ec1046c0"}],
# 		[
# 			{"FollowerPlots/Odette/odt_comte": "A pleasure, ser. We so rarely have a chance to meet anyone new. It is always the same crowd at these parties.", "_ID": "fbd7b993-9a36-4356-9ae3-3aa5711d14d2"},
# 			{"FollowerPlots/Odette/odt_comte": "So you must be a guest of Madame de Fer. Or are you here for Duke Bastien?", "_ID": "f536bca2-9aa3-4cf5-ad2d-6028ec1046c0"},
# 			{"FollowerPlots/Odette/odt_comtess": "Are you here on business?", "_ID": "976ebd10-fb67-4112-aca4-b9721afe9735"},
# 			{"FollowerPlots/Odette/odt_comtess": "I have heard the most curious tales of you. I cannot imagine half of them are true.", "_ID": "7f0c3eee-f63d-4946-8cef-4daca9fb6559"},
# 			{"CHOICE": [
# 					[
# 						{"ACTION": "PC CHOOSES > You know of me?"},
# 						{"PC": "What have you heard about me?", "_ID": "a9effbc0-a821-4e11-b378-f30c0db77b52"}
# 						],
# 					[	{"ACTION": "Second choice"}]
# 					]}]]}]

	
	# Re-sort to find common codas
	out = depthFirstToBreadthFirst(out)
	# Remove duplicates, assuming local constraints
	out = replaceDuplicateLinesWithGOTO(out)
	# Parse <LocalizedCharacter> tags (see Cre_keep_spy_09.xml)
	parseCharacterData(soup)
	
	#return(plines)  # return the parsed line chunks
	return(out)


def dataToDialogue(line,primarySpeaker):
	global charDict
	
		# replace link with the full line
	if line["type"] == "conversationlink":
		linkID = re.sub("\\[.+?\\]","",line["linkedline"]).strip()
		line = lineDict[linkID]
	
	
	out = []
	
	### Add preconditions
	if "plotconditions" in line:
		out.append({"ACTION":line["plotconditions"]})
		
	### Add choice cues
	if "paraphrasereference" in line:
		out.append({"ACTION":"PC CHOOSES > "+line["paraphrasereference"]})

	### Add dialogue	
	speakerName,speakerID = cleanName(line["speaker"])
	if speakerName == "":
		speakerName,speakerID = cleanName(primarySpeaker)
	if len(line["dialogue"])>0:
		lx = {speakerName:line["dialogue"],
				#"_sid":speakerID,
				"_ID":line["id"]}
		out.append(lx)

	### Add effects			
	if "plotactions" in line:
		for act in line["plotactions"]:
			out.append({"ACTION":act})
	
	# Keep track of character data
	if not speakerID in charDict:
		charDict[speakerID] = {
			"name":speakerName, 
			"gender":line["speakergender"]}
	
	return(out)

def walkStructure(line,primarySpeaker,seenIDs=[]):
	# (lineDict is global)
#	if line["id"] in seenIDs:
#		return([{"GOTO": line["id"]}])

	
	out = dataToDialogue(line,primarySpeaker)
#	if line["id"] == "f536bca2-9aa3-4cf5-ad2d-6028ec1046c0":
#		print("YES1")
	while True:
		childIDs = line["childIDs"]
		if len(childIDs)==1:
			line = lineDict[childIDs[0]]
			# If we swap the link line with its referent here,
			#    then there is infinite recursion?
#			if line["type"] == "conversationlink":
#				linkID = re.sub("\\[.+?\\]","",line["linkedline"]).strip()
#				line = lineDict[linkID]
			#if line["id"] in seenIDs:
			#	nextID = line["childIDs"][0]
			#	out.append({"GOTO":nextID})
			#	break
			#seenIDs.append(line["id"])
			out += dataToDialogue(line,primarySpeaker)
		elif len(childIDs)>1:
			childLines = []
			for childID in childIDs:
				#if childID in seenIDs:
				#	childLines.append({"GOTO":childID})
				#else:
				#	seenIDs.append(childID)
					childLines.append(walkStructure(lineDict[childID],primarySpeaker,seenIDs))
			childLines = [x for x in childLines if len(x)>0]
			if len(childLines)>0:
				out.append({"CHOICE":childLines})
			break
		elif len(childIDs)==0:
			break
	#seenIDs.append(line["id"])
	return(out)
	
			
def cleanName(txt):
	txt = txt.replace("[Ebx] DA3/DesignContent/Characters/","")
	if txt == "nullptr":
		return(("None","0"))
	sname,sid = [x.strip().replace("]","") for x in txt.split("[",1)]
	return((sname,sid))

def processLines(data):
	# PC dialogue has <ParaphraseReference> (the cue)
	# and ConversationStringReference that contains 
	# the actual line that is spoken by the character
	out = []
	for line in data:
		lx = {"id":line["guid"],"type":line.name}
		# Add dialogue line
		dt = line.find("conversationstringreference")
		if dt:
			stringID = dt.find("stringid").get_text().replace("0x","").strip().upper()
			if stringID in da3:
				lx["dialogue"] = da3[stringID]
			else:
				lx["dialogue"] = "(MISSING "+stringID+")"
		
		# Add other attributes
		for tag in ["ParaphraseReference","Speaker","SpeakerGender"]:
			addNodeData(line,tag.lower(),lx)
		if "paraphrasereference" in lx:
			lx["paraphrasereference"] = da3[lx["paraphrasereference"].upper()]
		
		# Add child ids
		lx["childIDs"] = getChildNodes(line)
		addNodeData(line,"linkedline",lx)	
		
		plotConditions = parsePlotConditions(line)
		if plotConditions:
			lx["plotconditions"] = plotConditions
		plotActions = parsePlotActions(line)
		if plotActions:
			lx["plotactions"] = plotActions

		out.append(lx)
	return(out)
	

def addNodeData(soup,tag,d):
	t = soup.find(tag)
	if t:
		txt = t.get_text().replace("0x","").strip()
		if txt!="00000000":
			d[tag] = txt

def getChildNodes(soup):
	cn = soup.find("childnodes")
	childIDs = [member.get_text() for member in cn.find_all("member")]
	childIDs = [re.sub("\\[.+?\\]","",x).strip() for x in childIDs]
	return(childIDs)
	
def parsePlotConditions(soup):
	pc = soup.find("plotconditions")
	if not pc or len(pc)==0:
		return(None)
	members = pc.find_all("member")
	if not members or len(members)==0:
		return(None)
	out = []
	for mem in members:
		schematic = mem.find("conditionschematic").get_text().strip()
		mid = mem.find("plotflagid").get_text().strip()
		#print(mid)
		if mid in plotFlags:
			mid = plotFlags[mid]
		val = mem.find("desiredvalue").get_text().strip()
		out.append(mid + " # "+schematic+ " = " + val)
	return("IF " + " AND ".join(["("+x+")" for x in out]))

def parsePlotActions(soup):
	pa = soup.find("plotactions")
	if not pa:
		return(None)
	if pa["count"]=="0":
		return(None)
	members = pa.find_all("member")
	out = []
	for mem in members:
		actionType = mem.find("actiontype").get_text().strip()
		actionSchem = mem.find("actionschematic").get_text().strip()
		fid = mem.find("plotflagid").get_text().strip()
		out.append("SET "+ actionType + " [" + fid+"] "+ actionSchem)
	return(out)


def parseCharacterData(soup):
	global charDict
	charData = soup.find_all("localizedcharacter")
	for cd in charData:
		cid = cd["guid"]
		elements = {}
		for elem in cd.findChildren():
			elements[elem.name] = elem.get_text()
		if not cid in charDict:
			charDict[cid] = elements
		else:
			charDict[cid].update(elements)
		
def writeCharData():
	global charDict
	# (some character data is in the conversation folders)
	
	# Load extra character data:
	files = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser("../data/DragonAge/DragonAgeInquisition_B/raw/Characters/")) for f in fn]	
	files = [x for x in files if x.endswith(".xml")]
	for file in files:
		txt = open(file).read()
		soup = BeautifulSoup(txt, "lxml")
		parseCharacterData(soup)
	
	# output full character data
	headers = ["id"]
	for cid in charDict:
		headers += [x for x in charDict[cid].keys() if not x in headers]
	out = []
	for cid in charDict:
		row = [cid]
		for h in headers:
			if h in charDict[cid]:
				dat = charDict[cid][h].replace("DA3/DesignContent/Characters/","")
				dat = cleanString(dat)
				row.append(dat)
			else:
				row.append("")
		out.append(row)
	with open('../data/DragonAge/DragonAgeInquisition_B/charDataFromGameData.csv', 'w') as f:
		writer = csv.writer(f)
		writer.writerow(headers)
		for row in out:
			writer.writerow(row)
	
	# Write alias data
	aliasDict = {}
	# Write gender data
	genderDict = {}
	for cid in charDict:
		cname = charDict[cid]["name"]
		cname = cname.replace("DA3/DesignContent/Characters/","")
		if cname == "nullptr":
			cname = "None"
		if "charactername" in charDict[cid]:
			fullName = charDict[cid]["charactername"]
			aliasDict[cname] = fullName
			cname = fullName
		gender = "Unknown"
		if "gender" in charDict[cid]:
			gender = charDict[cid]["gender"]
		if not cname in ["","None","nullptr","global/Hero"]:		
			try:
				genderDict[gender].append(cname)
			except:
				genderDict[gender] = [cname]
	json.dump(aliasDict, open('../data/DragonAge/DragonAgeInquisition_B/aliasesFromGameData.json', 'w'),indent=4)
	json.dump(genderDict, open('../data/DragonAge/DragonAgeInquisition_B/charGenderFromGameData.json', 'w'),indent=4)

	
def loadPlotFlags(fn):
	d = open(fn).read()
	parts = [x.split(",",2) for x in d.split("\n")[1:]]
	out = {}
	for p in parts:
		#93858996-9000-4db6-9373-658acae601bb
		#34f91a75-0826-4bf7-b14a-10deb0fa0117
		idx = p[0].lower()
		idx = idx[0:8]+"-"+idx[8:12] + "-" + idx[12:16] + "-"+idx[16:]
		out[idx]=p[1]
	return(out)
	
def replaceDuplicateLinesWithGOTO(lines):
	global finalSeenIDs
	out = []
	for line in lines:
		if "CHOICE" in line:
			choices = [replaceDuplicateLinesWithGOTO(choice) for choice in line["CHOICE"]]
			out.append({"CHOICE":choices})
		elif "_ID" in line:
			if line["_ID"] in finalSeenIDs:
				out.append({"GOTO":line["_ID"]})
				break # (or return(out)??)
			else:
				finalSeenIDs.append(line["_ID"])
				out.append(line)
		else:
			out.append(line)
	return(out)

def depthFirstToBreadthFirst(lines):
	# unfold two-choice structures
	# This is unfolding top-level stuff
	# e.g. see {"Global/HUBs/in1_chantry_mother": "My lord Inquisitor, it's good of you to speak with me.", "_ID": "2480b3f0-0ec1-4d90-adec-36c5c64622dd"}
	#  but not working recursively?
	# e.g. see "what a pleasure to meet ..." below,
	#  even though the code is reaching this deeper line???
	out = []
	for line in lines:
		if "CHOICE" in line:
			choices = line["CHOICE"]
			# Recursively apply
			choices = [depthFirstToBreadthFirst(choice) for choice in choices]
			# Deal with current level
			if len(choices)==2 and len(choices[1])>1:
# 				print(json.dumps(choices,indent=4))
# 				print(len(choices[0]))
# 				print(len(choices[1]))
# 				print("--")
				if choices[0][-1] == choices[1][1]:
					firstChoice = choices[0][:-1]
					secondChoice = choices[1][:1]
					out.append({"CHOICE": [firstChoice,secondChoice]})
					out += choices[1][1:]
# 				if choices[0][1]=={"FollowerPlots/Odette/odt_comte": "What a pleasure to meet you, my lady. Seeing the same faces at every event becomes so tiresome.", "_ID": "86206692-94aa-44f9-855f-416a8aaac56c"}:
# 					print(firstChoice)
# 					print(secondChoice)
# 					print(choices[1][1])
				else:
					out.append(line)
			else:
				out.append(line)
		else:
			out.append(line)	
	return(out)

# 
# def depthFirstToBreadthFirst(lines):
# 	# TODO: Reorder decisions from depth-first to breadth-first
# 	#  (move seenIDs to a process right at the very end)
# 	#  (but check whether convLinks allow you to visit the same
# 	#   lineID but end up in different childIDs?)
# 	# for choices, start from -1 of list and decrease to -[len shortest child]
# 	# find lowest number where all branches are identical: -x
# 	# split each list to [:-x] and [-x:]
# 	# Remove second half from each child 
# 	#   and += the second half onto the out
# 	
# 	def findCommonTail(choices):
# 		# Return index of tail that is identical across choices
# 		if len(choices)==1:
# 			return(None)
# 		choiceLengths = [len(x) for x in choices]
# 		if min(choiceLengths)==1:
# 			return(None)
# 		for i in [-x for x in range(1,min(choiceLengths)+1)]:
# 			ithChoice = [choice[i] for choice in choices]
# 			allIdentical = all([cx == ithChoice[0] for cx in ithChoice])
# 			if not allIdentical:
# 				if i==-1:
# 					return(None)
# 				return(i)
# 		# All identical?
# 		return(None)
# 	out = []
# 	for line in lines:
# 		if "CHOICE" in line:
# 			choices = line["CHOICE"]
# 			# Recursively apply
# 			choices = depthFirstToBreadthFirst(choices)
# 			# Deal with current level
# 			commonTail = findCommonTail(choices)
# 			if commonTail:
# 				print("HERE!")
# 				print(json.dumps(choices[0],indent=4))
# 				print(fghj)
# 				# Add unique parts to choices
# 				newChoices = []
# 				for choice in choices:
# 					newChoices.append(choice[:commonTail])
# 				out.append({"CHOICE":newChoices})
# 				# add common parts to coda
# 				out += choice[0][commonTail:]
# 			else:
# 				out.append(line)
# 		else:
# 			out.append(line)
# 	
# 	return(out)
# 	
# 	
# 	