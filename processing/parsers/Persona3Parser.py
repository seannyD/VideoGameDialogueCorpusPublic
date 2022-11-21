from bs4 import BeautifulSoup
import json, re, time, os
import xlsxwriter
from io import BytesIO
from urllib.request import urlopen


def cleanLine(txt):
	# don't include player input options
	txt = txt.strip()
	txt = txt.replace("..."," ... ")
	txt = txt.replace("…", " ... ")
	txt = txt.replace("“",'"')
	txt = txt.replace("”",'"')
	# e.g. ["chuckle","sigh","gasp","snrk","yip"]:
	txt = re.sub("\*([A-Za-z]+) ?\*","(\\1)",txt)
	txt = txt.replace('*cough cough*',"(cough cough)")
	txt = txt.replace('*munch munch*',"(munch munch)")
	txt = txt.strip()
	txt = re.sub(" +"," ",txt)
	return(txt)
	
	
def cleanName(name):
	name = name.replace("_"," ")
	return(name)


def parseFile(fileName,parameters={},asJSON=False):


	def getText2(txt):
		if isinstance(txt,str):
			return(txt)
		else:
			return(txt.getText())

	o = open(fileName)
	d = o.read()
	o.close()
	
	baseURL = "https://lparchive.org/Persona-3/"
	updateURL = d[:d.index("\n")]
	d = d[d.index("\n")+1:]
	
	#d = d.replace("<i>","*").replace("</i>","*")
	
	r1 = """<i>Senior: I don't even know who this Aragaki guy was...I heard he never came to school. ...Prolly just some punk. Anyway, I gotta get home...I have to study for my mock-exam. ...Hey, you guys know who Aragaki is? Wait, you're not seniors, so how would you know? Anyway, can you believe this? Scary, huh?</i><br/>"""
	
	r2 = """
<i>Senior (Front): I don't even know who this Aragaki guy was ...</i><br/><br/>
<i>Senior (Side): I heard he never came to school. ... Prolly just some punk. Anyway, I gotta get home ... I have to study for my mock-exam. ...</i><br/><br/>
<i>Senior (Front): Hey, you guys know who Aragaki is? Wait, you're not seniors, so how would you know? Anyway, can you believe this? Scary, huh?</i><br/><br/>"""
	
	d = d.replace(r1,r2)
	
	soup = BeautifulSoup(d,'html.parser')
	script = soup.find("div")
	
	# Divide into lines
	lines = []
	currentLineParts = []
	for child in script.children:
		if child.name=="br":
			if len(currentLineParts)>0:
				lines.append(currentLineParts)
				currentLineParts = []
		else:
			if len(str(child).strip()) >0:
				currentLineParts.append(child)
	
	# Parse lines
	out = []
	for line in lines:
		if isinstance(line[0], str):
			txt = "".join([getText2(x) for x in line]).strip()
			if len(txt)>0:
				out.append({"ACTION":txt})
		elif line[0].name=="i":
			txt = "".join([x.getText() for x in line])
			parts = txt.split("\n")
			for part in parts:
				if part.count(":")>0:
					charName = part[:part.index(":")].strip()
					if charName.startswith("Coming up"):
						out.append({"ACTION":part})
					else:
						dialogue = cleanLine(part[part.index(":")+1:])
						if len(dialogue)>0:
							out.append({charName: dialogue})
		elif line[0].name == "img":
				# single image
				url = baseURL+updateURL+line[0]["src"]
				out.append({"ACTION":url})
		else:
			txt = "".join([x.getText() for x in line]).strip()
			if len(txt)>0:
				out.append({"ACTION":txt})

				
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)
	
	
