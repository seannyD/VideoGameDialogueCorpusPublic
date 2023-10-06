import json,re,os

def parseFile(fileName,parameters={},asJSON=False):

	def cleanAction(txt):
		return(txt)

	def cleanDialogue(txt):
		txt = txt.replace("⬅"," / ")
		if txt.count('")')>0:
			txt = txt[:txt.index('")')]
		txt = txt.strip()
		if txt.endswith(")"):
			txt = txt[:-1]
		txt = txt.replace("{"," (").replace("}",") ")
		txt = txt.strip()
		return(txt)
	
	def cleanName(charName):
		charName = charName.title()
		return(charName)

	
	o = open(fileName)
	d = o.read()
	o.close()
	
	loc = {"LOCATION": fileName[fileName.rindex("/")+1:].replace(".yack.txt","")}
	
	out = [loc]
	# 	elaine: SAY(@40624:ELAINE:You know I always try to stay a step ahead.)
	# 4 SAY("@40625:GUYBRUSH:{whoa}Have you done something new with your hair?") -> $nestednode17	[once || yackChoices() <= 1]	
	bits = re.findall(' SAY\\("?@([0-9]+):(.+?):(.+?)\n',d)
	for idNum,charName,dialogue in bits:
		out.append({cleanName(charName): cleanDialogue(dialogue), "_ID":idNum})
	
	
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)
	
	
def postProcessing(out):
	# Not yet recursive!

	def cleanLine(txt):
		txt = txt.replace("⬅"," / ")
		txt = txt.replace("{"," (").replace("}",") ")
		txt = txt.replace("<"," (").replace(">",") ")
		txt = re.sub("\\[.+?\\]"," ",txt)
		txt = re.sub(" +"," ",txt)
		txt = txt.strip()
		return(txt)

	langs = {}
	# Load other languages
	base = "../data/MonkeyIsland/ReturnToMonkeyIsland/raw/"
	langFiles = os.listdir(base)
	langFiles = [x for x in langFiles if x.endswith(".tsv")]
	for langFile in langFiles:
		lang = langFile[langFile.index("_")+1:langFile.index("_")+3]
		print(lang)
		langs[lang] = {}
		o = open(base+langFile)
		d = o.read()
		o.close()
		for line in d.split("\n")[1:-1]:
			bits = line.split("\t")
			textID = bits[1]
			text = cleanLine(bits[2])
			charName = bits[0]
			if not charName in ["HOVER","TEXT"]:
				langs[lang][textID] = (charName,text)
	
	# Some lines are not in yack files, add them from localisation
	idsInYacks = [x["_ID"] for x in out if "ID_" in x]
	idsInLoc = [x for x in langs["en"].keys()]
	for idx in list(set(idsInLoc) - set(idsInYacks)):
		charName = langs["en"][idx][0].title()
		if charName == "Guybrush":
			charName = "Guybrush (internal)"
		dialogue = langs["en"][idx][1]
		out.append({charName:dialogue, "_ID":idx})
	
	# Add translations in other languages
	for line in out:
		if "_ID" in line:
			lineID = line["_ID"]
			for lang in langs:
				if lang != "en":
					if lineID in langs[lang]:
						line["_"+lang.upper()] = langs[lang][lineID][1]
	
	out2 = []	
	seenIDs = []
	for line in out:
		if "_ID" in line:
			if not line["_ID"] in seenIDs:
				out2.append(line)
			seenIDs.append(line["_ID"])
		else:
			out2.append(line)
	
	return(out2)