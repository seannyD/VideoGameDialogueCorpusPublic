from bs4 import BeautifulSoup
import json, re

def cleanLine(txt):
	# don't include player input options
	if txt.strip().startswith(">"):
		return("")

	txt = txt.strip()
	txt = re.sub("^:","",txt)
	txt = txt.strip()
	# Remove lines that start with parentheses and have nothing else
	txt = re.sub(r'^\([^)]*\)', '', txt)
	txt = txt.replace("...","... ")
	txt = txt.replace("[","").replace("]","")

	txt = txt.replace("\n"," ")
	txt = re.sub(" +"," ",txt)
	return(txt)
	

def parseFile(fileName,parameters={},asJSON=False):
	global currentOptionsCharName

	def choiceParser(child):
		global currentOptionsCharName
		
		choices = {"CHOICE":[]}
		#lis = child.find_all(["li","ul"], recursive=False)
		for lix in child:
			liLines = []
			if lix.name=="li":
				for bit in lix:
					if isinstance(bit,str):
						if len(cleanLine(bit))>0:
							liLines.append({currentOptionsCharName:cleanLine(bit)})
						elif bit.strip().startswith("("):
							liLines.append({"STATUS": cleanLine(bit.replace("(","").replace(")",""))})
					elif bit.name == "ul":
						liLines.append(choiceParser(bit))
					elif bit.name in ["b","i"]:
						currentOptionsCharName = bit.getText().replace(":","").strip()
						currentOptionsCharName = currentOptionsCharName.title()
					else:
						if len(bit.getText()) >0:
							liLines.append({currentOptionsCharName: cleanLine(bit.getText())})
			if len(liLines)>0:
				choices["CHOICE"].append(liLines)
		return(choices)
	
	def removeAHREFTags(child):
		exx = list(child.children)
		for i in range(len(exx)):
			if exx[i].name == "a":
				exx[i-1] += exx[i].getText()+exx[i+1].getText()
				exx[i].replace_with("")
				exx[i+1].replace_with("")
		return(exx)

	o = open(fileName)
	d = o.read()
	o.close()
	
	# Remove italic elements
	d = d.replace("<i>","*").replace("</i>","*")
	
	# Remove href links
	d = re.sub("<a.+?>(.+?)</a>","\\1",d)
	
	d =  d.replace("note 2","")
	
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
			# Get rid of <a> tags by merging them with surrounding parts
			children = removeAHREFTags(child)
		
			choiceSection = False
			choiceSectionParts = {"CHOICE":[[]]}
			charName = "NARRATIVE"
			for bit in children:
				# if charName is None, and it's a bit of text, this is narrative
				if isinstance(bit, str):
					if bit.strip().startswith("(If") or bit.strip().startswith("(When"):
						choiceSection = True
						choiceSectionParts["CHOICE"][0].append({"STATUS":cleanLine(bit.replace("(","").replace(")",""))})
					elif bit.strip().startswith("("):
						outx = {"ACTION":cleanLine(bit.replace("(","").replace(")",""))}
						if choiceSection:
							choiceSectionParts["CHOICE"][0].append(outx)
						else:
							out.append(outx)
					else:
						bit = cleanLine(bit)
						if len(bit)>0:
							outx = {charName:bit}
							if not charName in parameters["ignoreCharacters"]:
								if choiceSection:
									choiceSectionParts["CHOICE"][0].append(outx)							
								else:
									out.append(outx)
				else:
					if bit.name in ["b","i"]:
						charName = bit.getText().replace(":","").strip()
						charName = charName.title()

			if choiceSection:
				if len(choiceSectionParts["CHOICE"])>1:
					out.append(choiceSectionParts)
				else:
					# Just one "option"
					out += choiceSectionParts["CHOICE"][0]
				
				
		if child.name == "dl":
			currentOptionsCharName = child.find("dt").getText()
		
		if child.name == "ul":
			#currentOptionsCharName = optionsCharName
			choices = choiceParser(child)
			# Add choices to main object
			out.append(choices)
			
		if child.name == "h4" or child.name == "h3" or child.name == "h2":
			out.append({"LOCATION": child.getText().replace("[","").replace("]","")})
	

				
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)