from bs4 import BeautifulSoup
from igraph import *
import json, re, copy

def cleanLine(txt):
	# put keywords in parentheses so they're taken out of the analysis later on
	txt = re.sub("([_=]+.+?[_])","(\\1)",txt)
	txt = re.sub("(%[a-z]+)","(\\1)",txt)
	txt = txt.replace("...","... ")
	txt = txt.strip()
	txt = re.sub(" +"," ",txt)
	return(txt)
	

def postProcessing(out):
	out2 = []
	gender = {}
	for o in out:
		if "GENDER" in o:
			for k,v in o["GENDER"].items():
				try:
					gender[v].append(k)
				except:
					gender[v] = [k]
		else:
			out2.append(o)
			
	for x in gender:
		gender[x] = list(set(gender[x]))
	o = open("../data/ElderScrolls/Daggerfall/autoGender.json",'w')
	o.write(json.dumps(gender))
	o.close()
	return(out2)

def getNameToGender(d,questID):
	nameToGender = {}
	idToName = {}
	people = [x for x in d.split("\n") if x.strip().startswith("Person")]
	for p in people:
		p = p.strip()
		pID = p[p.index(" ")+1:].strip()
		pID = pID[:pID.index(" ")].strip()
		pName = pID
		pGender = ""
		if p.count(" named ")>0:
			#print(p+"<<")
			pName = re.findall("named ([^ \n]+)",p)[0].replace("_"," ")
			#print(">>>"+pName)
			pGender = "NAMED"
		else:
			pName = questID+"#"+pName
			# Make sure names don't start with "_"
			pName = re.sub("^_","",pName)
		idToName[pID] = pName
		if p.count(" male")>0:
			pGender = "male"
		if p.count(" female")>0:
			pGender = "female"
		nameToGender[pName] = pGender
		
		if p.count(" Questor"):
			idToName["Questor"] = pName
			nameToGender["Questor"] = pGender
		
	return(nameToGender,idToName)
	
	
def getMIDToDialogue(d):

	QMessageLabels = ["QuestorOffer","RefuseQuest","AcceptQuest","QuestComplete","QuestorPostfailure","QuestorPostsuccess","QuestFail",""]

	mIDToDialogue = {}
	messages = [x.strip() for x in d.split('\n\n') if x.strip().startswith("Message:") or any([x.startswith(y) for y in QMessageLabels])]
	
	questOfferMID = []
	
	prevMNum = ""
	# mID to Dialogue
	for m in messages:
		#print(m)
		if "\n" in m:
			txt = m[m.index('\n')+1:]
			txt = re.sub(" +"," ",txt.replace("<ce>"," ").replace("\n", " ")).strip()
			p1 = ""
			if m.count(":") > 0:
				p1 = m[:m.index(":")]
				if p1 in QMessageLabels:
					mIDToDialogue[p1] = txt
					if p1=="QuestorOffer":
						questOfferMID.append("QuestorOffer")
			# Also add duplicate message linked to mid
			mnum = ""
			if m.count(":")==0:
				mnum = prevMNum
			else:
				mnum = m[m.index(":")+1:].replace("[","").replace("]","").strip()
				if mnum.count("\n")>0:
					mnum = mnum[:mnum.index("\n")].strip()
				else:
					mnum = mnum.strip()
				prevMNum = mnum
				if p1=="QuestorOffer":
					questOfferMID.append(mnum)
			mIDToDialogue[mnum]=txt
	return((mIDToDialogue,questOfferMID))

def getCharacterFromClicked(line):
	charIDX = ""
	comm = line[:line.index(" ")]
	if comm=="clicked":
		lx = line.strip().replace(" npc","")
		charIDX = lx[lx.index(" ")+1:].strip()
	else:
		charIDX = re.findall(" ([^ ]+?) clicked",line)[0]

	if charIDX.count(" ")>0:
		charIDX = charIDX[:charIDX.index(" ")]
	return(charIDX)
	
def getEventDicts(events):
	sIDToCharID = {}
	sIDToMessageID = {}
	for event in events:
		event = re.sub("variable .+?\n","",event)
		idx = event[:event.index(" ")].replace(":","")
		for line in [x.strip() for x in event.split("\n") if len(x.strip())>0 and x.strip().count(" ")>0]:
			comm = line[:line.index(" ")]
			if comm=="clicked" or line.count(" clicked")>0:
				charIDX = getCharacterFromClicked(line)
				if len(charIDX)>0 and charIDX!="item":
					sIDToCharID[idx] = charIDX
			if comm=="say":
				mID = line[line.index(" ")+1:].strip()
				try:
					sIDToMessageID[idx].append(mID)
				except:
					sIDToMessageID[idx] = [mID]
	return(sIDToCharID,sIDToMessageID)
	
def getCharName(charID,idToName):
	charName = charID
	if charID in idToName:
		charName = idToName[charID]
	return(charName)
	
