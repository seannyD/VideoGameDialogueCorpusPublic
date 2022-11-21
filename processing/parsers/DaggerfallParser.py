from bs4 import BeautifulSoup
from igraph import *
import json, re

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
	
	
def processEvent(nodeID,charID="",visitedNodes=[]):
	out = []
	if nodeID in sIDToEventText:
		event = sIDToEventText[nodeID]
		idx = event[:event.index(" ")].replace(":","")
		print("PROCESS ----------")
		print(event)
		print("VN")
		print(nodeID,visitedNodes)
		for line in [x.strip() for x in event.split("\n")]:
			comm = line[:line.index(" ")]
			if comm== "when":
				# Link to another action, which might include who is talking
				sLinks = re.findall("when (_.+?_)",line) + re.findall("and (_.+?_)",line)
				for sLink in sLinks:
					if not sLink in visitedNodes:
						ox,charID,vn = processEvent(sLink,charID,visitedNodes)
					# Don't add output to out, just run the previous nodes
					# to get the character ID
			elif comm=="say":
				# Say line of dialogue
				if charID!="":
					mID = line[line.index(" ")+1:].strip()
					if mID in mIDToDialogue:
						mText = mIDToDialogue[mID]
						charName = charID
						if charID in idToName:
							charName = idToName[charID]
						out.append({charName:mText})
						#seenMessageIDs.append(mID)
			elif comm=="clicked" or line.count(" clicked")>0:
				charIDX = ""
				if comm=="clicked":
					lx = line.strip().replace(" npc","")
					charIDX = lx[lx.index(" ")+1:].strip()
				else:
					print("NNNNNN")
					print(line)
					charIDX = re.findall(" ([^ ]+?) clicked",line)[0]
			
				if charIDX.count(" ")>0:
					charIDX = charIDX[:charIDX.index(" ")]
				if charIDX.count("_")>0:
					charID = charIDX
			elif comm=="prompt":
				print(line)
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
						#yesResponse = [{charName:mIDToDialogue["AcceptQuest"],"_Type":"AcceptQuest"}]
						yesResponse,dummyCharID,vn = processEvent(yesSID,charID,visitedNodes)
						visitedNodes += vn #(will duplicate, but that's ok)
					if "RefuseQuest" in mIDToDialogue:
						#noResponse =  [{charName:mIDToDialogue["RefuseQuest"],"_Type":"RefuseQuest"}]
						noResponse,dummyCharID,vn = processEvent(noSID,charID,visitedNodes)
						visitedNodes += vn #(will duplicate, but that's ok)
					out.append({"CHOICE":[
							[{"PC":"Yes"}]+ yesResponse,
							[{"PC":"No" }]+noResponse]})
			
				else:
					out.append({charName:mIDToDialogue[mID]})
					#seenMessageIDs.append("mID")
					yesMIDs = sIDToMessageID[yesSID]
					noMIDs = sIDToMessageID[noSID]
					#yesResponse = [{charName:mIDToDialogue[mID]} for mID in yesMIDs]
					#noResponse = [{charName:mIDToDialogue[mID]} for mID in noMIDs]
					yesResponse,dummyCharID,vn = processEvent(yesSID,charID,visitedNodes)
					visitedNodes += vn #(will duplicate, but that's ok)
					noResponse,dummyCharID,vn = processEvent(noSID,charID,visitedNodes)
					visitedNodes += vn #(will duplicate, but that's ok)
					out.append({"CHOICE":[
							[{"PC":"Yes"}]+yesResponse,
							[{"PC":"No" }]+noResponse]})
					#seenMessageIDs += yesMIDs + noMIDs

	visitedNodes.append(nodeID)
	return((out,charID,visitedNodes))
########### End Process Event #########

def walkGraph(nodeID,g,visitedNodes,out,charID):
	if not nodeID in visitedNodes:
		visitedNodes.append(nodeID)
		ox,charID,vn = processEvent(nodeID,charID,visitedNodes)
		out += ox
		visitedNodes += vn
		reachableNodes = [g.vs[x]["name"] for x in g.neighbors(nodeID, mode="out")]
		for rNode in reachableNodes:
			visitedNodes,ox = walkGraph(rNode,g,visitedNodes,out,charID)
			out += ox
	return((visitedNodes,out))


idToName = {}
nameToGender = {}
mIDToDialogue = {}	
sIDToCharID = {}
sIDToMessageID = {}
sIDToEventText = {}

def parseFile(fileName,parameters={},asJSON=False):
	print(fileName)
	questID = fileName[fileName.rindex("/")+1:].replace(".txt","").replace("$","_")
	
	o = open(fileName)
	d = o.read()
	o.close()

	d = d.replace("_\n_","_\n\n_")
	d = re.sub("\n +\n","\n\n",d)
		
	#Dictionary of charIDs to charName
	people = [x for x in d.split("\n") if x.strip().startswith("Person")]
	for p in people:
		p = p.strip()
		pID = p[p.index(" ")+1:].strip()
		pID = pID[:pID.index(" ")].strip()
		pName = pID
		pGender = ""
		if p.count(" named ")>0:
			print(p+"<<")
			pName = re.findall("named ([^ \n]+)",p)[0].replace("_"," ")
			print(">>>"+pName)
			pGender = "NAMED"
		if pName.startswith("_"):
			pName = questID+"#"+pName
		idToName[pID] = pName
		if p.count(" male")>0:
			pGender = "male"
		if p.count(" female")>0:
			pGender = "female"
		nameToGender[pID] = pGender

	print(idToName)
	
	# Messages (dialogue)
	messages = [x.strip() for x in d.split('\n\n') if x.strip().startswith("Message:") or any([x.startswith(y) for y in ["QuestorOffer","RefuseQuest","AcceptQuest"]])]
	
	# mID to Dialogue
	for m in messages:
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
	print("CHAR")
	print(sIDToCharID)
	
	graphLinks = []
	
	for event in events:
		idx = event[:event.index(" ")].replace(":","")
		for line in [x.strip() for x in event.split("\n")]:
			comm = line[:line.index(" ")]
			if comm== "when":
				# Link to another action, which might include who is talking
				sLinks = re.findall("when (_.+?_)",line) + re.findall("and (_.+?_)",line)
				graphLinks += [(x,idx) for x in sLinks]
			elif comm=="prompt":
				# Keep in mind this could be questor offer/accept/reject
				mID,yesSID,noSID = re.findall("prompt ([^ ]+) yes ([^ ]+) no ([^ \n]+)",line)[0]
				graphLinks.append((idx,yesSID))
				graphLinks.append((idx,noSID))
				
	g = Graph(directed=True)
	g.add_vertices(list(set([x[0] for x in graphLinks] + [x[1] for x in graphLinks])))
	g.add_edges(graphLinks)
	print(g)
	import igraph as ig
	#g.vs["label"] = g.vs["name"]
	#ig.plot(g)
	
	components = g.components(mode="weak")
	print(components)
	out = []
	for component in components:
		# Find component with no in-degree
		print("COMP")
		print(component)
		print([g.vs[x]["name"] for x in component if g.vs[x].indegree()==0])
		
		startingNodes = [g.vs[x]["name"] for x in component if g.vs[x].indegree()==0]
		visitedNodes = []
		for nodeID in startingNodes:
			visitedNodes,ox = walkGraph(nodeID,g,visitedNodes,[],charID="")
			out += ox
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