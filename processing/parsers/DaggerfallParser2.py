from bs4 import BeautifulSoup
from igraph import *
import json, re, copy

# Todo: Track non-named NPCs and their gender
# TODO: Handle 'do' links  "repute with _gaffer_ exceeds 10 do _S.30_ "
# TODO: Handle "SAYING"

def cleanLine(txt):
	if txt.strip().startswith(">"):
		return("")
	txt = re.sub("^:","",txt)
	# don't include player input options
	txt = txt.strip()
	# Remove lines that start with parentheses and have nothing else
	txt = re.sub(r'^\([^)]*\)', '', txt)
	txt = txt.replace("...","... ")
	return(txt)
	
	
def processEvent(nodeID,charID="",visitedNodes=[],seenMIDs=[],doALL=True):
	out = []
	#print(("PR",nodeID,charID,seenMIDs))
	if nodeID in sIDToEventText:
		event = sIDToEventText[nodeID]
		#print(event)
		idx = event[:event.index(" ")].replace(":","")
		for line in [x.strip() for x in event.split("\n") if len(x.strip())>0 and x.strip().count(" ")>0]:
			comm = line[:line.index(" ")]
			if comm== "when" and doALL:
				# Link to another action, which might include who is talking
				sLinks = re.findall("when (_.+?_)",line) + re.findall("and (_.+?_)",line)
				for sLink in sLinks:
					#if not sLink in visitedNodes:
						ox,charIDX,vn,sx = processEvent(sLink,charID,copy.deepcopy(visitedNodes),seenMIDs,False)
						if charIDX!="":
							charID = charIDX
						visitedNodes.append(sLink)
					# Don't add output to out, just run the previous nodes
					# to get the character ID
			elif comm=="say" and doALL:
				# Say line of dialogue
				#print(("SAY",line,charID))
				if charID!="":
					mID = line[line.index(" ")+1:].strip()
					#print(("MID",mID))
					if mID in mIDToDialogue and not (mID in seenMIDs):
						mText = mIDToDialogue[mID]
						charName = charID
						if charID in idToName:
							charName = idToName[charID]
						out.append({charName:mText})
						seenMIDs.append(mID)
			elif comm=="clicked" or line.count(" clicked")>0:
				charIDX = ""
				if comm=="clicked":
					lx = line.strip().replace(" npc","")
					charIDX = lx[lx.index(" ")+1:].strip()
				else:
					charIDX = re.findall(" ([^ ]+?) clicked",line)[0]
			
				if charIDX.count(" ")>0:
					charIDX = charIDX[:charIDX.index(" ")]
				if len(charIDX)>0 and charIDX!="item":
					charID = charIDX
			elif comm=="prompt" and doALL:
				# Player choice
				mID,yesSID,noSID = re.findall("prompt ([^ ]+) yes ([^ ]+) no ([^ \n]+)",line)[0]
				# Char asks question
				charName = charID
				if charID in idToName:
					charName = idToName[charID]
		
				if mID=="QuestorOffer":
					out.append({charName:mIDToDialogue[mID],"_Type":"QuestorOffer"})
					#seenMessageIDs.append("QuestorOffer")
					yesResponse = []
					noResponse = []
					if "AcceptQuest" in mIDToDialogue:
						#print(("ACCEPTQUEST",nodeID,yesSID,charID))
						#yesResponse = [{charName:mIDToDialogue["AcceptQuest"],"_Type":"AcceptQuest"}]
						yesResponse,dummyCharID,vn,sx = processEvent(yesSID,charID,copy.deepcopy(visitedNodes))
						for ys in yesResponse:
							ys["_Type"] = "AcceptQuest"
						#visitedNodes += vn #(will duplicate, but that's ok)
					if "RefuseQuest" in mIDToDialogue:
						#noResponse =  [{charName:mIDToDialogue["RefuseQuest"],"_Type":"RefuseQuest"}]
						noResponse,dummyCharID,vn,sx = processEvent(noSID,charID,copy.deepcopy(visitedNodes),seenMIDs)
						for ns in noResponse:
							ns["_Type"] = "RefuseQuest"
						#visitedNodes += vn #(will duplicate, but that's ok)
					out.append({"CHOICE":[
							[{"PC":"Yes"}]+ yesResponse,
							[{"PC":"No" }]+noResponse]})
			
				else:
					if mID in mIDToDialogue:
						out.append({charName:mIDToDialogue[mID]})
						yesResponse,dummyCharID,vn,sx = processEvent(yesSID,charID,copy.deepcopy(visitedNodes),seenMIDs)
						#visitedNodes += vn #(will duplicate, but that's ok)
						noResponse,dummyCharID,vn,sx = processEvent(noSID,charID,copy.deepcopy(visitedNodes),seenMIDs)
						#visitedNodes += vn #(will duplicate, but that's ok)
						#visitedNodes = list(set(visitedNodes))
						out.append({"CHOICE":[
								[{"PC":"Yes"}]+yesResponse,
								[{"PC":"No" }]+noResponse]})
					#seenMessageIDs += yesMIDs + noMIDs
