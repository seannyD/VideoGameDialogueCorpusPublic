from bs4 import BeautifulSoup
import json
import re


def cleanText(dialogue):
	dialogue = dialogue.replace("::marker","")
	dialogue = re.sub('^ *"',"",dialogue)
	dialogue = re.sub('" *$',"",dialogue)
	# remove text within brackets
	dialogue = re.sub("\(.+?\)","",dialogue).strip()
	dialogue = re.sub("<.+?>","",dialogue).strip()
	return(dialogue)

def parseFile(fileName,parameters={},asJSON=False):
	
	skipLines = ["Mostly the same lines","The long drawn out moan","There are a few new","Note: As it would"]
	
	o = open(fileName)
	d = o.read()
	o.close()
	
	if "startText" in parameters:
		d = d[d.index(parameters["startText"]):]
	if "endText" in parameters:
		d = d[:d.index(parameters["endText"])]
		
	characterTags = ["h2","h3"]
	if "characterTags" in parameters:
		characterTags = parameters["characterTags"]
	
	html = BeautifulSoup(d, 'html.parser')
	
	out = []
	
	characterName = "Graham"
	for bit in list(html.children):
		if bit.name in characterTags:
			characterName = bit.find_all("span",{"class":"mw-headline"})
			if len(characterName)>0:
				characterName = characterName[0].getText().strip()
		else:
			if bit.name=="p":
				dialogue = bit.getText()
				if not any([dialogue.startswith(x) for x in skipLines]):
					dialogue = dialogue.replace(";",":")
					dialogue = dialogue.replace("\n","")
					if dialogue.count(":")>0:
						dialogue = dialogue.split(":")[1]
					dialogue = cleanText(dialogue)
					if len(dialogue)>0:
						out.append({characterName:dialogue})
			if bit.name=="ul":
				lines = bit.find_all("li")
				for l in lines:
					dialogue = l.text
					dialogue = cleanText(dialogue)
					if len(dialogue)>0:
						out.append({characterName:dialogue})
		
	
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)