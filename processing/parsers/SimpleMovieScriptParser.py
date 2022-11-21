from bs4 import BeautifulSoup
import json, re


def cleanLine(txt):
	if txt.strip().startswith(">"):
		return("")
	txt = re.sub("^:","",txt)
	# don't include player input options
	txt = txt.replace("\n"," ")
	txt = txt.strip()
	# Remove lines that start with parentheses and have nothing else
	txt = txt.replace("...","... ")
	txt = re.sub(" +"," ",txt)
	return(txt)
	
def cleanName(txt):
	txt = re.sub('\(.+?\)',"",txt).strip()
	if txt.count("(")>0:
		txt = txt[:txt.index("(")]
	return(txt)
	
def lineParser(line,param):

	if line.startswith("There seems to be destruction everywhere"):
		return({"ACTION":cleanLine(line)})

	if len(line.strip())==0:
		return(None)
	if line.strip().startswith(param["actionCue"]):
		# action
		return({"ACTION":cleanLine(line.replace("(","").replace(")","")).replace("[","").replace("]","")})
	elif line.startswith('“') or line.startswith('"'):
		return({"ACTION":cleanLine(line)})
	elif line.count(":")>0:
		charName = cleanName(line[:line.index(":")].strip())
		dialogue = cleanLine(line[line.index(":")+1:].strip())
		return({charName:dialogue})	
	return(None)

def parseFile(fileName,parameters={},asJSON=False):

	html_= open(fileName,'r', encoding = 'utf8')
	html_ = html_.read()
	# manual edits for KH3
	html_ = html_.replace("Hiro: And the crime fighting team of Big Hero 6! Together, we're unstoppable.\n\nEveryone: Yeah!", "Hiro: And the crime fighting team of Big Hero 6! Together, we're unstoppable.\n\nDonald & Goofy & Fred: Yeah!")
	html_ = html_.replace("Mickey: Right!\n\nEveryone: Yeah!", "Mickey: Right!\n\nDonald & Goofy & Roxas & Riku & Aqua & Kairi: Yeah!")
	
	soup = BeautifulSoup( html_, "html.parser")
	text = soup.find("div", {"id": parameters["textDivId"]})
	text = "\n\n".join([x.get_text() for x in text.children])
	text = text[text.index(parameters["startText"]):text.index(parameters["endText"])]
	lines = text.split("\n\n")					
	
	out =[]
	for line in lines:
		outPart = lineParser(line,parameters)
		if outPart is not None:
			out.append(outPart)
					
				
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)