# 			elif line.count(" do ")>0:
# 				doSID = line[line.index(" do ")+4].strip()
# 				if not doSID in visitedNodes:
# 					noResponse,dummyCharID,vn,sx = processEvent(doSID,charID,copy.deepcopy(visitedNodes),seenMIDs)
# 					seenMIDs += sx
# 					visitedNodes += vn
	visitedNodes.append(nodeID)
	return((out,charID,visitedNodes,seenMIDs))
########### End Process Event #########


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

idToName = {}
mIDToDialogue = {}	
sIDToCharID = {}
sIDToMessageID = {}
sIDToEventText = {}

def parseFile(fileName,parameters={},asJSON=False):
	nameToGender = {}
	
	#print(fileName)
	questID = fileName[fileName.rindex("/")+1:].replace(".txt","").replace("$","_")

	o = open(fileName)
	d = o.read()
	o.close()

	d = d.replace("_\n_","_\n\n_")
	d = re.sub("\n +\n","\n\n",d)
	
	d = "\n".join([x for x in d.split("\n") if not x.startswith("--")])
	
	out = []
	#Dictionary of charIDs to charName
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
		idToName[pID] = pName
		if p.count(" male")>0:
			pGender = "male"
		if p.count(" female")>0:
			pGender = "female"
		nameToGender[pName] = pGender
	out.append({"GENDER":nameToGender})
	#print(idToName)
	
	# Messages (dialogue)
	messages = [x.strip() for x in d.split('\n\n') if x.strip().startswith("Message:") or any([x.startswith(y) for y in ["QuestorOffer","RefuseQuest","AcceptQuest"]])]
	
	# mID to Dialogue
	for m in messages:
		#print(m)
		if "\n" in m:
			txt = m[m.index('\n')+1:]
			txt = re.sub(" +"," ",txt.replace("<ce>"," ").replace("\n", " ")).strip()

			p1 = m[:m.index(":")]
			if p1 in ["QuestorOffer","RefuseQuest","AcceptQuest"]:
				mIDToDialogue[p1] = txt
			else:
				mnum = m[m.index(":")+1:].replace("[","").replace("]","").strip()
				mnum = mnum[:mnum.index("\n")].strip()		
				mIDToDialogue[mnum]=txt
	
	# Get dict of SIDs to "clicked" events (who is talking)
	# And dict of SIDs to message "say" events
	#events = [x.strip() for x in d.split("\n\n") if (x.strip().startswith("_") or x.strip().startswith("QuestorOffer:")) and x.count(":")>0]
	events = [x.strip() for x in d.split("\n\n") if x.count(" task:")>0]
	for event in events:
		event = re.sub("variable .+?\n","",event)
		sID = event[:event.index(" ")].replace(":","")
		sIDToEventText[sID] = event
		talkingTo = re.findall("clicked npc ([^ \n]+)",event)
		talkingTo += re.findall(" ([^ ]+?) clicked",event)
		if len(talkingTo)>0:
			sIDToCharID[sID] = talkingTo[-1]
		# Get messages
		sIDToMessageID[sID] =  re.findall("say ([0-9]+)",event)
	#print("CHAR")
	#print(sIDToCharID)
	
	visitedNodes = []
	seenMIDs = []
	for sID in list(sIDToEventText.keys()):
		if not sID in visitedNodes:
			outX,charID,visitedNodes,sm = processEvent(sID,"",visitedNodes,seenMIDs)
			seenMIDs += sm
			seenMIDs = list(set(seenMIDs))
			out += outX
	
