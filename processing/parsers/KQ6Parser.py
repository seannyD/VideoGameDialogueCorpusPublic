from bs4 import BeautifulSoup
import json
import re


def cleanText(dialogue):
	dialogue = dialogue.strip()
	dialogue = dialogue.replace("\n", " ")
	dialogue = dialogue.replace("..."," ... ")
	dialogue = dialogue.replace("--"," -- ")
	dialogue = dialogue.replace("::marker","")
	dialogue = re.sub('^ *"',"",dialogue)
	dialogue = re.sub('" *$',"",dialogue)
	# remove text within brackets
	dialogue = re.sub("\(.+?\)","",dialogue).strip()
	dialogue = re.sub("<.+?>","",dialogue).strip()
	dialogue = re.sub(' +'," ",dialogue)
	return(dialogue)
	
	
def recogniseCharacter(characterNum, dataParts, location, parameters):
	if "characterCues" in parameters:
		cc = parameters["characterCues"]
		if characterNum in cc:
			cid = location + " " + " ".join(dataParts[:3])
			if cid in cc[characterNum]:
				return(cc[characterNum][cid])
	return(characterNum) 
	
	
def parseByCharacter(html):

	characterTags = ["h2","h3"]
	out = []	
	characterName = "Graham"
	for bit in list(html.children):
		if bit.name in characterTags:
			characterName = bit.find_all("span",{"class":"mw-headline"})
			if len(characterName)>0:
				characterName = characterName[0].getText().strip()
		else:
			if bit.name=="p":
				dialogue = bit.getText()
				dialogue = dialogue.replace(";",":")
				dialogue = dialogue.replace("\n","")
				if dialogue.count(":")>0:
					dialogue = dialogue.split(":")[1]
				dialogue = cleanText(dialogue)
				if len(dialogue)>0:
					out.append({characterName:dialogue})
			if bit.name=="ul":
				lines = bit.find_all("li")
				for l in lines:
					dialogue = l.text
					dialogue = cleanText(dialogue)
					if len(dialogue)>0:
						out.append({characterName:dialogue})
	return(out)
	
def parseByNumber(html, parameters, actionNumbers=["97"]):
	
	for br in html.find_all("br"):
		br.replace_with(" ")
	
	out = []
	seenKeys = []
	lastScene = ""
	location = ""
	
	for bit in list(html.children):
	
		if bit.name in ['h2','h3']:
			if len(bit)>0:
				location = bit.find("span").get_text().strip()
	
		if bit.name == "p":
			tx = bit.getText().strip()
			if len(tx)>0:
#				0 0 7 1 2 "Ooooh! I can't believe I ate BUGS! I'll never do THAT again!" 
				parts = re.split('([0-9]{1,2} [0-9]{1,2} [0-9]{1,2} [0-9]{1,2} [0-9]{1,3})',tx.strip())
				if parts[0]=="":
					parts = parts[1:]
				contentBits = [parts[i] for i in range(len(parts)) if i % 2 == 1]
				dataBits = [parts[i] for i in range(len(parts)) if i % 2 == 0]

				for dialogue,data in zip(contentBits,dataBits):
					dataKey = location + ":" + data.strip()
					dataParts = data.strip().split(' ')
					if len(dataParts)==5:
						characterNum = dataParts[4]
						#dialogue = line[line.index('"'):]
						if len(dialogue)>0 and not dataKey in seenKeys:
							seenKeys.append(dataKey)
							scene = str(dataParts[0]) + "_" + str(dataParts[1])+"_"+str(dataParts[2])
							if scene != lastScene and lastScene!="":
								if len(out)>0 and out[-1]!={"ACTION":"---"}:
									out.append({"ACTION":"---"})
							lastScene = scene
							
							
							if characterNum in actionNumbers:
								toAdd = {"ACTION": dialogue.strip()}
								if not toAdd in out:
									out.append(toAdd)
							else:
								cleanDialogue = cleanText(dialogue)
								if len(cleanDialogue)>0 and cleanDialogue.count("!!!")==0:
									characterName = recogniseCharacter(characterNum, dataParts, location, parameters)
									toAdd = {characterName:cleanDialogue}
									if not toAdd in out:
										out.append(toAdd)
	return(out)
						


def parseFile(fileName,parameters={},asJSON=False):
	
	o = open(fileName)
	d = o.read()
	o.close()
	
	part1 = d[d.index(parameters["startTextPt1"]):d.index(parameters["startTextPt2"])]
	part2 = d[d.index(parameters["startTextPt2"]):d.index(parameters["endText"])]
	
			
	html1 = BeautifulSoup(part1, 'html.parser')
	out = parseByNumber(html1,parameters)
	
	# Manually fix one error in the script
	out2 = []
	for line in out:
		if "Jowels" in line and line["Jowels"]=="Right, Jowels.":
			out2.append({"Mite":line["Jowels"]})				
		else:
			out2.append(line)
	
	# Part 2 is just repeated from above
	#html2 = BeautifulSoup(part2, 'html.parser')
	#out += parseByCharacter(html2)	
	
		
	
	if asJSON:
		return(json.dumps({"text":out2}, indent = 4))
	return(out2)
