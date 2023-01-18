import sqlite3

def parseFile(fileName,parameters={},asJSON=False):


	def findStart(convo):
		for lineID in convo:
			lx = convo[lineID]
			if lx["title"]=="START":
				return(lineID)
				
	
	temp_db = sqlite3.connect(fileName)
	temp_db.row_factory = sqlite3.Row
	dentries = temp_db.execute("SELECT * FROM dentries").fetchall()

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

	dlinks = temp_db.execute("SELECT * FROM dlinks").fetchall()

	dlinks_accumulator = []
	for item in dlinks:
		dlinks_accumulator.append({k: item[k] for k in item.keys()})
	
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
	
	convoID = 322
	convo = convoDict[convoID]
	convoLinks = dlinkDict[convo]
	startID = findStart(convo)
	convoOut = [convo[startID]]
	convoContinue = True
	
	# TODO: Keep track of IDs seen
	def walkStructure(convoID, convoLinks):
		
	
	while convoContinue:
		currentID = convoOut
		nextIDs = convoLinks[currentID]:
			# TODO: start adding lines to out
		

	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)