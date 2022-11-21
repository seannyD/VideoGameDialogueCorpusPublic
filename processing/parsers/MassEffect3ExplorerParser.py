# TODO: Post-process each conv to remove redundant links
#   see checkConv() function

# TODO: ME1: something wrong with parsing file/conv names.

from bs4 import BeautifulSoup
import json,re,csv


# def cleanText(t):
# 	t = t.replace("’","'").replace("“",'"').replace("”",'"').replace("…", " ... ")
# 	# Replace curled brackets to avoid counting descriptions as words
# 	# {"Shepard": "{Heavy surprised gasp 4}", "_ID": "610205"},
# 	t = t.replace("{","(")
# 	t = t.replace("}",")")
# 	return(t)


def parseFile(fileName,parameters={},asJSON=False):

	def cleanDialogue(txt):
		txt = txt.replace('"','')
		txt = txt.replace("{","(")
		txt = txt.replace("}",")")
		txt = txt.strip()
		return(txt)



	def loadPlotDatabase(folder):
		o = open(folder + "/plotDatabase.txt")
		txt = o.read()
		o.close()
		txt = txt.replace("/","/")
	
		condBits = txt.split("<conditional ")[1:-1]
		condDatabase = {}
		for condBit in condBits:
			condID = condBit[condBit.index("=")+2:condBit.index(">")-1].strip()
			condDesc = condBit[condBit.index("<description>")+13:condBit.index("</description")]
			condDatabase[condID] = condDesc
		
		transBits = txt.split("<state_transition ")[1:-1]
		transDatabase = {}
		for transBit in transBits:
			transID = transBit[transBit.index("=")+2:transBit.index(">")-1].strip()
			transDesc = transBit[transBit.index("<description>")+13:transBit.index("</description")]
			transDatabase[transID] = transDesc
		
		boolBits = txt.split("<value ")[1:-1]
		boolDatabase = {}
		for boolBit in boolBits:
			boolID = boolBit[boolBit.index("=")+2:boolBit.index(">")-1].strip()
			boolDesc = boolBit[boolBit.index("<description>")+13:boolBit.index("</description")]
			boolDatabase[boolID] = boolDesc

		# Character lists
		charBits = txt.split("<character ")[1:]
		charIDToFriendlyName = {}
		for charBit in charBits:
			friendlyName = charBit[charBit.index("=")+2:charBit.index(">")-1].strip()
			friendlyName = friendlyName.replace("&quot;",'"')
			tags = re.findall('<actor_tag>(.+?)</actor_tag>', charBit)
			for tag in tags:
				charIDToFriendlyName[tag] = friendlyName
				
		#allCharNames = list(set([x for x in charIDToFriendlyName.values()]))
		#for ax in allCharNames:
		#	print(ax)
#		o = open(folder + "/../charIDs.txt",'w')
#		o.write("\n".join(['\t"' + x + '":"' + charIDToFriendlyName[x] + '"' for x in charIDToFriendlyName]))
#		o.close()

		# extra parts:
		# (Abandoned for now because the format is weird)
