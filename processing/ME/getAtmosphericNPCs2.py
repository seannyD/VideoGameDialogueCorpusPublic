import json,csv,re,copy
import openpyxl

minNumChars = 2
maxNumChars = 5
excludeCasesWithSpeaker = ["Citadel Announcer","Citadel Female Announcer"]
linePropThreshold = 0.005

mainPCName = "Shepard"
systemKeys = ["CHOICE","ACTION","SYSTEM",'GOTO',"STATUS","ANCHOR"]

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
				if not mainKey in systemKeys:
					if len(line[mainKey])>0:
						try:
							charLines[mainKey] += 1
						except:
							charLines[mainKey] = 1
	walkLines(lines)
	return(charLines)	
		
def cleanTxt(txt):
	# make a bit more compact
	txt = re.sub('{\n\t+','{',txt)
	txt = re.sub('\n\t+}','}',txt)
	txt = re.sub('\n\t+]',']',txt)
	# Non-dialogue info should not have its own line
	txt = re.sub('",\n\t+"_','", "_',txt)
	
	# remove translations
	txt = re.sub('"_FRA":.+?}',"}",txt)
	txt = re.sub('\n\t+{"ACTION": "", "_ID": .+?},?',"",txt)
	txt = re.sub('\n\t+{"'+mainPCName+'": "", "_ID": .+?},?',"",txt)
	if txt.startswith(",\n"):
		txt = txt[2:]
	return(txt)
	
def getGenders(uniqueSpeakers,char2Gender):
	genders = []
	for spk in uniqueSpeakers:
		if spk in char2Gender:
			genders.append(char2Gender[spk])
		else:
			genders.append("Unknown")
	return(genders)
	


def getAtmosphericNPCs(inFileName):
	lines = json.load(open(inFileName))["text"]
	linestxt = open(inFileName).read()
	with open(inFileName.replace("data.json","meta.json")) as json_file:
		meta = json.load(json_file)
		
	game = meta["game"]
	
	char2Gender = {}
	for gender in meta["characterGroups"]:
		for n in meta["characterGroups"][gender]:
			char2Gender[n] = gender
	
	charLineCount = getCharLineCount(lines)
	totalLines = sum([x for x in charLineCount.values()])	
	
	print("JKR")
	#tlc = charLineCount['Jeff "Joker" Moreau']
	tlc = charLineCount['Liara T\'Soni']
	prp = tlc/totalLines
	print(prp)

	locations = linestxt.split('{"LOCATION": ')[1:]
	seenLocations = []
	for loc in locations:
		locName = loc[:loc.index("}")].replace('"',"").strip()
		cid = game+"#"+locName
		if not cid in seenLocations:
			seenLocations.append(cid)
	
			loc = loc[loc.index("\n")+1:] # remove location name
			loc = loc.strip()
			# add one tab so that the regex below works
			loc = "\t"+loc
			# Remove empty PC lines
			loc = re.sub('\t+{"' + mainPCName + '": "",.+?\n','',loc)
			# Remove lines with no dialogue:
			loc = re.sub('\t+{".+?": "",.+?\n',"",loc)
			# Fix escaped characters
			loc = loc.replace("\\","")
			
			convs = loc.split('{"ACTION": "---"}')
			for conv in convs:
				charNames = re.findall('{"(.+?)":',conv)
				charNames = [x for x in charNames if not x in systemKeys]
				charNames = [x for x in charNames if not x in excludeCasesWithSpeaker]
		
				uniqueChars = list(set(charNames))
				numChars = len(uniqueChars)
				charGenders = getGenders(uniqueChars,char2Gender)
				convLineCounts = [charNames.count(x) for x in uniqueChars]
				totalLineCounts = [charLineCount[x] for x in uniqueChars]
				totalLineProportion = [x/totalLines > linePropThreshold for x in totalLineCounts]
				charTypes = [["Minor","Major"][x > linePropThreshold] for x in totalLineProportion]

		
				convType = "None"
				if not mainPCName in uniqueChars: # If Shepard has no lines
					if numChars > 1: # number of unique characters > 1
						if not "Major" in charTypes: # all are minor
							convType = "Ambient Minor"
						elif not "Minor" in charTypes: # all are major
							convType = "Ambient Major"
						else:
							convType = "Ambient Mixed" # mixed major and minor
					elif numChars == 1: # only one speaker
						if charTypes[0] == "Minor": # the speaker is minor
							convType = "OneSided Minor"
						else:
							convType = "OneSided Major"
				else: # Shepard is part of the conversation
					# Does the location name suggest it's considered ambient by the game makers?
					if locName.count("_amb")>0 and locName.count("_ambassador")==0 and locName.count("_ambush")==0:
						convType = "Ambient System"
					elif convLineCounts[uniqueChars.index(mainPCName)] == 1 and numChars > 2:
						# Shepard only has one line and there are at least two other chars
						convType = "Ambient With PC Prelude"
					else:
						convType = "None"
		
				if not convType in convExamples:
					convExamples[convType] = []
				convExamples[convType].append({
					"game":game,
					"convType":convType,
					"locName": locName,
					"charNames": uniqueChars,
					"genders": charGenders,
					"lineCounts": convLineCounts,
					"charTypes":charTypes,
					"txt": cleanTxt(conv)})
	
	
		
