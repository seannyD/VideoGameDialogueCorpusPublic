from bs4 import BeautifulSoup
import json, re


def cleanLine(txt):
	if txt.strip().startswith(">"):
		return("")
	txt = re.sub("^:","",txt)
	# don't include player input options
	txt = txt.replace("\n"," ")
	txt = txt.strip()
	rep = [('’',"'"),("‘","'"),("…","... "),("—","-"),("“",'"'),("”",'"'),("é","é")]
	for r1,r2 in rep:
		txt = txt.replace(r1,r2)
	
	# Remove lines that start with parentheses and have nothing else
	txt = txt.replace("...","... ")
	txt = re.sub(" +"," ",txt)
	return(txt)
	
def cleanName(txt):
	txt = re.sub('\(.+?\)',"",txt).strip()
	if txt.count("(")>0:
		txt = txt[:txt.index("(")]
	txt = txt.replace("’","'").replace("‘","'")
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


	o = open(fileName)
	d = o.read()
	o.close()
	
	
	d = d[d.index(parameters["scriptStartCue"]):d.index(parameters["scriptEndCue"])]

	
	script = BeautifulSoup(d, 'html.parser')
	
	out = []

	for child in list(script.children):
		section = ""

		if child.name=="h2":
			section = child.find("span", {"class":"mw-headline"}).getText()
			out.append({"LOCATION": section.strip()})
	
		if child.name=="p":
			line = child.get_text()
			outPart = lineParser(line,parameters)
			if outPart is not None:
				out.append(outPart)
		if child.name=="dl":
			dds = child.find_all("dd")
			for dd in dds:
				line = dd.get_text()
				outPart = lineParser(line,parameters)
				if outPart is not None:
					out.append(outPart)
				
		if child.name=="table":
			trs = child.find_all("tr")
			for tr in trs:
				td = tr.find_all("td")
				th = tr.find_all("th")
				if len(th)>0 and len(td)>0:
					charName = cleanName(th[0].get_text())
					if(charName!="Speaker"):
						dialogueText = td[0].get_text()
						out.append({charName:cleanLine(dialogueText)})
				elif len(td)>0:
					out.append({"ACTION":cleanLine(td[0].get_text())})
					
		if child.name =="ul":
			for li in child.find_all("li"):
				line = li.get_text()
				outPart = lineParser(line,parameters)
				if outPart is not None:
					out.append(outPart)
		if child.name =="li":
			line = li.get_text()
			outPart = lineParser(line,parameters)
			if outPart is not None:
				out.append(outPart)
					
		if child.name=="hr":
			out.append({"ACTION":"----"})
			

		if child.name=="div" and "poem" in child.get("class"):
			for br in child.find_all("br"):
			    br.replace_with("\n")
			t = child.get_text()
			for line in t.split("\n"):
				outPart = lineParser(line,parameters)
				if outPart is not None:
					out.append(outPart)
					
					
				
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)