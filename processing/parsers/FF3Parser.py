import json,re
from bs4 import BeautifulSoup, NavigableString, Tag

def parseFile(fileName,parameters={},asJSON=False):

	def cleanName(charName):
		charName = charName.replace("*","").strip()
		charName = charName.title()
		charName = charName.replace("'S","'s")
		return(charName)
		
	def cleanDialogue(txt):
		txt = txt.replace("\n"," ")
		txt = txt.strip()
		txt = txt.replace("[sic]","")
		txt = re.sub(" +"," ",txt)
		txt = re.sub('^"'," ",txt)
		txt = re.sub('"$'," ",txt)
		txt = txt.replace("“","")
		txt = txt.replace("”","")
		txt = txt.strip()
		return(txt)
	
	def cleanAction(txt):
		txt = txt.strip()
		txt = re.sub("^ENTER","",txt)
		txt = txt.strip()
		txt = re.sub("^\(","",txt)
		txt = re.sub("\)$","",txt)
		return(txt.strip())

	o = open(fileName)
	html = o.read()
	o.close()
	
	soup = BeautifulSoup(html, 'html5lib')
	
	d = soup.find("pre",{"id":"faqspan-1"}).get_text()
	d += "\n\n" + soup.find("pre",{"id":"faqspan-2"}).get_text() 
	d += "\n\n" + soup.find("pre",{"id":"faqspan-3"}).get_text() 

	d = d[d.index("ENTER"):d.index("Cue credits!")]
	
	d = d.replace("(cue Kefka's theme)","\n\n(cue Kefka's theme)\n\n")
	d = d.replace("(To the girl)", "(To the girl)\n\n")
	
	# Split into lines
	d = re.sub("\n\s+\n","\n\n",d)
	lines = [line for line in d.split("\n\n") if len(line.strip())>0]

	
	# Recognise lines
	out = []
	for line in lines:
		if line.count(":")>0 and line.index(":")<15:
			charName,dialogue = line.split(":",1)
			dialogue = cleanDialogue(dialogue)
			if len(dialogue)>0:
				out.append({cleanName(charName):dialogue})
		elif line.startswith("   "):
			out.append({"ACTION":cleanAction(line)})
		elif line.strip().startswith("("):
			out.append({"COMMENT":cleanAction(line)})
		elif line.strip().startswith("ENTER"):
			out.append({"LOCATION":cleanAction(line)})
		elif line.strip().startswith('---'):
			out.append({"LOCATION":"---"})
	
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)