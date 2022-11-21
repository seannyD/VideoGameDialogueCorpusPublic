from bs4 import BeautifulSoup
import json, re


def cleanLine(txt):
	txt = txt.replace("\n"," ").replace("_"," ").replace("|"," ").replace("/","").replace("[","").replace("]","")
	txt = txt.strip()
	txt = re.sub(" +"," ",txt)
	txt = re.sub("\\-+","-",txt)
	# some 
	
	return(txt)
	
def cleanName(txt):
	txt = re.sub('\(.+?\)',"",txt).strip()
	if txt.count("(")>0:
		txt = txt[:txt.index("(")]
	return(txt)

def getOut(charName,dialogueText):
	dx = re.sub("\\(.+?\\)","",cleanLine(dialogueText)).strip()
	if len(dx)==0:
		return({"ACTION":cleanLine(dialogueText)})
	else:
		dialogueText = cleanLine(dialogueText)
		fullText = ""
		if dialogueText.count("("):
			fullText = dialogueText
			dialogueText = re.sub(r"\(.*?\)", "", dialogueText)
			dialogueText = re.sub(" +"," ",dialogueText)
			return({charName:cleanLine(dialogueText), "_withCue":fullText})
		else:
			return({charName:cleanLine(dialogueText)})


def parseFile(fileName,parameters={},asJSON=False):

	html_= open(fileName,'r', encoding = 'utf8')
	soup = BeautifulSoup( html_, "html.parser")
	text = soup.find("div", {"id": parameters["textDivId"]})
	text = "\n\n".join([x.get_text() for x in text.children])
	text = text[text.index(parameters["startText"]):text.index(parameters["endText"])]
	lines = text.split("\n")
	
	
	out =[]
	charName = ""
	dialogueText = ""
	actionText = ""
	for line in lines:
		if len(line.strip())<2:
			pass
		nameLen = 0
		dialogLen = 0
		if line.count(":")>0:
			nameLen = len(line[:line.index(":")].strip())
			dialogLen = len(line[line.index(":"):].strip())
		if re.match("^[A-Za-z0-9 \\-\\.]+:",line) and (dialogLen>3) and (nameLen>2) and (nameLen < 21):
			
			if len(cleanLine(actionText))>1:
				out.append({"ACTION":cleanLine(actionText)})
				actionText = ""
			if len(dialogueText)>0:
				out.append(getOut(charName,dialogueText))
				dialogueText = ""
		
			if line.strip().startswith("Part") or line.strip().startswith("Last Part"):
				out.append({"ACTION":cleanLine(line)})
			else:
				charName = line[:line.index(":")].strip()
				dialogueText = line[line.index(":")+1:].strip()
		elif line.startswith("  ") and not line.count("___")>0 and not line.count("|")>0:
			dialogueText += " " + line.strip()
		else:
			# Line of action description
			if len(dialogueText)>0:
				out.append(getOut(charName,dialogueText))
				dialogueText = ""
			actionText += " " + line.strip()
				
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)