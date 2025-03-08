import json,csv,re,copy
# TODO: don't add to transitions if pre and next speaker is the same
#  Exclude cases without at 2 transitions between two characters?

# For ME 1, need to ignore {"Shepard": "" ...}

# Add Just one character, and column for num speakers

minNumChars = 2
maxNumChars = 5
excludeCasesWithSpeaker = ["Citadel Announcer","Citadel Female Announcer"]
linePropThreshold = 0.01

def getCharLineCount(lines):
	charLines = {}
	def walkLines(lines):
		for line in lines:
			mainKey = [x for x in line if not x.startswith("_")][0]
			if mainKey == "CHOICE":
				choices = line["CHOICE"]
				for choice in choices:
					walkLines(choice)
			else:
				try:
					charLines[mainKey] += 1
				except:
					charLines[mainKey] = 1
	walkLines(lines)
	return(charLines)

			

def followConv(lines,loc):

	# Make dictionary of ids to content,
	# and links between IDs
	links = {}
	idToLine = {"START":"START"}
	def getConvLinks(lines, prevLink = "START"):
		for line in lines:
			mainKey = [x for x in line if not x.startswith("_")][0]
			if mainKey == "CHOICE":
				choices = line["CHOICE"]
				for choice in choices:
					getConvLinks(choice,prevLink)
			elif mainKey == "GOTO":
				try:
					links[prevLink].append(line["GOTO"])
				except:
					links[prevLink] = [line["GOTO"]]
			else:
				# Add to idToLine
				if "_ID" in line:
					sid = line["_ID"]
				else:
					# (STATUS parts don't have IDs, so make one up)
					sid = "STATUS"+	str(len(idToLine))					
					line["_ID"] = sid
				idToLine[sid] = line
				# Add links
				if line != {"ACTION": "---"}:
					try:
						links[prevLink].append(sid)
					except:
						links[prevLink] = [sid]
					prevLink = sid
				
	getConvLinks(lines)
				
	# Now walk through the links, keeping track of gender
	# assignments to each ID
	
	id2Gender = {"START":"START"}
	
	dTrans = {}
	
	seenIDs = {}
	seenLinks = {}
	def walkLinks(startID, prevSpeaker=""):
		if startID in links:
			startLine = idToLine[startID]
			startLineKey = [x for x in startLine if not x.startswith("_")][0]
			if not startLineKey in ["ACTION","STATUS"]:
				if not ((startLineKey == "Shepard") and (startLine["Shepard"] == "")):
					prevSpeaker = startLineKey
			for desitnationID in links[startID]:
				# (destline is dict)
				destLine = idToLine[desitnationID]
				destLineKey = [x for x in destLine if not x.startswith("_")][0]
				if not destLineKey in ["ACTION","STATUS"]:
					if not ((destLineKey == "Shepard") and (destLine["Shepard"] == "")):
						if not (prevSpeaker,destLineKey) in dTrans:
							dTrans[(prevSpeaker,destLineKey)] = []
						if not destLine in dTrans[(prevSpeaker,destLineKey)]:
							dTrans[(prevSpeaker,destLineKey)].append(destLine)
						prevSpeaker = destLineKey
				# Should we continue?
				# Keep track of links we've done already, assume we won't go through the 
				# same link more than 10 times
				if not (startID,desitnationID) in seenLinks:
					seenLinks[(startID,desitnationID)] = 0
				seenLinks[(startID,desitnationID)] += 1
				if seenLinks[(startID,desitnationID)]<3:
					walkLinks(desitnationID,prevSpeaker)

	walkLinks("START")
	#print(id2Gender)
	
	return(dTrans)
	
def getUniqueSpeakers(dTrans):
	uniqueSpeakers = list(set([x[0] for x in dTrans] + [x[1] for x in dTrans]))
	uniqueSpeakers = [x for x in uniqueSpeakers if not x in ["START","S","SYSTEM","ANCHOR"]]
	return(uniqueSpeakers)

def isAtmosphericConvo(dTrans, charLineCount):
	numLines = len([x for x in dTrans.keys()])
	# Number of unique speakers in conversation
	uniqueSpeakers = getUniqueSpeakers(dTrans)
	numUniqueSpeakers = len(uniqueSpeakers)
	print(uniqueSpeakers)
	print(numUniqueSpeakers)
	if "Shepard" in uniqueSpeakers:
		return(False)
	if any([x in excludeCasesWithSpeaker for x in uniqueSpeakers]):
		return(False)
	if (numUniqueSpeakers >maxNumChars) or (numUniqueSpeakers<minNumChars):
		return(False)
	
	totalCharLines = sum([charLineCount[x] for x in uniqueSpeakers if x in charLineCount])
	totalLines = sum([x for x in charLineCount.values()])
	
	print(totalCharLines/totalLines)
	if (totalCharLines/totalLines) < linePropThreshold:	
		print(uniqueSpeakers)
		for x in dTrans:
			print("\t\t"+str(x)+str(len(dTrans[x])))
		return(True)
	else:
		return(False)
		
