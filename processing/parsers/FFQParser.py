# TODO: choices are not being parsed correctly

from bs4 import BeautifulSoup
import json,re

def parseFile(fileName,parameters={"characterClassIdentifier":"ff7", "replaceFixes": []}, asJSON=False):

	def parseHappening(happening):
		actions = happening.find_all('div',recursive=False)
		out = []
		for action in actions:
			outx = parseBit(action)
			if outx:
				out.append(outx)
		return(out)		

	def parseBit(bit):
		cl = bit.get("class")

		if(cl[0]=='action'):
			return(actionParser(bit))
		if('narrative' in cl):
			return(narrativeParser(bit))
		if("event-container" in cl):
			return(eventParser(bit))
		if("choice-set-container" in cl):
			return(choiceParser(bit))
		return(None)

	def actionParser(bit):
		ret = {"ACTION": bit.find_all("span")[0].getText()	}
		return(ret)

	def narrativeParser(bit):
		ret = {"NARRATIVE": bit.find_all("span")[0].getText()	}
		return(ret)
		
	def locationParser(bit):
		ret = {"LOCATION": bit.find_all("span")[0].getText()	}
		return(ret)

	def eventParser(bit):

		firstBit = bit.find("div")
		if "action" in firstBit.get("class"):
			# TODO: what if there are other bits after this?
			return(actionParser(firstBit))
		elif "narrative" in firstBit.get("class"):
			return(narrativeParser(firstBit))
		elif "location" in firstBit.get("class"):
			return(locationParser(firstBit))
	
		cx = bit.find(class_=parameters["characterClassIdentifier"])		
		characterName = cx.find("a").getText()
		tx = "\n".join([x.getText() for x in bit.find_all("p")])
		
		# Sometimes, part of the spoken text is included in the
		# character name section.
		if characterName.count(":")>0:
			newName = characterName[:characterName.index(":")].strip()
			extraText = characterName[characterName.index(":")+1:].strip()
			characterName = newName
			tx = extraText + " " + tx
			tx = re.sub(" +"," ",tx)

		tx = tx.strip()
	
		ret = {characterName: tx}
		return(ret)

	def choiceParser(bit):
		choiceContainers = bit.find_all(class_="choice-show-container",recursive=False)
		out = []
		for choiceContainer in choiceContainers:
			happening = choiceContainer.find(class_="mdl-grid happenings",recursive=False)
			out.append(parseHappening(happening))
		return({"CHOICE":out})
	
	o = open(fileName)
	d = o.read()
	o.close()
	
	if "replaceFixes" in parameters:
		for rep in parameters["replaceFixes"]:
			d = d.replace(rep[0],rep[1])

	soup = BeautifulSoup(d, 'html.parser')
	html = list(soup.children)[2]
	script = html.find('div', class_='happenings')

	out = parseHappening(script)
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)
		