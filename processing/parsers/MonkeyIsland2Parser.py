from bs4 import BeautifulSoup
import json, re


def parseFile(fileName,parameters={},asJSON=False):

	html_= open(fileName,'r', encoding = 'utf8')
	soup = BeautifulSoup( html_, "html.parser")
	text = soup.find("div", {"id": parameters["textDivId"]})
	text = "\n\n".join([x.get_text() for x in text.children])
	
	text = text[text.index(parameters["startText"]):]
	
	text = text.replace("Yo can't win you don't play.","You can't win if you don't play.")
	
	text = text.replace("*sigh*", "(sigh)").replace("***rap tap tap**","(rap tap tap)")
	
	out = []
	for line in [x for x in text.split("\n\n") if len(x.strip())>0 and not x.startswith(">")]:
		line = line.replace("\n"," ")
		line = re.sub(" +"," ",line)
		if line.startswith("["):
			out.append({"ACTION":line[1:-1].strip()})
		else:
			charName = line[:line.index(":")].strip()
			dialogue = line[line.index(":")+1:].strip()
			out.append({charName: dialogue})
				
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)