from bs4 import BeautifulSoup
import json,re

# Intended for FFXIII

def parseFile(fileName,parameters={},asJSON=False):

	o = open(fileName)
	d = o.read()
	o.close()

	# Battle lines
	d1 = d[d.index(parameters["scriptStartCue"]):d.index(parameters["scriptMidCue"])]
	
	battle = BeautifulSoup(d1, 'html.parser')
	
	battleLines = battle.find_all([parameters["lineNode"],"h2"])
	battleLines = [x for x in battleLines if len(x.find_all("li"))==0]
	
	outBattle = []
	charName = "Lightning"
	for line in battleLines:
		if line.name=="h2":
			lx = line.getText()
			if lx.count("-")>0:
				lx = lx[:lx.index("-")].strip()
			lx = lx.replace("[edit]","")
			charName = lx
		elif line.name == "li":
			lx = line.getText()
			lx = lx.replace("[","(").replace("]",")")
			ctx = " ".join(re.findall("\(.+?\)", lx)).strip()
			lx = re.sub("\(.+?\)","",lx)
			lxs = lx.split("/")
			for x in lxs:
				bit = {charName:x.strip()}
				if len(ctx)>0:
					bit["_Context"] = ctx
				outBattle.append(bit)
				outBattle.append({"ACTION": "---"})
	
	# Ordinary dialogue
	d2 = d[d.index(parameters["scriptMidCue"]):d.index(parameters["scriptEndCue"])]

	script = BeautifulSoup(d2, 'html.parser')
	
	out = []

	for line in script.find_all([parameters["lineNode"],"p"]):
		lineText = "".join([x for x in line.children if isinstance(x,str)]).strip()
		lineText = lineText.replace("\n"," ")
		lineText = re.sub(" +"," ",lineText)
		if line.getText().strip().startswith("[") or line.name=="p":
			charName="ACTION"
		else:
			charBit = line.find(parameters["characterNameNode"])
			if charBit:
				charName = charBit.getText().strip()
			else:
				lx = line.getText()

				if lx.count(":")>0:
					charName = lx[:lx.index(":")].strip()
					lineText = lx[lx.index(":")+1:].strip()
		# remove stuff between brackets
		lineTextA = re.sub(r'\([^)]*\)', '', lineText).strip()					
		# remove colon at start of line
		lineTextA = re.sub("^:","",lineTextA).strip()
		if len(lineTextA)>0:
			out.append({charName:lineTextA})
		elif len(lineText)>0:
			out.append({"ACTION":lineText.replace("(","").replace(")","")})

	out.append({"ACTION": "Battle dialogue"})
	out += outBattle
	
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)