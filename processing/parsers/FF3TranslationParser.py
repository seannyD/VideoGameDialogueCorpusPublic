import json,re
from bs4 import BeautifulSoup, NavigableString, Tag

def parseFile(fileName,parameters={},asJSON=False):

	characterNameDictionary = {
		"[10][02]" :"Luneth",  # red
		"[11][02]" : "Refia", # blue
		"[12][02]" : "Arc", # green
		"[13][02]" : "Ingus",# red2
		"[0C]": "Luneth",  # This is technically the party leader?
		"[E4]": "\"", # closing quote
		"[AA]": "ö",
		"[09]": " ",
	# These are job names for each character
		"[10][01]":" Job ","[11][01]":" Job ","[12][01]":" Job ","[13][01]":" Job "
	}
	# These are job names for each character
	#[10][01]/[11][01]/[12][01]/[13][01]
	# These are character names.
	# [10][02],[11][02],/[12][02],and [13][02]
	# [0C] is the party leader?

	def cleanName(charName):
		charName = charName.replace("*","").strip()
		charName = charName.title()
		charName = charName.replace("'S","'s")
		return(charName)
		
	def cleanDialogue(txt):
		for cn in characterNameDictionary:
			txt = txt.replace(cn,characterNameDictionary[cn])
		txt = txt.replace("/"," ")
		txt = txt.replace("!","! ")
		txt = re.sub("\.([^\]\.])",". \\1",txt)
		txt = txt.replace("[.]"," ... ")
		txt = txt.replace(",",", ")
		txt = re.sub(" +"," ",txt) 
		txt = txt.replace("#",". ")
		txt = txt.strip()
		return(txt)
	
	def cleanAction(txt):
		txt = txt.strip()
		txt = re.sub("^ENTER","",txt)
		txt = txt.strip()
		txt = re.sub("^\(","",txt)
		txt = re.sub("\)$","",txt)
		return(txt.strip())

	o = open(fileName)
	txt = o.read()
	o.close()
	
	# Split into lines
	lines = [line for line in txt.split("\n") if len(line.strip())>0]

	if fileName.endswith("data_bank2.txt"):
		b2DialogueMessages = 	["msg5=","msg39","msg40","msg41","msg42","msg43","msg44","msg80","msg82","msg83","msg84","msg85","msg86","msg88","msg89"]
		lines = [x for x in lines if any([x.count(y)>0 for y in b2DialogueMessages])]

	
	# Recognise lines
	out = []
	for line in lines:
		line = line[line.index("=")+1:]
		line = line.replace("apprentices:","apprentices - ")
		line = line.replace("three:","three - ")
		line = line.replace("Year:","Year - ")
		line = line.replace("Mrs.","Mrs#")
		# A single message can have both action and dialogue.
		#  so split these first.
		parts = re.split("//+",line)
		for part in parts:
			bits = re.split("([A-Za-z0-9\[\]\? ,'#]+):",part)
			if len(bits[0])>0:
				if len(bits)>1:
					# some action before the dialogue
					out.append({"ACTION":cleanDialogue(bits[0])})
				elif bits[0].startswith("Obtained") or bits[0].startswith("Obtained") or bits[0].count("restored!")>0 or bits[0]=="Revived!" or bits[0].startswith("Received"):
					out.append({"ACTION":cleanDialogue(bits[0])})
				else:
					out.append({"NPC":cleanDialogue(bits[0])})
			if len(bits)>1:
				# bit [1] is name, bit [2] is dialogue etc.
				for charName,dialogue in zip(bits[1::2],bits[2::2]):
					if charName in characterNameDictionary:
						charName = characterNameDictionary[charName]
					charName = charName.replace("#",".")
					out.append({charName: cleanDialogue(dialogue)})
		
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)