from bs4 import BeautifulSoup
import json, re
# TODO: This site https://finalfantasy.fandom.com/wiki/Final_Fantasy_VII_Remake_script
# has lines like "(Upon talk to X ...)", which suggest optionality.
# However, this doesn't suggest where the optional dialogue ends.

# TODO: Some lines of dialogue in Remake have italics, which breaks the parser. But in FFVI, italics indicate the speaker name. Need to get around this. But might require collecting lines first, then parsing? Ugh.

# For this site: https://finalfantasy.fandom.com/wiki/Final_Fantasy_VI_SNES_script#Kefka.27s_Tower_.2F_Ending
# the dialogue is split into main narrative and optional dialogue.
# We match up each optional dialogue to its section, then add it in as e.g.:
# 		{"CHOICE": [
#			[],
#			[{"Cloud": "Buy one "}]
#       ]},
# There is a section called "other" which I've treated as optional. Each line of dialogue is treated as optional, which suggest more flexibility that there really is, but there's no other indication of how the dialogue breaks up.


def cleanLine(txt):
	if txt.strip().startswith(">"):
		return("")
	txt = re.sub("^:","",txt)
	# don't include player input options
	txt = txt.strip()
	# Remove lines that start with parentheses and have nothing else
	txt = re.sub(r'^\([^)]*\)', '', txt)
	txt = txt.replace("...","... ")

	txt = txt.replace("\n"," ")
	txt = re.sub(" +"," ",txt)
	return(txt)
	

def parseFile(fileName,parameters={},asJSON=False):

	# TODO:
	# For this site: https://finalfantasy.fandom.com/wiki/Final_Fantasy_VI_SNES_script#Kefka.27s_Tower_.2F_Ending
	# the dialogue is split into main narrative and optional dialogue.
	# At the moment, everything is just dumped into the data.json
	# We could match up each optional dialogue to its section, then add it in as e.g.:
	# 		{"CHOICE": [
	#			[],
	#			[{"Cloud": "Buy one "}]
	#       ]},

	o = open(fileName)
	d = o.read()
	o.close()
	
	all = BeautifulSoup(d,'html.parser')
	toctext = [x.getText() for x in all.find_all("span",{"class":"toctext"})]
	tocnumber = [x.getText() for x in all.find_all("span",{"class":"tocnumber"})]
	
	toc = [x for x in zip(toctext,tocnumber)]
	toc  = [x for x in toc if x[1][0]=="1"]
	tocIndex = -1
	
	d = d[d.index(parameters["scriptStartCue"]):d.index(parameters["scriptEndCue"])]

	script = BeautifulSoup(d, 'html.parser')
	
	sectionDialogue = {}
	out = []
	
	optionalDialogueSection = False
	
	optionsCharName = "NARRATIVE"

	for child in script.children:
		
		section = ""
		
		if child.name=="h2":
			if "Optional Dialogue" in child.getText():
				optionalDialogueSection = True
	
		if child.name=="h4":
			section = child.find("span", {"class":"mw-headline"}).getText()
			if section in [x[0] for x in toc]:
				while section != toc[tocIndex][0]:
					tocIndex += 1
					if tocIndex >= len(toc):
						tocIndex = 0
			else:
				toc.append((section,len(toc)))
	
		if child.name=="p":
			charName = "NARRATIVE"
			for bit in list(child.children):
				# if charName is None, and it's a bit of text, this is narrative
				if isinstance(bit, str):
					bit = cleanLine(bit)
					if len(bit)>0:
						outx = {charName:bit}
						if optionalDialogueSection:
							outx = {"CHOICE":[[],[outx]]}
						if not charName in parameters["ignoreCharacters"]:
							if parameters["scriptHasOptionalDialogueSection"]:
								try:
									sectionDialogue[toc[tocIndex][1]].append(outx)
								except:
									sectionDialogue[toc[tocIndex][1]] = [outx]
							else:
								out.append(outx)
				else:
					if bit.name in ["b","i"]:
						charName = bit.getText().replace(":","").strip()
						charName = charName.title()
						if bit.name == "i" and not parameters["scriptHasOptionalDialogueSection"]:
							lastDialogue = out[-1]
							lastSpeaker = [x for x in lastDialogue.keys()][-1]
							if lastSpeaker == "CHOICE":
								lastDialogue = lastDialogue["CHOICE"][-1]
								lastSpeaker = [x for x in lastDialogue.keys()][-1]
							lastDialogue[lastSpeaker] += " " + bit.getText()
						# todo: we also need to add the NEXT line after the italics.
		
		if child.name == "dl":
			optionsCharName = child.find("dt").getText()
		
		if child.name == "ul":
			currentOptionsCharName = optionsCharName
			choices = {"CHOICE":[]}
			lis = child.find_all("li")
			for bits in lis:
				liLines = []
				for bit in bits:
					if isinstance(bit,str):
						bit = cleanLine(bit)
						if len(bit)>0:
							liLines.append({currentOptionsCharName:bit})
					else:
						if bit.name in ["b","i"]:
							currentOptionsCharName = bit.getText().replace(":","").strip()
							currentOptionsCharName = currentOptionsCharName.title()
				choices["CHOICE"].append(liLines)
			# Add choices to main object
			if not optionsCharName in parameters["ignoreCharacters"]:
				if parameters["scriptHasOptionalDialogueSection"]:
					try:
						sectionDialogue[toc[tocIndex][1]].append(outx)
					except:
						sectionDialogue[toc[tocIndex][1]] = [outx]
				else:
					out.append(choices)
	
	if parameters["scriptHasOptionalDialogueSection"]:
		for tt,tid in toc:
			if tid in sectionDialogue.keys():
				for x in sectionDialogue[tid]:
					out.append(x)
				
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)