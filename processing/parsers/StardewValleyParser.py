import yaml,re

def readYAML(fileName):
	o = open(fileName)
	d = o.read()
	o.close()
	txt = yaml.safe_load(d)
	return(txt)
	
def cleanStardewDialogue(txt):
	txt = txt.replace("#"," ")
	txt = txt.replace('"'," ")
	txt = txt.replace('%fork'," ")
	txt = txt.replace('%'," ")
	txt = txt.replace('\.\.\.'," ... ")
	txt = txt.replace('<'," ")
	txt = txt.replace('>'," ")
	txt = re.sub("\$[a-z0-9][0-9]?"," ",txt)
	txt = re.sub(" +"," ",txt)
	return(txt.strip())
	
def parseDialogue(txt,fileName,parameters):
	characterName = fileName[fileName.rindex("/")+1:fileName.rindex(".yaml")]
	characterName = characterName.replace("MarriageDialogue","")
	
	out = []
	if len(characterName)>0:
		if characterName=="rainy":
			for line in txt["content"]:
				out.append({line: cleanStardewDialogue(txt["content"][line]),"_Context":"rainy"})
				out.append({"ACTION":"---"})
		else:
			for line in txt["content"]:
				# some keys can be numbers, and these are converted to int
				dialogue = txt["content"][line]
				parts = [x for x in dialogue.split("#") if x.count("_")==0] 
				for part in parts:
				#	if part.startswith('$q'):
				#		preQuestion,choice = parseQuestion(characterName, part)
				#		out.append(preQuestion)
				#		out.append({"CHOICE":choice})
				#	else:
					dlg = cleanStardewDialogue(part)
					if len(dlg)>1:
						out.append({characterName: dlg, "_Context":str(line)})
						out.append({"ACTION":"---"})
	return(out)
	
def parseQuestion(characterName, dialogue):
	dialogue = dialogue.split("$r")
	dialogue_spk = [re.findall('#.+?[#"]',x)[0] for x in dialogue]
	dialogue_nextD = [re.findall(" [A-Za-z].+?#",x)[0][1:-1] for x in dialogue]
	preQuestion = {characterName:cleanStardewDialogue(dialogue_spk[0])}

	choice = []
	for reaction,nxt in zip(dialogue_spk[1:],dialogue_nextD[1:]):
		react = cleanStardewDialogue(reaction)
		if len(react)>1:
			choice.append([{"PC":react, "_GOTO":characterName+"/"+nxt}])
	return((preQuestion,choice))
	
def parseEvent(txt,fileName,parameters):
	out = []
	for key in txt["content"]:
		line = txt["content"][key]
		for part in line.split("/"):
			if part.startswith("speak"):
				characterName = part.split(" ")[1].strip()
				dialogue = re.findall('\\".+?\\"',part)
				if len(dialogue)>0:
					dialogue= dialogue[0]
					if dialogue.startswith('"$q'):
						preQuestion,choice = parseQuestion(characterName, dialogue)
						if len([x for x in preQuestion.items()][0])>1:
							out.append(preQuestion)
						if len(choice)>0:
							out.append({"CHOICE":choice})
					else:
						# dialogue might have several lines.
						# We need to split them so that the ^ separator works properly
						dialogueLines = [x for x in dialogue.split("#") if x.count("_")==0]
						for dialogueLine in dialogueLines:
							dialogueLine = cleanStardewDialogue(dialogueLine)
							if len(dialogueLine)>1:
								out.append({characterName:dialogueLine})
		if out[-1]!={"ACTION":"---"}:
			out.append({"ACTION":"---"})
	return(out)
			
def parseFile(fileName,parameters={},asJSON=False):
	
	txt = readYAML(fileName)
	
	out = []
	if fileName[fileName.rindex("/")+1:].startswith("Event_"):
		out = parseEvent(txt,fileName,parameters)
	else:
		out = parseDialogue(txt,fileName,parameters)
	
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)

def findCharacterKey(item):
	for key in item:
		if not key.startswith("_"):
			return(key)
	return(item.keys()[0])


def findEventKey(item):
	if "_Context" in item:
		characterName = findCharacterKey(item)
		event = item["_Context"]
		return(characterName+"/"+event)
	else:
		return("!")

def postProcessing(out):
	print("    Post-processing ...")
	# build list of character/context keys
	altOut = {}
	for item in out:
		key = findCharacterKey(item)
		if key!="CHOICE":
			if "_Context" in item:
				context = item["_Context"]
				altOut[key+"/"+context] = item[key]
	
	# Add responses in
	keysToDelete = []
	for item in out:
		key = findCharacterKey(item)
		if key=="CHOICE":
			for choice in item[key]:
				if "_GOTO" in choice[0]:
					followupKey = choice[0]["_GOTO"]
					followupChar = followupKey.split("/")[0]
					choice.append({followupChar:altOut[followupKey]})
					keysToDelete.append(followupKey)
					
	# Remove duplicated keys
	out = [x for x in out if not findEventKey(x) in keysToDelete]
	
	# Split dialogue dependant on gender
	
	def walkChoices(lines):
		outx = []
		for line in lines:
			k = [x for x in line if not x.startswith("_")][0]			
			if k=="CHOICE":
				choices = []
				for choice in line[k]:
					choices.append(walkChoices(choice))
				outx.append({"CHOICE":choices})
			else:
				dlg = line[k]
				if dlg.count("^")>0:
					parts = dlg.split("^")
					if len(parts)>2:
						print("ERROR")
						print(dlg)
					bit = {"CHOICE": [
						[{"STATUS":"Player is male"},   {k:parts[0]}],
						[{"STATUS":"Player is female"}, {k:parts[1]}]]}
					outx.append(bit)
				else:
					outx.append(line)
		return(outx)
		
	out2 = walkChoices(out)

	return(out2)	
			