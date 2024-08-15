from bs4 import BeautifulSoup
import re, csv

DA2_existingTalkstringIDs = ""

DA2_WheelTypeDict = {
	"0": "Neutral",
	"1": "Agressive",
	"2": "Diplomatic",
	"3": "Humorous",
	"4": "Bonus",
	"5": "Follower",
	"6": "Choice #1",
	"7": "Choice #2",
	"8": "Choice #3",
	"9": "Choice #4",
	"10": "Choice #5",
	"11": "Investigate"
}


def parseFile(fileName,parameters={},asJSON=False):
	global DA2_existingTalkstringIDs
	
	# Avoid debug files
	if fileName.count("_debug")>0 or fileName.count("zz_")>0:
		return([])
	# Avoid demo files
	if any([fileName.count(x)>0 for x in ["montage_subs_demohack.cnv","demo_weapon_swap.cnv", "testconvo.cnv", "narrative_varric_demo.cnv"]]):
		return([])
	
	
	print(fileName)
	# input is an unencoded dlg file
	
	xml = open(fileName,'r', encoding = 'utf8')
	soup = BeautifulSoup( xml, "lxml")
	
	# Load ids
	if len(DA2_existingTalkstringIDs)==0:
		existingTalkstringIDFile = open("../data/DragonAge/DragonAge2/talkstringIDs.xml").read()
		DA2_existingTalkstringIDs = existingTalkstringIDFile.split(",")
	
	
	out = []
	
	#voBank = soup.find("string", {"alias": "ConversationVOBank"}, recursive=True).getText()
	#ownerCharName = "OWNER_"+voBank
	
	conv = soup.find("struct_list", {"label":"30002"},recursive=True)

	# first struct list is starting list
	startingListStruct = soup.find("struct_list",{"label":"30001"}, recursive=True)
	startingList = [x.getText() for x in startingListStruct.find_all("uint16")]
	
	# second struct list is order
	dialogueList = soup.find("struct_list",{"label":"30002"}, recursive=True).find_all("struct",{"name":"LINE"})
	
	wheelChoices = soup.find("")
		
	def parseStruct(struct):
		#print(struct)
		#print("----")
		label = struct["index"]
		# TODO: filter for particular types of tlkstring?
		lineID = ""
		tkx = struct.find("tlkstring",recursive=True)
		if not tkx is None:
			lineID = tkx.getText().strip()
		# Get list of links out of this node,
		#  which can also include dialogue wheel options
		childList = struct.find("struct_list", {"label": "30204"}).find_all("struct")
		children = []
		wheelChoices = []
		for child in childList: # Each link Struct
			linkx = child.find("uint16",{"label":"30100"})
			if not linkx is None:
				linkx = linkx.getText()
			children.append(linkx)
			wheelTlk = None
			wtx = child.find("tlkstring", {"label": "30101"}).getText()
			if not wtx is None and wtx in DA2_existingTalkstringIDs:
				wheelType = ""
				wheelTypeX = child.find("uint8",{"label":"30300"})
				if not wheelTypeX is None:
					wheelType = wheelTypeX.getText()
					if wheelType in DA2_WheelTypeDict:
						wheelType = DA2_WheelTypeDict[wheelType]
				wheelTlk = (wtx,wheelType)
			wheelChoices.append(wheelTlk)
			# TODO: extract wheel tips
		#children = [x.getText() for x in childList.find_all("uint16",{"label":"30100"}, recursive=True) if len(x.getText().strip()) >0]
		#childrenWheelTlkStrings = []
		return ((label, lineID, children, wheelChoices))
	
	bits = {}
	ix = 0
	for struct in [x for x in dialogueList if len(x.getText().strip())>0]:
		#if not "index" in struct:
		#	struct["index"] = str(ix)
		label, lineID, childList, wheelChoices = parseStruct(struct)
		bits[label] = (lineID, childList, wheelChoices)
		ix +=1

	
	# Build structure

	def getOutFromLabel(label):
		lineID, childList, wheelChoices = bits[label]
		#if speaker == "OWNER":
		#	speaker = ownerCharName
		if label in visitedIDs:
			return([{"GOTO": lineID}])
		else:
			outx = []
			if lineID in DA2_existingTalkstringIDs:
				outx.append({lineID: lineID, "_ID": lineID})
			visitedIDs.append(label)
			choices = []
			for child,wheelChoice in zip(childList,wheelChoices):
				cx = []
				if not wheelChoice is None:
					wid, wcat = wheelChoice
					cx.append({"ACTION":"Player chooses: "+wid,"_CHOICETYPE":wcat})
				cx += getOutFromLabel(child)
				choices.append(cx)
			if len(choices)>0:
				if len(choices)==1:
					outx += choices[0]
				else:
					outx.append({"CHOICE": choices})			
			return(outx)

	visitedIDs = []
	out = [{"LOCATION":"FILE: "+fileName}]
	
	for st in startingList:
		stx = getOutFromLabel(st)
		if len(stx)>0:
			out += stx
			
	# Add separator between dialogues
	out.append({"ACTION":"---"})

	if asJSON:
		print(json.dumps({"text":out}, indent = 4))
		return(json.dumps({"text":out}, indent = 4))
	return(out)