# 		b2 = open(folder + "/bools.txt").read()
# 		for x in ["name:","id:","categories:","Note:","ints:","bools:"]:
# 			b2 = b2.replace(x,'"'+x[:-1]+'":')
# 		b2 = b2.replace(",\n}","\n}")
# 		bools2 = json.loads(b2)
# 		print(bools2)
# 		print(naskj)
		

		return((charIDToFriendlyName,condDatabase,transDatabase,boolDatabase))

	def loadConversationOwnerData(folder):
		convOwners = {}
		with open(folder+"/../DialogueOwners.csv") as csvfile:
			creader = csv.reader(csvfile)
			for row in creader:
				conv = row[0]
				owner = row[1]
				convFile = row[2].lower()
				
				convOwners[conv] = owner
		return(convOwners)
		
	def getOwner(convFile,conv):
		global convOwners
		if conv in convOwners:
			return(convOwners[conv])
		else:
			ownerClues = {
				"kaid": "Kaidan Alenko",
				"kelly": "Kelly Chambers",
				"joker": "Jeff \"Joker\" Moreau",
				"liara": "Liara T'soni",
				"garrus": "Garrus Vakarian",
				"gianna": "Gianna Parasini",
				"tali": "Tali'Zorah",
				"edi": "EDI",
				"warden": "Warden Kuril"
			}
			clue = conv.split("_")[1]
			if clue in ownerClues:
				return(ownerClues[clue])
		return("owner")
		
	def getDialogue(node,owner):
		global charIDToFriendlyName
		dial = None
		if len(node["DialogueLine"])>0 and node["DialogueLine"]!="No Data":
			charName = node["SpeakerName"]
			# Try to find owner
			if charName == "owner":
				charName = owner
			# convert to friendly
			if charName in charIDToFriendlyName:
				charName = charIDToFriendlyName[charName]
				
			# If there's still no owner
			if charName == "owner" or charName == "no_owner":	
				charName = "owner_" + node["convName"]
			
			dial = {charName: cleanDialogue(node["DialogueLine"]), "_ID":node["LineStrRef"]}
		elif len(node["StageDirection"])>1:
			dial = {"ACTION": cleanDialogue(node["StageDirection"]), "_ID":node["LineStrRef"]}
		return(dial)
		
		
	def getLinks(node):
		links = node["Link"]
		lx = [x for x in links.split(";") if len(x.strip())>0]
		links = []
		for l in lx:
			if l.count(":")>0:
				links.append(re.split("([0-9][0-9][0-9]+):",l)[1:])
			else:
				links.append([l])
		#links = [x.split(":") for x in links]
		return(links)
		
	def huntNextSpeaker(lineStrRef,lines,owner):
		global charIDToFriendlyName
		node = [x for x in lines if x["LineStrRef"]==lineStrRef][0]
		dx = cleanDialogue(node["DialogueLine"]).replace("No data","")
		if len(dx)>0:
			charName = node["SpeakerName"]
			# TODO - add convName to owner
			if charName.startswith("owner"):
				return(owner)
			else:
				if charName in charIDToFriendlyName:
					charName = charIDToFriendlyName[charName]
				else:
					charName = "Next speaker"
				return(charName)
		else:
			links = getLinks(node)
			if len(links)>1 or len(links)==0:
				return(None)
			else:
				return(huntNextSpeaker(links[0][0],lines,owner))
			
	
	def followNode(node,lines,owner):
		global visitedNodes
		global ownersNotFoundLines
		
		if node["LineStrRef"] in visitedNodes:
			return([{"GOTO":node["LineStrRef"]}])
		
		visitedNodes.append(node["LineStrRef"])
		
		ret = []
		dialogue = getDialogue(node,owner)
		if not dialogue is None:
			ret.append(dialogue)
			spkx = [x for x in dialogue if not x.startswith("_")][0]
			if spkx.lower().startswith("owner"):
				if len(ownersNotFoundLines)>0 and len(ownersNotFoundLines[-1]) <4:
					ownersNotFoundLines[-1].append(dialogue[spkx])
		else:
			# Node is routing node without dialogue or stage directions.
			# These are sometimes used as GOTO points in conditionals
			# It's possible that not all of them are used, so could be post-processed
			ret.append({"ACTION":"", "_ID":node["LineStrRef"]})
		links = getLinks(node)
		if len(links)==1:
			nextNode = [x for x in lines if x["LineStrRef"]==links[0][0]]
			if len(nextNode)>0:
				ret += followNode(nextNode[0],lines,owner)
		else:
			choice = []
			for link in links:
				nextNode = [x for x in lines if x["LineStrRef"]==link[0]]
				if len(nextNode)>0:
					condition = []
					if len(link)>1:
						if link[1].count("REPLY_")>0:
							# "Liara's mother\"(REPLY_CATEGORY_INVESTIGATE)"
							#print(link)
							# Some links have parentheses in the text, so need re
							# '"(Shoot him.)"(REPLY_CATEGORY_DISAGREE)'
							guiPrompt, replyCategory = re.split("\\(REPLY",link[1])
							if guiPrompt != "No Data":
								replyCategory = replyCategory.replace(")","")
								# (the "REPLY" part should be cut by the split above)
								replyCategory = replyCategory.replace("_CATEGORY_","")
								condition = [{"ACTION":replyCategory,
												"_PROMPT":guiPrompt}]
						else:
							condID,condVar = link[1].replace("(","").replace(")","").split("/")
							condDescription = ""
							if condID in condDatabase:
								condDescription = condDatabase[condID]
								if condDescription == "Speaker is in party":
									nextSpeaker = huntNextSpeaker(link[0],lines,owner)
									if nextSpeaker is None:
										condDescription = "Next speaker is in party"
									else:
										condDescription = nextSpeaker + " is in party"
							elif condID in boolDatabase:
								condDescription = boolDatabase[condID]
							condition = [{"STATUS": condDescription.strip() + " (" + condID + "/" + condVar.strip() + ")" }]
					choice.append(condition + followNode(nextNode[0],lines,owner))
			if len(choice)>0:
				ret.append({"CHOICE":choice})
		return(ret)
		
	def parseConv(lines,owner):
		global visitedNodes
		visitedNodes = []
		startNodes = [n for n in lines if n["NodeType"]=="start"]
		outx = []
		for startNode in startNodes:
			outx += followNode(startNode,lines,owner)
			outx.append({"ACTION":"---"})
		return(outx)
		
	def checkConv(outx):
		gotoIDs = [x for x in getAllProps(outx,"GOTO")]
		allIDs = [x for x in getAllProps(outx,"_ID")]
		print("All GOTOs in Line Refs: " + str(all([x in allIDs for x in gotoIDs])))
		lineStrRefsToRemove = [x["_ID"] for x in outx if "_ID" in x and x["_ID"] in gotoIDs and "ACTION" in x and x["ACTION"]==""]
		print("Redundant")
		print(lineStrRefsToRemove)
		return(lineStrRefsToRemove)
	
	def getAllProps(outx,prop):
		if isinstance(outx,list):
			for line in outx:
				if "CHOICE" in line:
					for choice in line["CHOICE"]:
						yield from getAllProps(choice,prop)
				else:
					if prop in line:
						yield(line[prop])
		
	folder = fileName[:fileName.rindex("/")]
	global charIDToFriendlyName,condDatabase
	charIDToFriendlyName,condDatabase,transDatabase,boolDatabase = loadPlotDatabase(folder)
	
	global convOwners
	convOwners = loadConversationOwnerData(folder)
	
	d = []
	header = []
	with open(fileName) as csvfile:
		csvreader = csv.reader(csvfile,dialect=csv.excel)
		for row in csvreader:
			if len(header)==0:
				for cell in row:
					if cell=='\ufefffilename':
						header.append("filename")
					else:
						header.append(cell)
			else:
				dx = {}
				for h in header:
					dx[h] = row[header.index(h)]
				d.append(dx)
				
	# just first conv for testing
