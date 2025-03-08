import json,csv,re

def writeData(out,destFile):
	json_data = json.dumps({"text":out}, indent="\t",ensure_ascii=False)
	# make a bit more compact
	json_data = re.sub('{\n\t+','{',json_data)
	json_data = re.sub('\n\t+}','}',json_data)
	json_data = re.sub('\n\t+]',']',json_data)
	# Non-dialogue info should not have its own line
	json_data = re.sub('",\n\t+"_','", "_',json_data)
	o = open(destFile,'w')
	o.write(json_data)
	o.close()
	
def findRelevantFlag(flagString,flagsToFind):
	flags = flagString.split("\n")
	for flag in flags:
		if any([flag.count(f)>0 for f in flagsToFind]):
			ret = flag.replace("CHECK FLAG: ","")
			ret = re.sub("\\[.+","",ret).strip()
			state = "True"
			if flag.count("False")>0:
				state = "False"
			return(ret,state)
	return("None","True")
	
def getAllFlags(flagString):
	out = []
	for flag in flagString.split("\n"):
		ret = flag.replace("CHECK FLAG: ","")
		ret = re.sub("\\[.+","",ret).strip()
		out.append(ret)
	return(list(set(out)))
	
	
def getBG3DialogueByFlag(flagsToFind,setPrefix):

	outFileJSON = "../../results/doNotShare/BG3/BG3_"+setPrefix+".json"
	outFileXML = "../../results/doNotShare/BG3/BG3_"+setPrefix+".xml"
	outFileCSV = "../../results/doNotShare/BG3/BG3_"+setPrefix+".csv"
	outCheckFlagList = "../../results/doNotShare/BG3/BG3_"+setPrefix+"_checkFlags.csv"
	outSetFlagList = "../../results/doNotShare/BG3/BG3_"+setPrefix+"_setFlags.csv"


	with open("../../data/BaldursGate/BaldursGate3/data.json") as json_file:
		lines = json.load(json_file)["text"]
	with open("../../data/BaldursGate/BaldursGate3/meta.json") as json_file:
		meta = json.load(json_file)
	
	char2gender = {}
	for group in meta["characterGroups"]:
		for charName in meta["characterGroups"][group]:
			char2gender[charName] = group

	out = []
	outFlags = {}
	outSetFlags = {}
	allCheckFlags = {}

	currentLoc = ""
	currentLines = []
	for line in lines:
		if "LOCATION" in line:
			if len(currentLines)>0:
				out.append(currentLoc)
				out += currentLines
				currentLines = []
			currentLoc = line
		elif "_checkflags" in line:
			flags = line["_checkflags"]
			allFlags = getAllFlags(flags)
			for flag in allFlags:
				if not flag in allCheckFlags:
					allCheckFlags[flag] = 1
				allCheckFlags[flag] += 1
			setFlags = line["_setflags"]
			if any([flags.count(f)>0 for f in flagsToFind]):
				mainKey = [x for x in line if not x.startswith("_")][0]
				line[mainKey] = line[mainKey].replace("*"," * ")
				currentLines.append(line)
				for flag in [x.replace("CHECK FLAG: ","") for x in flags.split("\n")]:
					if not flag in outFlags:
						outFlags[flag] = 0
					outFlags[flag] += 1
				for flag in [x.replace("CHECK FLAG: ","") for x in setFlags.split("\n")]:
					if not flag in outSetFlags:
						outSetFlags[flag] = 0
					outSetFlags[flag] += 1

	writeData(out, outFileJSON)

	xmlOut = ""
	currentLoc = ""
	with open(outFileCSV, 'w') as csvfile:
		csvwriter = csv.writer(csvfile)
		csvwriter.writerow(["ID","location","relFlag","relFlagSetting","speaker","line","checkFlags", "setFlags"])
		for line in out:
			mainKey = [x for x in line if not x.startswith("_")][0]
			if mainKey == "LOCATION":
				currentLoc = line[mainKey]
			else:
				gender = "unknown"
				if mainKey in char2gender:
					gender = char2gender[mainKey]
				idx = ""
				if "_id" in line:
					idx = line["_id"]
				dialogue = line[mainKey]
				dialogue = dialogue.replace('"','""')
				checkFlags = ""
				relFlag = ""
				relFlagSetting = ""
				if "_checkflags" in line:
					checkFlags = line["_checkflags"]
					relFlag,relFlagSetting = findRelevantFlag(checkFlags,flagsToFind)
				setFlags = ""
				if "_checkflags" in line:
					setFlags = line["_setflags"]
				csvwriter.writerow([idx,currentLoc,relFlag,relFlagSetting,mainKey,dialogue,checkFlags,setFlags])
		
				xmlOut += '<doc game="Baldur\'s Gate 3" '
				xmlOut += 'location="'+currentLoc+'" '
				xmlOut += 'relFlag="'+relFlag+'" '
				xmlOut += 'relFlagSetting="'+relFlagSetting+'" '
				xmlOut += 'speaker="'+mainKey+'" '
				xmlOut += 'gender="'+ gender + '" ' 
				xmlOut += 'set="' + setPrefix + '"' 
				xmlOut += ">"+ dialogue.replace("<",";lt").replace(">",";gt")
				xmlOut += "</doc>\n"

	with open(outFileXML, 'w') as xmlfile:
		xmlfile.write(xmlOut)

	def writeFlagData(flagList, outFile):
		with open(outFile, 'w') as csvfile:
			csvwriter = csv.writer(csvfile)
			csvwriter.writerow(["Flag","Frequency"])
			for flag in flagList:
				csvwriter.writerow([flag,flagList[flag]])

	writeFlagData(outFlags, outCheckFlagList)
	writeFlagData(outSetFlags, outSetFlagList)
	
	with open("../../results/doNotShare/BG3/BG3_AllFlags.csv", 'w') as csvfile:
		csvwriter = csv.writer(csvfile)
		csvwriter.writerow(["flag","frequency"])
		for flag in allCheckFlags:
			csvwriter.writerow([flag,allCheckFlags[flag]])
		



getBG3DialogueByFlag(flagsToFind = [
	": REALLY_GITHYANKI",
	": GITHYANKI",
	"This character is in an exclusive relationship with Laezel"], 
	setPrefix = "Gith")
	
getBG3DialogueByFlag(flagsToFind = [
	": TIEFLING",
	": REALLY_TIEFLING"], setPrefix = "Tiefling")




