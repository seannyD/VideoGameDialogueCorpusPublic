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

	#d = d[d.index('<a name="_6514z9385er8"></a>'):]
	
	html = BeautifulSoup(d, 'html.parser')
	html = html.find("div")

	out = []
	
	charName = ""
	inOptions = False
	afterOptions = False
	choices = []
	pathTaken = []
	
	startedParse = False
	
	for part in html.children:	
		if part.name == "p":
			t = cleanText(part.get_text().replace("\n", " ").strip())
			if t.startswith("["):
				startedParse = True
			if startedParse:
				if len(t)<2:
					if inOptions:
						choices.append(pathTaken)
						out.append({"CHOICE":choices})
						choices = []
						afterOptions = True
						inOptions = False
				elif "a" in [x.name for x in part.children]:
					pass
				elif inOptions and t.count("-")>0:
					type = t[:t.index("-")].strip()
					cue = t[t.index("-")+1:].strip()
					op = [{"ACTION":cue}]
					if len(type)>0:
						op[0]["_Type"] = type
					if "b" in [x.name for x in part.children]:
						# chosen option
						pathTaken = op
						pathTaken[0]["_ChosenPath"]=True
					else:
						choices.append(op)
			
				elif t.startswith("["):
					afterOptions = False
					out.append({"ACTION":t.replace("[","").replace("]","")})
				else:
					nameX = re.findall("^([A-Za-z\\- 0-9\\(\\)’'\\.]+)[:;]",t)
					if len(nameX)>0 and t.count("options")==0:
						if inOptions:
							choices.append(pathTaken)
							out.append({"CHOICE":choices})
							choices = []
							afterOptions = True
							inOptions = False
						
						charName = nameX[0]
						for repl in ["(COMM)","(on comm)","(voice-over)"]:
							charName = charName.replace(repl,"").strip()
					elif re.match(parameters["mainCharName"] + " .+?options:",t):
						#RYDER - Investigate dialogues options:
						inOptions = True
					else:
						dialogue = t.strip()
						if len(dialogue)>0:
							if afterOptions:
								out[-1]["CHOICE"][-1].append({charName:dialogue})
								afterOptions = False
							else:
								out.append({charName:dialogue})
	
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)


