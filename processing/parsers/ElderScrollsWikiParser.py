from bs4 import BeautifulSoup
import json, re

def cleanLine(txt):
	txt = txt.replace('"',"")
	txt = txt.replace('\n'," ")
	txt = txt.replace("Nerevarine (Player name)","")
	txt = re.sub("\(.+?\)"," ",txt)
	txt = re.sub(" +"," ",txt)
	txt = txt.strip()
	txt = txt.replace("[PC Name]","Indoril")
	txt = re.sub("\[(.+?)\]", "(\\1)",txt)
	return(txt)


def parseDialogue(child, charName):
	out = []
	if child.name=="p":
		elements = [x for x in child if str(type(x))=="<class 'bs4.element.Tag'>"]
		if len(elements)>1:
			for bit in elements:
				bitDialogue = parseDialogue(bit,charName)
				out += bitDialogue
		else:
			dlg = cleanLine(child.get_text())
			if len(dlg)>0:
				out.append({charName:dlg})
	elif child.name == "span" and "caption" in child.get("class"):
		bits = [x for x in child if x.name in ['b','span']]
		if len(bits)==2:
			if list(child)[0].name == "b" and list(child)[1].name=="span":
				out.append({"PC": list(child)[0].get_text(), "_State":list(child)[1].get_text()})
		elif list(child)[0].name == "i":
			dialx = cleanLine(list(child)[0].get_text())
			if len(dialx)>1:
				out.append({charName: dialx})
	elif child.name == "b":
		PCPrompt = cleanLine(child.get_text())
		if re.match("^[a-z]",PCPrompt):
			# text is a general prompt rather than dialogue
			PCPrompt = "("+ PCPrompt + ")"
		out.append({"PC":PCPrompt})
	elif child.name == "i":
		dialx = cleanLine(child.get_text())
		if len(dialx)>1:
			out.append({charName:dialx})
	elif child.name == "dl":
		subDialogue = []
		for dd in child.children:
			if dd.name == "dd":
				subParts = []
				for bit in dd.children:
					# TODO: fix this
					bitOut = parseDialogue(bit,charName)
					if len(bitOut)>0:
						subParts += bitOut
				subDialogue.append(subParts)
		out.append({"CHOICE":subDialogue})
		#if len(subDialogue)>1:
		#	out.append({"CHOICE":subDialogue})
		#elif len(subDialogue)==1:
		#	out += subDialogue


	return(out)
	
def postProcessing(out):
	# Make gender dictionary
	genderDict = {}
	for line in out:
		if "GENDER" in line:
			charName, gender = line["GENDER"]
			try:
				genderDict[gender].append(charName)
			except:
				genderDict[gender] = [charName]

	# remove gender items
	out[:] = [x for x in out if not "GENDER" in x]
	
	o = open("../data/ElderScrolls/Morrowind/autoGender.json",'w')
	o.write(json.dumps(genderDict))
	o.close()
	
	# Unpack unnecessary choices
	def unpack(x):
		charName = [z for z in x if not z.startswith("_")][0]
		if charName == "CHOICE":
			if len(x[charName])==1:
				if len(x[charName][0])==1:
					charName2 = [z for z in x[charName][0][0] if not z.startswith("_")][0]
					if charName2 == "CHOICE":
						return(unpack(x[charName][0][0]))
		return([x])
	
	out2 = []
	for line in out:
		out2 += unpack(line)
	return(out2)
	

def parseFile(fileName,parameters={},asJSON=False):

	o = open(fileName)
	d = o.read()
	o.close()
	
	d = re.sub(" oyu "," you ",d)
	
	out = []
	if len(d)>4:
		script = BeautifulSoup(d, 'html.parser')
	
		dialogue = script.find_all("div",{"class":["diabox","diabox-half"]})
		genderDiv = script.find("div",{"data-source":"gender"})
		charName = script.find_all("h1",{"class":"page-header__title"})[0].get_text().strip()
		
		for dial in dialogue:
			for child in dial:
				out += parseDialogue(child,charName)
		#print(dska)
		if genderDiv:
			gender = genderDiv.get_text().replace("Gender","").strip()
			out.append({"GENDER":(charName,gender)})
		
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)
			