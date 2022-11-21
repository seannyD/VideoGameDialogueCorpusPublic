from bs4 import BeautifulSoup
import json
import re


def parseFile(fileName,parameters={},asJSON=False):

	skipChar = ["int","WHABConvoG09ALT2","C4PackReptileB"]

	def cleanText(dialogue):
		dialogue = dialogue.replace("::marker","")
		dialogue = dialogue.replace("’","'")
		dialogue = re.sub('^ *"',"",dialogue)
		dialogue = re.sub('" *$',"",dialogue)
		# remove text within brackets
		dialogue = re.sub("\(.+?\)","",dialogue).strip()
		dialogue = re.sub("<.+?>","",dialogue).strip()
		# Some dialogue has cues within it
		if dialogue.count(":")>0:
			if dialogue[:dialogue.index(":")] in ["Nesse","Vee","Graham", "Manny","Old Graham","Knights","KNIGHT","WADDLES"]:
				dialogue = dialogue[dialogue.index(":")+1:].strip()
		return(dialogue)
	
	fileNameEnd = fileName[fileName.rindex("/")+1:]
	print(fileNameEnd)
	# Set parameters for individual file
	if fileNameEnd in parameters["optionsForChapters"]:
		parameters = parameters["optionsForChapters"][fileNameEnd]
	
	if not "reForDialogue" in parameters:
		parameters["reForDialogue"] = "Text=\".+?\""
	
	o = open(fileName)
	d = o.read()
	o.close()
	
	d = d.replace('SpokenText=','ST=')
	d = d.replace('\\"',"'")
	d = d.replace('"no"',"'no'")
	
	if "startText" in parameters:
		d = d[d.index(parameters["startText"]):]
	if "endText" in parameters:
		d = d[:d.index(parameters["endText"])]
		

	html = BeautifulSoup(d, 'html.parser')
	out = [{"ACTION":"---- Chapter "+fileNameEnd[5]}]
	
	htmlParts = list(html.children)
	
	# Some lines are split across two p tags
	#  so join them up here
	parts = []
	lastPart = ""
	for bit in htmlParts:
		if bit.name == "p":
			lx = bit.getText().strip()
			if len(lx)>0:
				if lx.endswith("]"):
					# need to add next line to this one
					lastPart = lx
				else:
					parts.append((lastPart + lx).replace("\n","").replace("<br >",""))
					lastPart = ""
		if bit.name == "h3":
			tx = bit.getText().strip()
			if tx.count("VO")==0:
				out.append({"LOCATION":tx})
	
	for lx in parts:
		if len(lx)>15 and lx[0]=="[" and lx.count("_")>0:
			character = "Graham"
			if not ("_Choice_" in lx or "TextAndImagesDisplayToggle" in lx):
				# [VO_BoS3rdYarnRevA_AC SoundNodeWave] Subtitles[0]=(Text="Nooo... the Drozdeck Demon!")
				context = lx[:lx.index("]")]
				character = context.replace(" ","_").split("_")[2]
				if len(character)>3:
					character = context.replace(" ","_").split("_")[1]						
			dialogues = re.findall(parameters["reForDialogue"],lx)
			dialogues = " ".join([x[x.index('"')+1:-1] for x in dialogues])
			
			# clean dialogues
			dialogues = re.sub("\[.+?\]","",dialogues).strip()
			dialogues = re.sub(" +"," ",dialogues).strip()
			
			if len(dialogues)>0 and not character in skipChar:
				out.append({character:dialogues})
	
	
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)
