import json,re,csv


#     id: unique numerical identifier (assigned during dataset creation, has no meaning in the game)
#     speaker: human readable name of the character that speaks the line. For NPCs: [firstname] + [lastname]. For PC: Player.
#     listener: human readable name of the character the speaker is speaking to. Probably used for head-turning 3D animations as well.
#     text: dialogue line
#     animation: animations that should be played for conversation participants. Might contain data for other characters (not speaker or listener) as well.
#     comment: game developer/writer comments for this dialogue line
#     next: possible follow-up dialogue lines (branching dialogue). Either the Player can choose, or the game uses conditional logic to choose.
#     previous: the dialogue lines that possibly preceeded this line.
#     source_dlg: the .dlg file from which this dialogue line is extracted. Generally there is 1 .dlg per character per planet.
#     audiofile: some dialogue lines have associated audio files with recordings of the voice actor. Extracting audio files is not (yet) covered in the instructions of this repo yet.


def parseFile(fileName,parameters={},asJSON=False):

	# Manual fixes for character IDs
	CharNameToID = parameters["IDToCharName"]
	IDToCharName = {}
	for charName in CharNameToID:
		for idx in CharNameToID[charName]:
			IDToCharName[idx] = charName
	
	# Manual fixes for conversation owners
	sourceToConvOwner = {}
	convOwnerFile = "../data/StarWarsKOTOR/StarWarsKOTOR/ConversationOwnersToCode_complete.csv"
	with open(convOwnerFile) as csvfile:
		csvreader = csv.reader(csvfile)
		for row in csvreader:
			if len(row[0])>0:
				sourceToConvOwner[row[3]] = row[1]

	header = []
	lines = []
	# id,speaker,listener,text,animation,comment,next,previous,source_dlg,audiofile
	with open(fileName) as csvfile:
		csvreader = csv.reader(csvfile)
		for row in csvreader:
			if len(header)==0:
				header = row
			else:
				dx = {}
				for i in range(len(header)):
					dx[header[i]] = row[i]
				lines.append(dx)
	
	def cleanLine(text):
		text = re.sub("\*([A-Za-z!?]+)\*","(\\1)",text)
		return(text)
		
	dialogueMapping = {}
	dialogueLines = {}
	startLines = []
	
	for line in lines:
		origCharName = line["speaker"]
		charName = origCharName
		lineID = line["id"]
		sourceID = line["source_dlg"]
		
		# Manual fixes to character names
		if lineID in IDToCharName:
			charName = IDToCharName[lineID]
		if charName == "Conversation owner":
			if sourceID in sourceToConvOwner:
				charName = sourceToConvOwner[sourceID]
				# The action dictionary actually has the correct character name
				origCharName = charName
			else:
				charName = "SYSTEM"
		
		lineText = line["text"]
		outx = [{charName: cleanLine(lineText), "_ID":lineID}]
		
		# The entry could be an action and a line of dialogue.
		# Split up:
		if lineText.startswith("[") and not lineText.startswith("[UNLOADING"):
			bits = re.split("(\[.+?\])",lineText)
			action = bits[1][1:-1]
			dlg = bits[2].strip()
			outx = [{"ACTION":action},
					{charName: cleanLine(dlg), "_ID":lineID}]
		
		
		listener = line["listener"].strip()
		if len(listener)>0:
			outx[-1]["_Listener"] = listener
			
		comment = line["comment"].strip()
		if len(listener)>0:
			outx[-1]["_Comment"] = comment
		
		# anim is a valid python list
		anim = eval(line["animation"])
		if len(anim)>0:
			emotion = ";".join([x[origCharName] for x in anim if charName in x])
			if len(emotion)>0:
				outx[-1]["_Emotion"] = emotion
		
		# Is there actual dialogue?
		if len(outx[-1][charName])==0:
			# If not, 
			if len(outx)==1:
				# replace a single line with an anchor
				# (I don't think this occurs)
				outx = [{"ANCHOR":lineID}]
			else:
				# or strip to just the action
				outx = outx[:-1]
		dialogueLines[lineID] = outx
				
		nextLines = line["next"][1:-1].split(",")
		nextLines = [x.strip() for x in nextLines if len(x.strip())>0]
		if len(nextLines)>0:
			dialogueMapping[lineID] = nextLines
		
		# Can the line be an initiating line?
		# "None" can appear in a list, like [None, 22868, 22881]
		if line["previous"].count("None")>0:
			startLines.append(lineID)
	
	
	def walkStructure(lineID):	
		outx = []
		if not lineID in seenIDs:
			seenIDs.append(lineID)
			outx += dialogueLines[lineID]
			if lineID in dialogueMapping:
				choices = []
				for nextLine in dialogueMapping[lineID]:
					choices.append(walkStructure(nextLine))
				if len(choices)>1:
					outx.append({"CHOICE": choices})
				elif len(choices)==1:
					outx += choices[0]
		else:
			outx.append({"GOTO":lineID})
		return(outx)

	#seenIDs is global
	seenIDs = []
	out = []
	for	startLineID in startLines:
		out += walkStructure(startLineID)
		out.append({"ACTION": "---"})

	#print(len(seenIDs))
	
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)