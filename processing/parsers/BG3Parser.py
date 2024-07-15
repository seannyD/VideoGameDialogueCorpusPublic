import json,pathlib,copy
from bs4 import BeautifulSoup
import re,os

localisation = {}
charData = {}
flagData = {"8f74d144-041e-4035-a9ac-72f41fc32de7":"Male pronoun",
			"3806477c-65a7-4100-9f92-be4c12c4fa4f":"Female pronoun"}

DCDict = {"e0a7c461-08bf-459d-9c9a-747008ced85c":50,
			"306ba0ce-1a69-4a46-9ca0-7d3e8f5be954":25,
			"881bda2f-b08b-4788-b0ec-e410b5bacc57":20,
			"1afda678-eb97-4b25-9548-0908e84b5475":19,
			"bddbb9b8-a242-4c3e-a2eb-3fd274c0c539":15,
			"598ee99a-f9e9-4a07-a98a-d1379131daa1":14,
			"98197cc5-8713-44bb-9afc-f5fe32bc5ff9":12,
			"f4c9d750-49a9-4b7d-a27c-92b801b7d808":11,
			"625be976-7a67-4394-97c8-14c69715ae4b":10,
			"f149a3ce-7625-4b9c-97b5-cfefaf791b64":8,
			"6e246ccd-6149-4ec4-a325-034309a18138":5,
			"98d69b07-f551-4d77-af31-41d074748dc0":0,
			"5028066b-6ea0-4a6a-9e3e-53bee62559a7":"?",
			"6298329e-255c-4826-9209-e911873b64e7":"?",
			"77cee1c4-384a-4217-b670-67db3c7add57":"?",
			"96bc76f2-0b2e-4a79-854f-e4971a772c36":"?",
			"00000000-0000-0000-0000-000000000000":"?",
			"fa621d38-6f83-4e42-a55c-6aa651a75d46": "?"}
			
conditionToTrueCharName = {
		"|Karlach, Hells' champion. Tiefling origin. Whether or not she's shapeshifted.|": "Karlach",
		"| Really Astarion, Vampire companion |": "Astarion",
		"REALLY_GALE": "Gale",
		"REALLY_LAEZEL": "Lae'zel",
		"| Lae'zel, the Gith Companion |": "Lae'zel",
		"|Really Shadowheart|": "Shadowheart",
		"|Really Wyll, superhero warlock|": "Wyll",
		"REALLY_MINTHARA": "Minthara",
		"REALLY_MINSC": "Minsc"
		# I'm less sure about these:
		"|Jaheira companion, shapeshifted or not|": "Jaheira",
		"|Halsin, shapeshifted or not|": "Halsin",
		"| Astarion, Vampire Companion |": "Astarion",		
		"|Shadow Heart, Sharite companion|": "Shadowheart",
		'|Gale companion|': "Gale"
	}

# TODO: approvalID - what is this?
# TODO: add localisation handles
# TODO: Some lines include variables which are stored in GustavDev/Story/Diaogs/DialogVariables
# 	<content contentuid="he7b465fcga9aag4350g8838gbd86ef7a4857" version="2">Adjusting for inflation, the appreciable value of knowledge, Lord Mammon's tithe... A-ha. There we are. ([LOW_DevilsFee_GortashInfoPayment_4feace82-e2ce-a19d-967c-2a346b2cf96d])</content>

# TODO: DC Dict - lots of missing. these are referenced in raw/STORY/ and raw/STORYDEV/