def getPrompt(line, charID, mIDToDialogue, idToName,sIDToMessageID, seenQuestorOffer, questOfferMID):
	# Player choice
	mID,yesSID,noSID = re.findall("prompt ([^ ]+) yes ([^ ]+) no ([^ \n]+)",line)[0]
	
	if mID in questOfferMID:
		seenQuestorOffer = True
	
	# Char asks question
	charName = getCharName(charID,idToName)
	outX = []
	if mID=="QuestorOffer" and mID in list(mIDToDialogue.keys()):
		off = messageToOut(charName,mIDToDialogue[mID])
		off["_Type"] = "QuestorOffer"
		outX.append(off)
		#seenMessageIDs.append("QuestorOffer")
		yesResponse = []
		noResponse = []
		if "AcceptQuest" in mIDToDialogue:
			yesResponse = messageToOut(charName,mIDToDialogue["AcceptQuest"])
			yesResponse["_Type"] = "AcceptQuest"
		if "RefuseQuest" in mIDToDialogue:
			noResponse = messageToOut(charName,mIDToDialogue["RefuseQuest"])
			noResponse["_Type"] = "RefuseQuest"
		outX.append({"CHOICE":[
				[{"PC":"Yes"}, yesResponse],
				[{"PC":"No" },  noResponse]]})
	else:
		if mID in mIDToDialogue:
			outX.append(messageToOut(charName,mIDToDialogue[mID]))
			# TODO: we have an SID, but need to find message
			yesTxt = ""
			noTxt = ""
			if yesSID in sIDToMessageID:
				yesTxt = " ".join([mIDToDialogue[x] for x in sIDToMessageID[yesSID] if x in mIDToDialogue])
			if noSID in sIDToMessageID:
				noTxt = " ".join([mIDToDialogue[x] for x in sIDToMessageID[noSID] if x in mIDToDialogue])
			#yesResponse = [{charName:yesTxt}]	
			#noResponse =  [{charName:noTxt}]
			yesResponse = [messageToOut(charName,yesTxt)]	
			noResponse =  [messageToOut(charName,noTxt)]
			outX.append({"CHOICE":[
					[{"PC":"Yes"}]+yesResponse,
					[{"PC":"No" }]+noResponse]})
	return((outX,seenQuestorOffer))
	
	
def messageToOut(charName,txt):
	if charName == "":
		charName = "Unknown"
	if(txt.count("<--->")==0):
		if txt.startswith("Error:"):
			return({charName: "(no text)"})	
		else:
			return({charName:cleanLine(txt)})
	else:
		return({"CHOICE":[[{charName:cleanLine(bit)}] for bit in txt.split("<--->")]})

###############
	
def parseFile(fileName,parameters={},asJSON=False):

	questID = fileName[fileName.rindex("/")+1:].replace(".txt","").replace("$","_")
	
	o = open(fileName)
	d = o.read()
	o.close()

	d = d.replace("_\n_","_\n\n_")
	d = re.sub("\n +\n","\n\n",d)
	
	d = "\n".join([x for x in d.split("\n") if not x.startswith("--")])
	out = []	
	#Dictionary of charIDs to charName
	nameToGender,idToName = getNameToGender(d,questID)
	out.append({"GENDER":nameToGender})
	
	# Messages (dialogue)
	mIDToDialogue,questOfferMID = getMIDToDialogue(d)
	
	events = [x.strip() for x in d.split("\n\n") if x.count(" task:")>0]	
	sIDToCharID,sIDToMessageID = getEventDicts(events)
	
	seenQuestorOffer = False
	for event in events:
		charID = ""
		event = re.sub("variable .+?\n","",event)
		idx = event[:event.index(" ")].replace(":","")
		for line in [x.strip() for x in event.split("\n") if len(x.strip())>0 and x.strip().count(" ")>0]:
			comm = line[:line.index(" ")]
			if comm=="clicked" or line.count(" clicked")>0:
				charIDX = getCharacterFromClicked(line)
				if len(charIDX)>0 and charIDX!="item":
					charID = charIDX
			if comm== "when":
				# Link to another action, which might include who is talking
				sLinks = re.findall("when (_.+?_)",line) + re.findall("and (_.+?_)",line)
				charIDXs = [sIDToCharID[x] for x in sLinks if x in sIDToCharID]
				if len(charIDXs)>0:
					charID = charIDXs[-1]
			if comm=="say":
				mID = line[line.index(" ")+1:].strip()
				if charID!="":
					charName = getCharName(charID,idToName)
					if mID in mIDToDialogue:
						#out.append({charName: mIDToDialogue[mID]})
						out.append(messageToOut(charName,mIDToDialogue[mID]))
					else:
						print(questID+ ": Can't find mID "+mID)
			if line.count("saying"):
				if charID!="":
					charName = getCharName(charID,idToName)
					saysMID = line[line.index("saying ")+7:].strip()
					if saysMID in mIDToDialogue:
						#out.append({charName: mIDToDialogue[saysMID]})
						out.append(messageToOut(charName,mIDToDialogue[saysMID]))								
			if comm=="prompt":
				prompt,seenQuestorOffer = getPrompt(line, charID, mIDToDialogue, idToName,sIDToMessageID,seenQuestorOffer,questOfferMID)
				if len(prompt)>0:
					out += prompt

	if not seenQuestorOffer:
		# We haven't seen a 'clicked' event that's led to a questor offer
		# So try to guess the questor
		charID = ""	
		if "Questor" in idToName:
			# Questor is identified in person ref
			charID = "Questor"
		else:
			addQuestor = re.findall("add (.+?) as questor",d)
			if len(addQuestor)>0:
				# Questor is explicitly added
				charID = addQuestor[0]
			else:
				if len(list(idToName.keys()))==1:
					# There's only one person
					charID = list(idToName.keys())[0]
		
		if charID!="":
			qofferD,seenQuestorOffer = getPrompt("prompt QuestorOffer yes AcceptQuest no RefuseQuest", charID, mIDToDialogue, idToName,sIDToMessageID,seenQuestorOffer,questOfferMID)
			out = qofferD+out
		else:
			print("No quest offer for "+questID)
				
	out.append({"ACTION": "---"})
	
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)