def cleanData(lines):
	line

		
def writeData(out,dest):
	json_data = json.dumps({"text":out}, indent="\t",ensure_ascii=False)
	# make a bit more compact
	json_data = re.sub('{\n\t+','{',json_data)
	json_data = re.sub('\n\t+}','}',json_data)
#		json_data = re.sub('\[\n\t+','[',json_data)
	json_data = re.sub('\n\t+]',']',json_data)
	# Non-dialogue info should not have its own line
	json_data = re.sub('",\n\t+"_','", "_',json_data)
	
	# remove translations
	json_data = re.sub('"_FRA":.+?}',"}",json_data)
	json_data = re.sub('\n\t+{"ACTION": "", "_ID": .+?},?',"",json_data)
	json_data = re.sub('\n\t+{"Shepard": "", "_ID": .+?},?',"",json_data)
	
	o = open(dest,'w')
	o.write(json_data)
	o.close()
	
def getGenders(uniqueSpeakers,char2Gender):
	genders = []
	for spk in uniqueSpeakers:
		if spk in char2Gender:
			genders.append(char2Gender[spk])
		else:
			genders.append("Unknown")
	return(genders)

def getAtmosphericNPCs(inFileName,outFileName):
	with open(inFileName) as json_file:
		lines = json.load(json_file)["text"]
	with open(inFileName.replace("data.json","meta.json")) as json_file:
		meta = json.load(json_file)
		
	game = meta["game"]
	
	char2Gender = {}
	for gender in meta["characterGroups"]:
		for n in meta["characterGroups"][gender]:
			char2Gender[n] = gender
	
	charLineCount = getCharLineCount(lines)	

	out = []
	skipLocs = []
	seq = []
	loc = ""
	#Spilt into sections and followConv for each
	for line in lines:
		# TODO: or {"ACTION": "---"}
		if "LOCATION" in line:
			oldLoc = copy.deepcopy(loc)
			loc = line["LOCATION"] # Next upcoming location
			if len(seq)>0 and not loc in skipLocs:
				dTransSeq = followConv(seq,oldLoc)
				if isAtmosphericConvo(dTransSeq,charLineCount):
					print("LOC "+oldLoc)
					out.append([{"LOCATION":oldLoc}]+seq)
					uniqueSpeakers = getUniqueSpeakers(dTransSeq)
					genders = getGenders(uniqueSpeakers,char2Gender)
					exampleList.append([game,oldLoc,uniqueSpeakers,genders])
				seq = []
		else:
			seq.append(line)
	# Process leftover dialogue
	if len(seq)>0:		
		try:
			dTransSeq = followConv(seq,loc)
			if isAtmosphericConvo(dTransSeq,charLineCount):
				out.append([line]+seq)
				uniqueSpeakers = getUniqueSpeakers(dTransSeq)
				genders = getGenders(uniqueSpeakers,char2Gender)
				exampleList.append([game,loc,uniqueSpeakers,genders])
		except:
			pass

	writeData(out,outFileName)
	
	
		
		
exampleList = []
getAtmosphericNPCs("../../data/MassEffect/MassEffect1B/data.json",
				"../../results/doNotShare/ME/AtmosphericNPCs/ME1_AtmosphericNPCs.json")
getAtmosphericNPCs("../../data/MassEffect/MassEffect2/data.json",
				"../../results/doNotShare/ME/AtmosphericNPCs/ME2_AtmosphericNPCs.json")
getAtmosphericNPCs("../../data/MassEffect/MassEffect3C/data.json",
				"../../results/doNotShare/ME/AtmosphericNPCs/ME3_AtmosphericNPCs.json")


with open("../../results/doNotShare/ME/AtmosphericNPCs/ExampleList.csv", 'w') as csvfile:
	csvwriter = csv.writer(csvfile)
	csvwriter.writerow(["Num","Game","Location","Speakers","NumSpeakers","Genders","nMale",'nFemale'])
	i = 0
	for eRow in exampleList:
		i += 1
		print(eRow)
		game,loc,uniqueSpeakers,genders = eRow
		nMale = sum([x=="male" for x in genders])
		nFemale = sum([x=="female" for x in genders])
		row = [i,game, loc,", ".join(uniqueSpeakers),str(len(uniqueSpeakers)),", ".join(genders),nMale,nFemale]
		csvwriter.writerow(row)