def parseFile(fileName,parameters={},asJSON=False):
	global localisation
	
	def loadLocalisation():
		global localisation
		
		def cleanLine(txt):
			# Italics
			for targ,repl in [
				("&lt;i&gt;"," # "),
				("&lt;/i&gt;"," # "), 
				("&amp;","&"),
				("&lt;br&gt;"," \t ")]:
				txt = txt.replace(targ,repl)
			txt = txt.replace("[GEN_PlayerName_c11eee1e-7815-6143-7233-f2427799fa53]","PLAYERNAME")
			txt = txt.strip()
			return(txt)
		
		d = open("../data/BaldursGate/BaldursGate3/raw/Localization/English/english.xml").read()
		d = d.split('<content contentuid="')[1:-1]
		for line in d:
			line = line.replace(" ",">",1)
			bits = line.split(">",2)
			uuid = bits[0][:-1]
			version = bits[1]
			txt = bits[2].replace('</content>','')
			localisation[uuid] = cleanLine(txt)

	def loadCharacterData():
		global charData
		charDataFilePath = "../data/BaldursGate/BaldursGate3/charData.json"
		if os.path.isfile(charDataFilePath):
			f = open(charDataFilePath)
			charData = json.load(f)
		else:
			charData["e0d1ff71-04a8-4340-ae64-9684d846eb83"] = {'charName':"PC"}
			# -------------------
			def parseCharacterFile(lsxFileName):
				global charData
				xml = open(lsxFileName,'r', encoding = 'utf8')
				soup = BeautifulSoup(xml, "lxml")
				gameObjects = soup.find_all("node",{"id":"GameObjects"})
				for gameObject in gameObjects:
					charID = gameObject.find("attribute",{"id":"MapKey"})["value"]
					charName = ""
					dispName = gameObject.find("attribute",{"id":"DisplayName"})
					if not dispName is None:
						charNameID = dispName["handle"]
						charName = localisation[charNameID]
					else:
						rawName = gameObject.find("attribute",{"id":"Name"})
						charName = rawName["value"]
						charName = charName.replace("S_Player_","").strip()
					charData[charID] = {"charName":charName}
					# Add another link to the peanut speakers?
					# e.g. Auntie Ethel's name is linked only in a "speakergrouplist" contained inside an "Item" file.
					cnode = gameObject.find("node",{"id":"SpeakerGroupList"})
					if not cnode is None:
						guid = cnode.find("attribute",{"id":"Object","type":"guid"})
						if not guid is None:
							charData[guid["value"]] = {"charName":charName}

						
			# -------------------
		
			baseFolders = ["../data/BaldursGate/BaldursGate3/raw/lsxMODS/GustavDev/Globals/",
							"../data/BaldursGate/BaldursGate3/raw/lsxMODS/Gustav/Globals/"]
			for baseFolder in baseFolders:
				for settingFolder in [x for x in os.listdir(baseFolder) if os.path.isdir(baseFolder+x)]:
					subfolders = os.listdir(baseFolder+settingFolder)
					if "Characters" in subfolders:
						lsxFileName = baseFolder+settingFolder+"/Characters/_merged.lsx"
						parseCharacterFile(lsxFileName)
					if "Items" in subfolders:
						lsxFileName = baseFolder+settingFolder+"/Items/_merged.lsx"
						parseCharacterFile(lsxFileName)						
						
			# Some character names are in Marker files?
			markerFolder = "../data/BaldursGate/BaldursGate3/raw/lsxMODS/GustavDev/Story/Journal/Markers/"
			for markerFile in [f for f in os.listdir(markerFolder) if f.endswith(".lsx")]:
				xml = open(markerFolder+markerFile,'r', encoding = 'utf8')
				soup = BeautifulSoup(xml, "lxml")
				markerType = soup.find("attribute",{"id":"MarkerTargetObjectType"})["value"]
				if markerType == "Character":
					displayTextID = soup.find("attribute",{"id":"DisplayText"})["handle"]
					if displayTextID in localisation:
						displayText = localisation[displayTextID]
						uuid = soup.find("attribute",{"id":"MarkerTargetObjectUUID"})["value"]
						if displayText=="Track the Serial Killer":
							displayText = "Dolor Amarus"
						charData[uuid] = {"charName":displayText}
			
			# A voices file stores mappings between known and unknown labels
			#  (e.g. 'voice' and 'voice of Astarion')
			# The 'SpeakerUUID' field links to the 'MapKey' field in the character file _merged.lsx
			#voicesFile = "../data/BaldursGate/BaldursGate3/raw/Public/Gustav/Voices/Voices.lsx"
			#xml = open(voicesFile,'r', encoding = 'utf8')
			#soup = BeautifulSoup(xml, "lxml")
			#for voice in soup.find_all("node",{"id":"Voice"}):
			#	voice.find("attribute")
			
					
			# Write out to save time
			with open(charDataFilePath, "w") as outfile:
				outfile.write(json.dumps(charData))
		print("CHAR DATA")
		print(len(charData))
		
	def loadFlagData():
		global flagData
		flagDataFilePath = "../data/BaldursGate/BaldursGate3/flagData.json"
		if os.path.isfile(flagDataFilePath):
			f = open(flagDataFilePath)
			flagData = json.load(f)
		else:
			# Treat Flags and Tags as the same
			baseFolders = ["../data/BaldursGate/BaldursGate3/raw/lsxPUBLIC/GustavDev/Flags/",
							"../data/BaldursGate/BaldursGate3/raw/lsxPUBLIC/Gustav/Flags/",
							"../data/BaldursGate/BaldursGate3/raw/lsxPUBLIC/GustavDev/Tags/",
							"../data/BaldursGate/BaldursGate3/raw/lsxPUBLIC/Gustav/Tags/"]
			for baseFolder in baseFolders:
				files = os.listdir(baseFolder)
				files = [x for x in files if x.endswith(".lsx")]
				for file in files:
					xml = open(baseFolder+file,'r', encoding = 'utf8')
					soup = BeautifulSoup(xml, "lxml")
					description = soup.find("attribute",{"id":"Description"})["value"]
					uuid = soup.find("attribute",{"id":"UUID"})["value"]
					name = soup.find("attribute",{"id":"Name"})["value"]
					if name.endswith("description"):
						name = name[:-11]
					if description.strip()=="":
						description = name
					flagData[uuid] = description
				
			# Global flags
			d = open("../data/BaldursGate/BaldursGate3/globalFlags.csv").read()
			for line in [x for x in d.split("\n") if len(x)>0]:
				cat,lab,idx = line.split(",")
				flagData[idx] = lab
			# Write out
			with open(flagDataFilePath, "w") as outfile:
				outfile.write(json.dumps(flagData))
			
	
	def parseSpeakerList(speakerData):
		# speakers are not always listed in order,
		# so speakerList is a dictionary of speakerIndex (str) -> charName
		speakerList = {}
		if "speaker" in speakerData[0]:
			for speaker in speakerData[0]["speaker"]:
				indx = speaker["index"]["value"]
				if "list" in speaker:
					charID = speaker["list"]["value"]
					charName = ""
					if charID in charData:
						charName = charData[charID]['charName']
					else:
						charName = charID
					speakerList[indx] = charName
				else:
					# TODO: e.g. CAMP_Bard_AD.lsj: no 'list' property for speaker list.
					#  Something to do with mappipngs?
					speakerList[indx] = ""
					pass
		return(speakerList)

	def parseLSJ(data):	
		nodeData = data["save"]["regions"]["dialog"]["nodes"]
		if "RootNodes" in nodeData[0]:
			rootNodes = nodeData[0]["RootNodes"]
			rootNodes = [x["RootNodes"]["value"] for x in rootNodes]
			nodes = nodeData[0]["node"]
			speakerList = parseSpeakerList(data["save"]["regions"]["dialog"]["speakerlist"])
			pnodes = [parseNode(node,speakerList) for node in nodes]
			return(rootNodes,pnodes)
		else:
			print("\tError: no root nodes")
			return([],[])
		
	def getFlags(flags,flagType="CHECK"):
		flagText = ""
		for flag in flags:
			for subflag in flag["flag"]:
				flagUUID = subflag["UUID"]["value"]
				if flagUUID in flagData:
					flagDescription = flagData[flagUUID]
				else:
					flagDescription = flagUUID
				if "paramval" in subflag:
					paramval = subflag["paramval"]["value"]
				else:
					paramval = ""
				pvalue = subflag["value"]["value"]
				flagText += flagType + " FLAG: "+ flagDescription + " [" + str(paramval) + " / " + str(pvalue) + "]"  +"\n"
		flagText = flagText.strip()
		return(flagText)

	def parseNode(nx,speakerList):	
		#print("\n\n\n\n")
		#print(json.dumps(nx,indent=2))
		
		uuid = nx["UUID"]["value"]
		constructor = nx["constructor"]["value"]
		
		speaker = ""
		if "speaker" in nx:
			# the speakerIndex is an int, but the speakerList indices are strings
			speakerIndex = nx["speaker"]["value"]
			if speakerIndex == -666: # TODO: is the 
				speaker = "Narrator"		
			elif str(speakerIndex) in speakerList:
				speaker = speakerList[str(speakerIndex)]
		#print(speaker)

		txt = ""
		if "TaggedTexts" in nx:
			if "TaggedText" in nx["TaggedTexts"][0]:
				tt = nx["TaggedTexts"][0]["TaggedText"]
				# It's possible there are multiple texts,
				#  often due to gender (he / her / they)
				# So, collect texts and add rule note if there are any
				txts = []
				rules = []
				for t in tt:
					opTextID = t["TagTexts"][0]
					if "TagText" in opTextID:
						opTextID = t["TagTexts"][0]["TagText"][0]["TagText"]["handle"]
						opText = ""
						if opTextID in localisation:
							opText = localisation[opTextID]
						else:
							print("   Error - no localisation id specified: " + t["TagTexts"][0]["TagText"][0]["LineId"]["value"])
												  
						txts.append(opText)
						if "RuleGroup" in t:
							rt = t["RuleGroup"][0]["Rules"][0]
							if "Rule" in rt:
								if "Tags" in rt["Rule"][0]:
									ruleTags = rt["Rule"][0]["Tags"]
									ruleTags = [tag["Tag"][0]["Object"]["value"] for tag in ruleTags if "Tag" in tag]
									ruleDescriptions = [flagData.get(x,x) for x in ruleTags]
									if len(ruleDescriptions)>0:
										ruleText = " {" + "; ".join(["IF: "+x for x in ruleDescriptions]) + "}"
										txts[-1]+= ruleText
				txt = " /\n".join(txts)

		children = []
		jumptargetpoint = 0
		if "child" in nx["children"][0]:
			children = [x["UUID"]["value"] for x in nx["children"][0]["child"]]
		elif nx["constructor"]["value"] == "Jump":
			# If the jump value is 2, then this should connect
			# to the CHILDREN of the jump target, not the jump target
			#  (i.e. skips the jump target)
			#  But we can't fix that here because we haven't loaded
			#  all the child data, so leave till later
			children = [nx["jumptarget"]["value"]]
			jumptargetpoint = nx["jumptargetpoint"]["value"]
		elif nx["constructor"]["value"] == "Alias":
			children = [nx["SourceNode"]["value"]]

		
		roll = ""
		if "RollType" in nx:
			ability = nx["Ability"]["value"]
			skill = nx["Skill"]["value"]
			adv = ""
			if nx["Advantage"]["value"]==1:
				adv = " (ADV)"
			DCID = nx["DifficultyClassID"]["value"]
			if DCID in DCDict:
				DCID = str(DCDict[DCID])
			else:
				print("    DC ERROR "+DCID)
			# build roll
			roll = ability
			if nx["RollType"] in ["MeleeSpellAttack","MeleeUnarmedAttack","MeleeArmedAttack"]:
				roll = nx["RollType"]
			
			if skill !="":
				 roll += " (" + skill + ") " 
			roll += adv + " DC "+DCID
			if nx["constructor"]["value"] == "PassiveRoll":
				roll += " (Passive)"
		
		success = ""	
		if "Success" in nx:
			if nx["Success"]["value"]:
				success = "Pass"
			else:
				success = "Fail"
				
		approval = ""
		if "ApprovalRatingID" in nx:
			approvalID = nx["ApprovalRatingID"]["value"]
			
			
		checkflags = ""
		if "checkflags" in nx:
			if "flaggroup" in nx["checkflags"][0]:
				flags = nx["checkflags"][0]["flaggroup"]
				checkflags = getFlags(flags)
				
		setflags = ""
		if "setflags" in nx:
			if "flaggroup" in nx["setflags"][0]:
				flags = nx["setflags"][0]["flaggroup"]
				setflags = getFlags(flags,"SET")
				
				
		context = ""
		if "editorData" in nx:
			edDats = nx["editorData"][0]["data"]
			contextDescriptions = [dat["val"]["value"] for dat in edDats if dat["key"]["value"] in ["AnimationTags","NodeContext","stateContext"]]
			contextDescriptions = [x for x in contextDescriptions if len(x)>0]
			if len(contextDescriptions)>0:
				context = contextDescriptions[0]
			
				
		label = str(speaker) + ": "+txt
		if txt=="":
			label = roll
			if roll=="":
				label = success
				if success=="" and nx["constructor"]["value"] == "Jump":
					label = "JUMP"
				elif success=="" and nx["constructor"]["value"] == "Alias":
					label = "ALIAS"
		if checkflags!="":
			label += "\n"+ checkflags
		if setflags!="":
			label += "\n"+ setflags
		if context != "":
			label += "\n"+ "ACTION: "+context
					
		
		return({"uuid":uuid,
				"constructor":constructor,
				"children":	children,
				"text":	txt,
				"speaker":speaker,
				"roll": roll,
				"success": success,
				"label":label,
				"jumptargetpoint":jumptargetpoint,
				"checkflags": checkflags,
				"setflags": setflags,
				"context": context})
	# END OF PARSE NODE

	def nodeToVGDCFormat(rootNodes,nodes,dialogTitle):
		# Build a child dictionary so we can look up jumps
		childDict = {"START":[]}
		for rootNode in rootNodes:
			childDict["START"].append(rootNode)
		for node in nodes:
			uuid = node["uuid"]
			childDict[uuid] = []
			for child in node["children"]:
				childDict[uuid].append(child)
	
		out = []
		# Add root nodes
		out.append({"ACTION": "START", "_id":"START-"+dialogTitle, "_children":rootNodes})
		
		for node in nodes:
			# 'TagCinematic', 'Visual State', 'PassiveRoll', 'RollResult', 
			# 'Alias', 'ActiveRoll', 'Jump', 'TagQuestion', 'TagGreeting', 'TagAnswer'
			# 'Nested Dialog'
			line = {}
			if node["constructor"] in ["TagAnswer","TagQuestion","TagGreeting"]:
				line = {node["speaker"]: node["text"]}
			elif node["constructor"] in ["ActiveRoll","PassiveRoll"]:
				line = {node["speaker"]: node["text"], "_roll":node["roll"]}
			elif node["constructor"] in ["RollResult","Jump","Alias"]:
				line = {"ACTION": node["label"]}
			elif node["constructor"] in ["Visual State"]:
				line = {"ACTION": node["context"]}
			elif node["constructor"] == "TagCinematic":
				line = {"ACTION": "CINEMATIC"}
				if len(node["context"])>0:
					line["_context"]= node["context"]
			else:
				line = {"ACTION": node["text"]}
		
			line["_id"] = node["uuid"]
			line["_checkflags"] = node["checkflags"]
			line["_setflags"] = node["setflags"]
			line["_lt"] = node["constructor"]
		
			if node["jumptargetpoint"]==2:
				# Jump to children of target
				line["_children"] = childDict[node["children"][0]]
			else:
				line["_children"] = node["children"]
			out.append(line)
		
		return(out)
			
	def nodesToGraphVis(rootNodes,nodes):
		
		# Build a child dictionary so we can look up jumps
		childDict = {"START":[]}
		for rootNode in rootNodes:
			childDict["START"].append(rootNode.replace("-",""))
		for node in nodes:
			uuid = node["uuid"].replace("-","")
			childDict[uuid] = []
			for child in node["children"]:
				childDict[uuid].append(child.replace("-",""))
	
		out = 'digraph G {\nrankdir="LR"\nnode [shape=box]\n START [label="START"];\n'
		
		for rootNode in rootNodes:
			rid = rootNode.replace("-","")
			out += f'START -> I{rid}\n'
		
		for node in nodes:
			uuid = node["uuid"].replace("-","")
			lab = node["label"]
			lab = lab.replace('"',"'")
			out += f'I{uuid} [label="{lab}"];\n'
			children = node["children"]
			if node["jumptargetpoint"]==2:
				#print(children)
				# Jump to destinations of children
				children = childDict[node["children"][0].replace("-","")]
			for child in children:
				cid = child.replace("-","")
				out += f'I{uuid} -> I{cid}\n'
		out += "\n}"
		print(out)
		return(out)
		
	def identifyWhichOriginCharactersAreShownPCOptions(lines):
		global seenEdges
		# Identify which origin characters can speak each PC option.
		#  To do this, we need to follow the paths and keep track of 
		#  the possible speakers. Modify the lines in-place to store this info.
		# If there's only one origin character who can be given these lines,
		#  then rename PC to that origin character
		
		# TODO: There are also lines that exclude characters, e.g.:
		#	{"PC": "Vampires aren't invincible. We could take him.", "_id": "823bc205-2366-4ff3-9642-d5455ffe91dd", "_checkflags": "CHECK FLAG: |Really Wyll, superhero warlock| [1 / False]\nCHECK FLAG: REALLY_MINSC [1 / False]\nCHECK FLAG: REALLY_LAEZEL [1 / False]", "_setflags": "", "_lt": "TagQuestion", "_children": [
		
		# Make dictionary of id to index position,
		#  so we can index the line directly
		idToLineIndex = {}
		for i,line in enumerate(lines):
			idToLineIndex[line["_id"]] = i
			
		def getFlags(line):
			if "_checkflags" in line:
				flags = line["_checkflags"]
				if len(flags)>0:
					flags = flags.split("\n")
					flags = [x.split("[",1) for x in flags]
					flags = [(var.replace("CHECK FLAG: ","").strip(), val.replace("]","").strip()) for var,val in flags]
					return(flags)
			# Else
			return([])
			
		
		def trackPossibleSpeakers(line, currentCharFlags=["PC"]):
			global seenEdges
			# Does it have an origin character flag? (could be more than one)
			flags = getFlags(line)
			originCharFlags = [conditionToTrueCharName[flagVar] for flagVar,flagVal in flags if flagVar in conditionToTrueCharName and flagVal.count("True")>0]
			if len(originCharFlags)>0:
				# if so, update variable (the constraint is overwritten)
				currentCharFlags = originCharFlags
			# if the speaker is PC ...
			speaker = [k for k in line if not k.startswith("_")][0]
			if speaker == "PC":
				# ... then add the current char flags to the line
				if "_posSpk" in line:
					line["_posSpk"] = list(set(line["_posSpk"]+currentCharFlags))
				else:
					line["_posSpk"] = currentCharFlags
			# Follow paths from the line to all children
			#  (if we haven't followed the path already)
			#  (this assumes a markov principle)
			if "_children" in line:
				for child in line["_children"]:
					edge = (line["_id"], child)
					if not edge in seenEdges:
						seenEdges.append(edge)
						trackPossibleSpeakers(lines[idToLineIndex[child]],currentCharFlags)
		
		# Keep track of which edges have been seen (global)
		seenEdges = []
		# Follow paths from all starting lines
		for startingLine in [line for line in lines if "ACTION" in line and line["ACTION"]=="START"]:
			trackPossibleSpeakers(startingLine)
			
		# Now the lines have the constraints stored in the "_posSpk" var
		#  so go through each line and identify whether there's a constraint
		for line in lines:
			speaker = [k for k in line if not k.startswith("_")][0]
			if speaker == "PC" and "_posSpk" in line:
				 possibleChars = list(set(line["_posSpk"]))
				 if len(possibleChars) == 1 and not possibleChars[0]=="PC":
				 	newSpeaker = possibleChars[0]
				 	# Reorder keys to put dialogue at the start
				 	copiedLine = copy.deepcopy(line)
				 	for k in [x for x in line]:
				 		del line[k]
				 	line[newSpeaker] = copiedLine[speaker]
				 	for k in [x for x in copiedLine if x!=speaker]:
				 		line[k] = copiedLine[k]
		# TODO: Tidy up by deleting unnecessary "_posSpk" entries
		for line in lines:
			if "_posSpk" in line:
				if list(set(line["_posSpk"])) == ["PC"] or line["_posSpk"] == []:
					del line["_posSpk"]
				 	
	# End of identifyWhichOriginCharactersAreShownPCOptions
	#############################			 	
			
	# Start main loop for processing talk file
	print(fileName)
	loadLocalisation()
	print(len(localisation))
	loadCharacterData()
	loadFlagData()

	out = []	
	fileNamesToProcess = []
	dialogDirs = ['../data/BaldursGate/BaldursGate3/raw/Mods/Gustav/Story/Dialogs/',
			  	  '../data/BaldursGate/BaldursGate3/raw/Mods/GustavDev/Story/Dialogs/']
	for dialogDir in dialogDirs:
		px = pathlib.Path(dialogDir)
		fileNamesToProcess += [str(x) for x in px.rglob("*.lsj")]
