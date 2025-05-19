import sqlite3, re

# TODO: Add checks and condition strings.
# TODO: Remove redundant SYSTEM IDs

def parseFile(fileName,parameters={},asJSON=False):

	def findStart(convo):
		for lineID in convo:
			lx = convo[lineID]
			if lx["title"]=="START":
				return(lineID)

	def cleanLine(txt):
		# There are some very long numbers, and these break the hyphenator!
		txt = re.sub("([0-9]{10})[0-9]+","\\1...",txt)
		return(txt)


	def splitDialogueAndDescription(txt,charName,idx):
		# "\"So, like...\" The girl on the ice looks up at you. \"Seriously, what's eating you, man?\""
		parts = re.split('(".+?")',txt)
		out = []
		for part in parts:
			if len(part)>0:
				if part.startswith('"') or len(parts)<=3:
					# includes dialogue and internal dialogue (with no quotes)
					out.append({charName: part.replace('"',"").strip()})
				else:
					out.append({"Narrator": part.strip()})
		out[0]["_ID"] = idx
		return(out)
			
			

	def dentry2DialogueLine(dentry):
		dTitle = dentry["title"]
		charName = "SYSTEM"
		if dTitle.count(":")>0:
			charName = dTitle[:dTitle.index(":")].strip()
		txt = dentry["dialoguetext"]
		txt = cleanLine(txt)
		#print(dentry)
		idx = str(dentry["conversationid"]) + "_" + str(dentry["id"])
		dialogueParts = splitDialogueAndDescription(txt,charName,idx)
		return(dialogueParts)
	
	# Connect to database
	temp_db = sqlite3.connect(fileName)
	temp_db.row_factory = sqlite3.Row
	dentries = temp_db.execute("SELECT * FROM dentries").fetchall()
	
	# List of dialogue entries (with dialogue text)
	list_accumulator = []
	for item in dentries:
		list_accumulator.append({k: item[k] for k in item.keys()})
	
	convoDict = {}
	for line in list_accumulator:
		convoID = line["conversationid"]
		lineID = line["id"]
		if not convoID in convoDict:
			convoDict[convoID] = {}
		convoDict[convoID][lineID] = line

	# List of links between dialogue entries
	dlinks = temp_db.execute("SELECT * FROM dlinks").fetchall()

	dlinks_accumulator = []
	for item in dlinks:
		dlinks_accumulator.append({k: item[k] for k in item.keys()})
	
	# Convert to dictionary of links, look up origin, get destinations
	# convos can have destinations in other convos
	dlinkDict = {}
	for link in dlinks_accumulator:
		convoID = link["originconversationid"]
		originID = link["origindialogueid"]
		if not convoID in dlinkDict:
			dlinkDict[convoID] = {}
		if originID in dlinkDict[convoID]:
			dlinkDict[convoID][originID].append(link)
		else:
			dlinkDict[convoID][originID] = [link]
			
	# get conversation titles
	dtitles = temp_db.execute("SELECT * FROM dialogues").fetchall()
	convID2Title = {}
	for item in dtitles:
		convID2Title[item['id']] = str(item['id']) + " :: " + item['title'] + " :: " + item["description"]
	
	# Build out, one conversation at a time
	out = []
	allConvoIDs = sorted([convoID for convoID in dlinkDict])
	#allConvoIDs = [322]
	for convoID in allConvoIDs:
		# name local convo IDs, shortcut to convoLinks
		convo = convoDict[convoID]
		convoLinks = dlinkDict[convoID]
		startID = findStart(convo)
		convoSeenIDs = []	
		out.append({"LOCATION":convID2Title[convoID]})
		# Recursive walk. Given an origin line ID, provide next steps
		def walkStructure(lineID):
			originConvID = convo[lineID]["conversationid"]
			idx = str(originConvID)+ "_"+ str(lineID)
			# If already seen ...
			if idx in convoSeenIDs:
				# ... just add a GOTO
				return([{"GOTO": idx}])
			else:
				convoSeenIDs.append(idx)
			# dialogue Line is always a list
			dialogueLine = dentry2DialogueLine(convo[lineID])
			if not lineID in convoLinks:
				# end of the line
				return(dialogueLine)
			#print(convoLinks[lineID])
			destIDs = [(x["destinationconversationid"], x["destinationdialogueid"]) for x in convoLinks[lineID]]
			destinations = []
			for destConvID,destDialogueID in destIDs:
				if destConvID == convoID:
					destinations.append(walkStructure(destDialogueID))
				else:
					# Link to another conversation
					destinations.append([{"GOTO":str(destConvID) + "_" + str(destDialogueID)}])
	
			if len(destinations)==1:
				return(dialogueLine + destinations[0])
			elif len(destinations)>1:
				return(dialogueLine + [{"CHOICE": destinations}])
			else:
				# No destinations (already dealt with?)
				return(dialogueLine)

		convoOut = walkStructure(startID)
		out += convoOut
			

	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)