# TODO: need to get around block on scraper

from bs4 import BeautifulSoup
import json,re


def cleanText(t):
	t = t.replace("’","'").replace("“",'"').replace("”",'"').replace("…", " ... ")
	return(t)


def parseFile(fileName,parameters={},asJSON=False):
	
	o = open(fileName)
	d = o.read()
	o.close()
	
	d = d[:d.index('<span class="c9">Messages</span>')]

	#d = d[d.index('<a name="_6514z9385er8"></a>'):]
	
	html = BeautifulSoup(d, 'html.parser')
	html = html.find("div",{"class":"c31"})

	out = []
	
	charName = ""
	inOptions = False
	afterOptions = False
	choices = []
	pathTaken = []
	
	startedParse = False
	
	inBarks = False
	
	for part in html.children:
		if part.name=="h1":
			startedParse=True
			inBarks = False
		if part.name=="h5":
			inBarks = False
		if startedParse:
			if part.name == "h5" and part.get_text().count("letters")>0:
				startedParse=False
			elif part.name == "p":
				span = part.find("span")
				for child in span.children:
					if not child.name=="br":
						if child.strip().startswith("-") and inBarks:
							dialogue = child.strip()[1:].strip()
							out.append({charName:dialogue})
							out.append({"ACTION":"---"})
						elif child.count(":")>0:
							charName = child[:child.index(":")].strip()
							charName = charName.replace("*","").replace(">","").replace("-","").strip()
							if child.endswith(":"):
								inBarks=True
							else:
								dialogue = child[child.index(":")+1:].strip()
								if len(charName)<27:
									out.append({charName:dialogue})
				if len(list(span.children))>1:
					out.append({"ACTION":"---"})
	
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)