#		dialogFolders = [x for x in os.listdir(dialogDir) if os.path.isdir(dialogDir+x) and not x in ["DialogVariables","MainMenu","ScriptFlags","Tutorial","WorldCinematics"]]
#		for folder in dialogFolders:
#			fileNamesToProcess += [dialogDir+folder+"/"+x for x in os.listdir(dialogDir+folder+"/") if x.endswith(".lsj")]	
#	fileNamesToProcess = ['../data/BaldursGate/BaldursGate3/raw/Mods/Gustav/Story/Dialogs/Companions/Astarion_Recruitment.lsj',
#						  '../data/BaldursGate/BaldursGate3/raw/Mods/GustavDev/Story/Dialogs/Companions/Scratch_SummonUnavailable_PAD.lsj',
#						  '../data/BaldursGate/BaldursGate3/raw/lsxMODS/GustavDev/Story/Dialogs/Companions/Minsc_InParty_Nested_PersonalQuestions.lsj']
#	fileNamesToProcess = ['../data/BaldursGate/BaldursGate3/raw/Mods/Gustav/Story/Dialogs/Camp/Campfire_Moments/CAMP_AstarionHunger_SCO_Companion.lsj']
	
	for fileNameToProcess in fileNamesToProcess:
		#dialogTitle = os.path.basename(fileNameToProcess).replace(".lsj","")
		dialogTitle = "/".join(fileNameToProcess.split("/")[-2:]).replace(".lsj","")
		print(dialogTitle)
		f = open(fileNameToProcess)
		data = json.load(f)
		synopsis = data["save"]["regions"]["editorData"].get("synopsis",{"value":""}).get("value","")
		rootNodes,pnodes = parseLSJ(data)
		#print(list(set([p["constructor"] for p in pnodes])))
		#nodesToGraphVis(rootNodes,pnodes)
		
		lines = nodeToVGDCFormat(rootNodes,pnodes,dialogTitle)
		
		# Identify which origin characters can speak each PC option,
		#  and set the speaker name if it's constrained to only one origin char
		# (changes are done in-place)
		identifyWhichOriginCharactersAreShownPCOptions(lines)
		
		
		out.append({"LOCATION": dialogTitle})
		out.append({"ACTION": synopsis})
		out += lines


	if asJSON:
		print(json.dumps({"text":out}, indent = 4))
		return(json.dumps({"text":out}, indent = 4))
	return(out)


