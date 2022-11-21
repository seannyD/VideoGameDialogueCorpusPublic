from bs4 import BeautifulSoup
import json, re


def cleanLine(txt):
	if txt.strip().startswith(">"):
		return("")
	txt = re.sub("^:","",txt)
	# don't include player input options
	txt = txt.replace("\n"," ")
	txt = txt.strip()
	rep = [("&quot;",'"'),("&amp;","&")]
	for r1,r2 in rep:
		txt = txt.replace(r1,r2)
	
	# Remove lines that start with parentheses and have nothing else
	txt = txt.replace("...","... ")
	txt = txt.replace("--", " - ")
	txt = re.sub(" +"," ",txt)
	return(txt)
	
def cleanName(txt):
	txt = re.sub('\(.+?\)',"",txt).strip()
	if txt.count("(")>0:
		txt = txt[:txt.index("(")]
	#txt = txt.replace("Õ","'").replace("Ô","'")
	return(txt)
	
def lineParser(line,param):

	if line.startswith("There seems to be destruction everywhere"):
		return({"ACTION":cleanLine(line)})

	if len(line.strip())==0:
		return(None)
	if line.strip().startswith(param["actionCue"]):
		# action
		cline = cleanLine(line.replace("(","").replace(")",""))
		cline = cline.replace("[","").replace("]","")
		return({"ACTION":cline})
	elif line.startswith('&quot;') or line.startswith('"'):
		return({"ACTION":cleanLine(line)})
	elif line.count(":")>0:
		charName = cleanName(line[:line.index(":")].strip())
		dialogue = cleanLine(line[line.index(":")+1:].strip())
		return({charName:dialogue})	
	return(None)

def parseFile(fileName,parameters={},asJSON=False):


	o = open(fileName)
	d = o.read()
	o.close()
	
	d = d.replace("&amp;","&")
	
	
	d = d[d.index(parameters["scriptStartCue"]):d.index(parameters["scriptEndCue"])]
	open("../data/KingdomHearts/KingdomHearts3D/raw/tmp.txt",'w').write(d)
	out = []

	children = d.split("\n\n")
	for child in children:
		#section = ""

		#if child.name=="h2":
		#	section = child.find("span", {"class":"mw-headline"}).getText()
		#	out.append({"LOCATION": section.strip()})
		
		line = child.replace("\n"," ")
		line = re.sub(" +"," ",line)
		
		outPart = lineParser(line,parameters)
		if not outPart is None:
			out.append(outPart)
			
				
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)