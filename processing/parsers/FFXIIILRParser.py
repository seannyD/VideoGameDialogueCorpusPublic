from bs4 import BeautifulSoup
import json, re


def cleanLine(txt):
	txt = re.sub(" +"," ",txt)
	txt = txt.strip()
	return(txt)
	
def cleanName(txt):
	txt = re.sub('\(.+?\)',"",txt).strip()
	if txt.count("(")>0:
		txt = txt[:txt.index("(")]
	return(txt)
	

	

def parseFile(fileName,parameters={},asJSON=False):

	script = open(fileName,'r', encoding = 'utf8').read()
	out= []
	
	lines = [x for x in script.split("\n\n") if len(x.strip())>0]
	
	vNum = fileName[-5]
	
	firstLine = True
	for line in lines:
		if firstLine:
			out.append({"ACTION": line.strip()})
			firstLine = False
		else:
			line = line.replace("\n"," ")
			line = re.sub(" +"," ",line)
			if line.strip().startswith("---"):
				out.append({"ACTION": "---"})
			elif line.strip().startswith("["):
				out.append({"ACTION": "Timestamp: V"+vNum+" "+line.strip()})
			else:
				charName, dialogue = line.split(":",1)
				out.append({cleanName(charName): cleanLine(dialogue)})
	
				
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)
	