#	cnx = list(set([x["convName"] for x in d]))
#	d = [x for x in d if x["convName"] in cnx[:2]]

	# Filter files that we don't want to process (like multiplayer files)
	if "avoidConvIDs" in parameters:
		d = [x for x in d if not x["convName"] in parameters["avoidConvIDs"]]

	convs = list(set([x["filename"]+': ' + x["convName"] for x in d if (x["filename"].count("_INT")>0)]))
	if len(convs)==0:
		# ME 1
		convs = list(set([x["filename"]+': ' + x["convName"] for x in d]))
#	fnSubs = list(set([x["filename"].split("_")[-1] for x in d]))
#	print(fnSubs)
#	print(ndsjnk)
	
	out = []
	global visitedNodes
	visitedNodes = []
	
	ownersNotFound = []
	global ownersNotFoundLines
	ownersNotFoundLines = []
	
	for conv in convs:
		lines = [x for x in d if (x["filename"]+': ' + x["convName"] == conv) and (x["filename"].count("_INT")>0)]
		if len(lines)==0:
			# ME1 file names
			lines = [x for x in d if (x["filename"]+': ' + x["convName"] == conv)]
		fn = lines[0]["filename"].replace("_LOC_INT.pcc","").lower()
		#print((fn,len(lines)))
		owner = getOwner(fn, lines[0]["convName"])
		# TODO - change to owner + convName
		if  owner.lower().startswith("owner_") or owner.lower().startswith("not found") or owner.lower().startswith("no_owner"):
			owner = "owner_" + lines[0]["convName"]
			ownersNotFound.append((lines[0]["filename"],lines[0]["convName"]))
			ownersNotFoundLines.append([])
			
		
		# Sometimes the player is controlling other characters
		if "MainCharacterOverride" in parameters:
			convMini = conv[conv.index(":")+2:]
			if convMini in parameters["MainCharacterOverride"]:
				for line in lines:
					line["SpeakerName"] = line["SpeakerName"].replace("Shepard",parameters["MainCharacterOverride"][convMini])
					line["SpeakerFriendlyName"] = line["SpeakerFriendlyName"].replace("Shepard",parameters["MainCharacterOverride"][convMini])
		
		out.append({"LOCATION":conv})
		convOut = parseConv(lines,owner)
		#checkConv(convOut)
		out += convOut
		
	# Print list of lines we need to check
	ownersToCheckOut = '"file","conversation","name","gender","Line1","Line2","Line3"\n'
	for i in range(len(ownersNotFound)):
		if len(ownersNotFoundLines[i])>0:
			if len("".join(ownersNotFoundLines[i]))>0:
				ownersToCheckOut += ownersNotFound[i][0] + "," + ownersNotFound[i][1] + ",,," + '"' + '","'.join(ownersNotFoundLines[i])+'"\n'
	
	o = open(folder + "/../OwnersToCheck.csv",'w')
	o.write(ownersToCheckOut)
	o.close()
			
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)











