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
		txt = txt.replace('“','').replace('”','')
		txt = txt.replace('’',"'")
		txt = txt.replace('—','-')
		txt = txt.strip()
		txt = txt.replace("[sic]","")
		txt = txt.replace("...","... ")
		txt = re.sub(" +"," ",txt)
		#txt = re.sub('^"'," ",txt)
		#txt = re.sub('"$'," ",txt)
		txt = txt.replace("“",'"')
		txt = txt.replace("”",'"')
		txt = txt.strip()
		return(txt)
	
	def cleanAction(txt):
		txt = txt.strip()
		txt = txt.replace("\n"," ")
		txt = txt.replace("(","").replace(")","")
		#txt = re.sub("^\(","",txt)
		#txt = re.sub("\)$","",txt)
		txt = txt.replace("...","... ")
		txt = re.sub(" +"," ",txt)
		return(txt.strip())
		
	def cleanLocation(txt):
		txt = txt.replace("-"," ")
		txt = re.sub(" +"," ",txt)
		return(txt.strip())

	o = open(fileName)
	html = o.read()
	o.close()
	
	soup = BeautifulSoup(html, 'html5lib')
	
	faqspans = soup.find("div",{"id":"faqtext"})
	d = "\n\n".join([x.getText() for x in faqspans])
	
	#d = soup.find("pre",{"id":"faqspan-1"}).get_text()
	#d += "\n\n" + soup.find("pre",{"id":"faqspan-2"}).get_text() 
	#d += "\n\n" + soup.find("pre",{"id":"faqspan-3"}).get_text() 
	
	startAt = d.index("-------------------------------------")
	d = d[startAt:d.index("Please check out my other Kingdom Hearts scripts",startAt)]
	
	#d = d.replace("This if a fight","This is a fight")
	#d = re.sub("([A-Za-z])\.\.([a-z])","\\1... \\2",d)
	
	# Split into lines
	d = re.sub("\n\s+\n","\n\n",d)
	lines = [line for line in d.split("\n\n") if len(line.strip())>0]

	
	# Recognise lines
	out = []
	for line in lines:
		if line.count(":")>0 and line.index(":")<35:
			charName,dialogue = line.split(":",1)
			dialogue = cleanDialogue(dialogue)
			if len(dialogue)>0:
				cue = ""
				if charName.count("(")>0:
					charName,cue = charName.split("(")
					#dialogue = "("+cue.strip() + " " + dialogue
				charName = cleanName(charName)
				outbit = {charName:dialogue}
				if len(cue)>0:
					outbit["_CUE"] = cue.strip().replace(")","")
				out.append({charName:dialogue})
		elif line.strip().startswith("("):
			out.append({"ACTION":cleanAction(line)})
		elif line.strip().startswith('---'):
			out.append({"LOCATION":cleanLocation(line)})
		else:
			actionLine = cleanAction(line)
			if len(actionLine)>0:
				out.append({"ACTION":actionLine})
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)