convExamples = {}
getAtmosphericNPCs("../../data/MassEffect/MassEffect1B/data.json")
getAtmosphericNPCs("../../data/MassEffect/MassEffect2/data.json")
getAtmosphericNPCs("../../data/MassEffect/MassEffect3C/data.json")

print([(ty,len(convExamples[ty])) for ty in convExamples])

# Filter repeating types
finalExamples = {}
for convType in convExamples:
	finalExamples[convType] = []
	uniqueTxts = []
	for conv in convExamples[convType]:
		utxt = copy.deepcopy(conv["txt"])
		utxt = re.sub('"_ID":.+?}',"}",utxt)
		utxt = utxt.replace("\t","").replace(" ","")
		if not utxt in uniqueTxts:
			uniqueTxts.append(utxt)
			finalExamples[convType].append(conv)
				
# Add previously coded information
dataframe = openpyxl.load_workbook("../../../../../../Teaching/ResearchExperience/2024_2025/projects/ZofiaSzefler/ExampleList.xlsx")
datasheet = dataframe["General"]
colNames = [x.value for x in datasheet[1]]
previousCodes = {}
for row in range(2, datasheet.max_row):
	game = datasheet[row][colNames.index("Game")].value
	locName = datasheet[row][colNames.index("Location")].value
	xid = game.strip() + "#" + locName.strip()
	if xid!="#":
		previousCodes[xid] = dict([(x,datasheet[row][colNames.index(x)].value) for x in colNames])
	


print([(ty,len(finalExamples[ty])) for ty in finalExamples])

for convType in finalExamples:
	folder = "../../results/doNotShare/ME/AtmosphericNPCs/"
	fileName = folder + "ConvExamples_"+convType.replace(" ","")+".csv"
	with open(fileName, 'w') as csvfile:
		csvwriter = csv.writer(csvfile)
		rowHeaders = [
			"Num","Game","Location","Speakers","NumSpeakers",
			"Genders","CharTypes","nMale",'nFemale','nMaleLines','nFemaleLines',
			"charLineCounts",'text',
			"OldRelevant","OldPlotRelevant","OldHumorousFinal","OldTopic",
			"NewRelevant","NewHumorous","NewTopic"]
		csvwriter.writerow(rowHeaders)
		i = 0 
		prevLoc = ""
		for conv in finalExamples[convType]:
			i += 1
			nMale = sum([x=="male" for x in conv["genders"]])
			nFemale = sum([x=="female" for x in conv["genders"]])
			nMaleLines = sum([conv["lineCounts"][i] for i in range(len(conv["lineCounts"])) if conv["genders"][i]=="male"])
			nFemaleLines = sum([conv["lineCounts"][i] for i in range(len(conv["lineCounts"])) if conv["genders"][i]=="female"])
			
			oRel = ""
			oPlot = ""
			oHum = ""
			oTop = ""
			xid = conv["game"].strip() + "#" + conv["locName"].strip()
			if xid in previousCodes:
				oRel = previousCodes[xid]["relevant to me?"]
				oPlot = previousCodes[xid]["plot relevant?"]
				oHum = previousCodes[xid]["humorousFinal"]
				oTop = previousCodes[xid]["topic 1"]
			
			# Add blank line to sep locations
			if i>1 and conv["locName"]!=prevLoc:
				prevLoc = conv["locName"]
				csvwriter.writerow([""]*len(rowHeaders))
			
			row = [i,conv["game"], conv["locName"]]
			row += ["/ ".join(conv["charNames"])]
			row += [str(len(conv["charNames"])),"/ ".join(conv["genders"])]
			row += ["/ ".join(conv["charTypes"])]
			row += [nMale,nFemale,nMaleLines,nFemaleLines]
			row += ["/ ".join([str(x) for x in conv["lineCounts"]])]
			row += [conv["txt"]]
			row += [oRel,oPlot,oHum,oTop]
			csvwriter.writerow(row)
		
		