# 			
# 	out = []
# 	seenMessageIDs = []
# 	# Parse events
# 	for event in events:
# 		idx = event[:event.index(" ")].replace(":","")
# 		charID = ""
# 		for line in [x.strip() for x in event.split("\n")]:
# 			comm = line[:line.index(" ")]
# 			if comm== "when":
# 				# Link to another action, which might include who is talking
# 				sLinks = re.findall("when (_.+?_)",line) + re.findall("and (_.+?_)",line)
# 				charLink = [sIDToCharID[l] for l in sLinks if l in sIDToCharID]
# 				if len(charLink)>0:
# 					charID = charLink[0]
# 			elif comm=="say":
# 				# Say line of dialogue
# 				if charID!="":
# 					mID = line[line.index(" ")+1:].strip()
# 					if mID in mIDToDialogue:
# 						mText = mIDToDialogue[mID]
# 						charName = charID
# 						if charID in idToName:
# 							charName = idToName[charID]
# 						out.append({charName:mText})
# 						seenMessageIDs.append(mID)
# 			elif comm=="clicked" or line.count(" clicked")>0:
# 				charIDX = ""
# 				if comm=="clicked":
# 					lx = line.strip().replace(" npc","")
# 					charIDX = lx[lx.index(" ")+1:].strip()
# 				else:
# 					print("NNNNNN")
# 					print(line)
# 					charIDX = re.findall(" ([^ ]+?) clicked",line)[0]
# 					
# 				if charIDX.count(" ")>0:
# 					charIDX = charIDX[:charIDX.index(" ")]
# 				if charIDX.count("_")>0:
# 					charID = charIDX
# 			elif comm=="prompt":
# 				print(line)
# 				# Player choice
# 				mID,yesSID,noSID = re.findall("prompt ([^ ]+) yes ([^ ]+) no ([^ \n]+)",line)[0]
# 				# Char asks question
# 				charName = charID
# 				if charID in idToName:
# 					charName = idToName[charID]
# 				
# 				if mID=="QuestorOffer":
# 					out.append({charName:mIDToDialogue[mID],"_Type":"QuestorOffer"})
# 					seenMessageIDs.append("QuestorOffer")
# 					yesResponse = []
# 					noResponse = []
# 					if "AcceptQuest" in mIDToDialogue:
# 						yesResponse = [{charName:mIDToDialogue["AcceptQuest"],"_Type":"AcceptQuest"}]
# 					if "RefuseQuest" in mIDToDialogue:
# 						noResponse =  [{charName:mIDToDialogue["RefuseQuest"],"_Type":"RefuseQuest"}]
# 					out.append({"CHOICE":[
# 							[{"PC":"Yes"}]+ yesResponse,
# 							[{"PC":"No" }]+noResponse]})
# 					
# 				else:
# 					out.append({charName:mIDToDialogue[mID]})
# 					seenMessageIDs.append("mID")
# 					yesMIDs = sIDToMessageID[yesSID]
# 					noMIDs = sIDToMessageID[noSID]
# 					yesResponse = [{charName:mIDToDialogue[mID]} for mID in yesMIDs]
# 					noResponse = [{charName:mIDToDialogue[mID]} for mID in noMIDs]
# 					out.append({"CHOICE":[
# 							[{"PC":"Yes"}]+yesResponse,
# 							[{"PC":"No" }]+noResponse]})
# 					seenMessageIDs += yesMIDs + noMIDs
# 			elif comm=="do":
# 				pass
# 
# 		# If quest start hasn't been entered, add those.
# 		if not "QuestorOffer" in seenMessageIDs:
# 			charName = ""
# 			if "QuestorOffer" in sIDToMessageID:
# 				sid = sIDToMessageID["QuestorOffer"]
# 				if sid in sIDToCharID:
# 					charID = sIDToCharID[sid]
# 					charName = charID
# 					if charID in idToName:
# 						charName = idToName[charID]
# 			elif "_qgiver_" in idToName:
# 				charName = idToName["_qgiver_"]
# 				
# 			if charName!="":
# 				out.append({charName:mIDToDialogue["QuestorOffer"],"_Type":"QuestorOffer"})
# 				seenMessageIDs.append("QuestorOffer")
# 				yesResponse = []
# 				noResponse = []
# 				if "AcceptQuest" in mIDToDialogue:
# 					yesResponse = [{charName:mIDToDialogue["AcceptQuest"],"_Type":"AcceptQuest"}]
# 				if "RefuseQuest" in mIDToDialogue:
# 					noResponse =  [{charName:mIDToDialogue["RefuseQuest"],"_Type":"RefuseQuest"}]
# 				out = out + [{"CHOICE":[
# 						[{"PC":"Yes"}]+ yesResponse,
# 						[{"PC":"No" }]+noResponse]}]
		
				
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)