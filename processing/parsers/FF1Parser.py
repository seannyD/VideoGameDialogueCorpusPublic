import json,re

def parseFile(fileName,parameters={},asJSON=False):

	def cleanAction(txt):
		txt = txt.replace("\t","")
		txt = txt.replace("_","")
		txt = txt.replace("*","")
		txt = txt.replace('/',"")
		txt = txt.replace('\\',"")
		txt = txt.replace('|',"")
		txt = re.sub("--+",". ",txt)
		txt = re.sub(" +"," ",txt)
		txt = txt.strip()
		return(txt)

	def cleanDialogue(txt):
		txt = txt.replace("(s)","") # code for stationary
		txt = txt.replace("\t","")
		txt = re.sub(" +"," ",txt)
		txt = re.sub("--+",". ",txt)
		txt = txt.strip()
		return(txt)
	
	def cleanName(charName):
		global genericCharCounter
		
		if charName in genericCharCounter:
			genericCharCounter[charName]+=1
			charName += " " + str(genericCharCounter[charName])
		charName = charName.replace("'S","'s")
		return(charName)

	# Some dialogue attributed to the same character name,
	# is given to different characters
	global genericCharCounter
	genericCharCounter = {"Person":0, "Guard":0, "Woman":0, "Man":0,"Citizen":0, "Mermaid":0}

	o = open(fileName)
	d = o.read()
	o.close()
		
	d = d[d.index(parameters["startText"]):d.index(parameters["endText"])]
	
	parts = [re.sub(" +"," ",x.replace("\n"," ")).strip() for x in d.split("\n\n")]
	
	out = []
	for p in parts:
		if p.startswith("INTERIOR:") or p.startswith("EXTERIOR:") or p.startswith("-"):
			# Location
			out.append({"LOCATION": cleanAction(p)})
		elif re.match("^[A-Z '\\.]+:",p):
			# Dialogue
			if p.count("(r)")==0:
				# Not repeated
				charName = p[:p.index(":")].strip().title()
				dialogue = cleanDialogue(p[p.index(":")+1:].strip())
				comments = [x.group() for x in re.finditer("\(.+?\)",dialogue)]
				for comm in comments:
					dialogue = dialogue.replace(comm," ").strip()
				dialgoue = re.sub(" +"," ",dialogue)
				commentText = " . ".join([x.replace("(","").replace(")","") for x in comments]).strip()
				if len(dialogue)>0:
					if len(commentText)>0:
						out.append({cleanName(charName):dialogue, "_Comment":commentText})
					else:
						out.append({cleanName(charName):dialogue})
		elif p.startswith("(") or p.startswith("***"):
			# Comment
			out.append({"COMMENT":cleanAction(p)})
		elif p.count("~~~")>0:
			# Chapter
			if p.count("|")>0:
				p = p[p.index("|")+1:]
				p = p[:p.index("|")].strip()
				out.append({"LOCATION":p})
		else:
			# Action (including < >)
			actionText = cleanAction(p)
			if len(actionText)>0:
				out.append({"ACTION": actionText})

	
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)