def postProcessing(out):
	print("post-processing")
	# Find lines of dialogue with "{IF:" statements, split into separate options.
	# We'll keep the format of not using the CHOICE structures, 
	# so this requires finding all the parents and re-directing to the choices.
	
	# TODO: Lines like this could be assigned to characters, too?
	#   though note that it should only happen if the char flag is true [1 / False]
	# {"PC": "Fine. But not a drop more than you need.", "_id": "a30a564e-7ef7-bd7d-7fcc-40e7c1999166", "_checkflags": "CHECK FLAG: |Karlach, Hells' champion. Tiefling origin. Whether or not she's shapeshifted.| [1 / False]\nCHECK FLAG: REALLY_GALE [1 / False]", "_setflags": "SET FLAG: For an achievement - agree to let Astarion bite you. Doesn't mean he ends up actually succeeding, depending on the origin. [1 / True]", "_lt": "TagQuestion", "_children": [
	

	out2 = []
	childLinksToFix = {}
	for line in out:
		charName = [x for x in line if not x.startswith("_")][0]
		dialogue = line[charName]
		if dialogue.count("{IF:") == 0:
			out2.append(line)
		else:
			parts = dialogue.split("/\n")
			for i,part in enumerate(parts):
				newDialogue = part
				condition = ""
				if newDialogue.count("{IF:")>0:
					condition = newDialogue[newDialogue.index("{IF:")+4:-1].strip()
					if condition.endswith("}"):
						condition = condition[:-1].strip()
					newDialogue = newDialogue[:newDialogue.index("{IF:")].strip()
				newID = line["_id"]+"-"+str(i)
				# Track links to change parents later
				if line["_id"] in childLinksToFix:
					childLinksToFix[line["_id"]].append(newID)
				else:
					childLinksToFix[line["_id"]] = [newID]

				# Change charName if flag is appropriate
				newCharName = charName
				if newCharName == "PC":
					if condition in conditionToTrueCharName:
						newCharName = conditionToTrueCharName[condition]
				
				# TODO: combine check flags
				newFlags = line["_checkflags"]+"\n"+"CHECK FLAG: "+condition
				newFlags = newFlags.strip()
				newLine = {
					newCharName: newDialogue, 
					"_id": newID,
					"_checkflags": newFlags,
					"_setflags": line["_setflags"],
					"_lt": line["_lt"],
					"_children":line["_children"]}
				# Just in case, add all other keys
				for key in line:
					if (not key in newLine) and key.startswith("_"):
						newLine[key] = line[key]
				out2.append(newLine)
	
	# Fix the previous links	
	for line in out2:
		newChildren = []
		if "_children" in line:
			for child in line["_children"]:
				if child in childLinksToFix:
					newChildren += childLinksToFix[child]
				else:
					newChildren.append(child)
			line["_children"] = newChildren


	return(out2)
					
					
					