def postProcessing(out):
	
	# Get dialogue text
	talkStrings = {}
	xml = open("../data/DragonAge/DragonAge2/raw/campaign_base_en-us.xml")
	soup = BeautifulSoup( xml, "lxml")
	for st in soup.find_all("string"):
		talkStrings[st["id"]] = st.getText()
		
	# Get character mappings
	mappingFile = "../data/DragonAge/DragonAge2/tlkStringToCharName.csv"
	tlkStringIDColumn = 6
	chosenCharNameColumn = 5
	
	# TODO:
	# in the tlkStringToCharName file, each tlkString can be mapped to more than one character
	#  e.g. if the player is male or female.
	tlkString2CharName = {}
	with open(mappingFile) as csvfile:
		csvreader = csv.reader(csvfile)
		for row in csvreader:
			tlkString2CharName[row[tlkStringIDColumn]] = row[chosenCharNameColumn]
	
	def cleanLine(txt):
		txt = txt.replace("<emp>","")
		txt = txt.replace("</emp>","")
		txt = txt.replace("<desc>","(")
		txt = txt.replace("</desc>",")")
		return(txt)
	
	def getText(line):
		k = [x for x in line if not x.startswith("_")][0]
		# Replace main key with character name
		charName = k
		if k in tlkString2CharName:
			charName = tlkString2CharName[k]
			if charName in ["PLAYER_male","PLAYER_female"]:
				line["_PLAYERGENDER"] = charName
				charName = "PLAYER"
			if charName.startswith("PlayerMale") or charName.startswith("PCfemale"):
				if "_" in charName:
					# e.g. PlayerMale_humourous
					line["_CHOICETYPE"] = charName[charName.index("_")+1:].title()
					if line["_CHOICETYPE"] == "Dip":
						line["_CHOICETYPE"] = "Diplomatic"
					if charName.startswith("PlayerMale"):
						line["_PLAYERGENDER"] = "Male"
					elif charName.startswith("PCfemale"):
						line["_PLAYERGENDER"] = "Female"
					charName = "ACTION"
			# capitalise
			if not charName in ["ACTION","CHOICE","SYSTEM"]:
				charName = charName.title()
			# Remove mission info from name
			if charName.count("_")>0:
				charName = charName[charName.index("_")+1:]
			# Remove underscores
			charName = charName.replace("_"," ")
		
		# Replace ID with text
		dialogue = line[k]
		if "_CHOICETYPE" in line:
			# If this is a choice marker
			dialogue = "Player chooses: '" + line["_CHOICETYPE"] + "'"
		elif line[k] in talkStrings and k!="GOTO":
			dialogue = talkStrings[line[k]]
			dialogue = cleanLine(dialogue)

		outLine = {charName:dialogue}
		if "_ID" in line:
			outLine["_ID"] = line["_ID"]
		if "_PLAYERGENDER" in line:
			outLine["_PLAYERGENDER"] = line["_PLAYERGENDER"]
		if "_CHOICETYPE" in line:
			outLine["_CHOICETYPE"] = line["_CHOICETYPE"]
		return(outLine)

	
	def walk(lines):
		outx = []
		for line in lines:
			k = [x for x in line if not x.startswith("_")][0]
			if k == "CHOICE":
				choices = []
				for choice in line["CHOICE"]:
					choices.append(walk(choice))
				outx.append({"CHOICE":choices})
			elif k == "ACTION" and line[k].startswith("Player chooses:"):
				tlkID = line[k]
				tlkID = tlkID[tlkID.index(":")+1:].strip()
				if tlkID in talkStrings:
					outx.append({"ACTION": "Player chooses: '"+ talkStrings[tlkID] +"'",
								"_ID":tlkID, "_CHOICETYPE": line["_CHOICETYPE"]})
				else:
					outx.append(line)
			else:
				outx.append(getText(line))
		return(outx)
	
	out2 = walk(out)
		
	return(out2)
					
					
					