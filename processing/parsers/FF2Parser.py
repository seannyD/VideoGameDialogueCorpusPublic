import json,re
from bs4 import BeautifulSoup, NavigableString, Tag
def parseFile(fileName,parameters={},asJSON=False):

	def cleanName(charName):
		charName = charName.replace("*","").strip()
		return(charName)
		
	def cleanDialogue(txt):
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
		txt = re.sub("^\(","",txt)
		txt = re.sub("\)$","",txt)
		return(txt.strip())

	hardcodedChoices = [
		# Choice 1
		[{"CHOICE":[
			[{"ACTION": "Player chooses 'Yes'"}, {"Man at Entrance":"Deal! Okay, I'll see you at my ship docked outside this town."}],
			[{"ACTION": "Player chooses 'No'"}]
		]}],
		# Choice 2
		[{"CHOICE": [
		 	[{"ACTION": "Player chooses 'Yes'"},
		 	 {"Cid's buddy": "Where to?"},
		 	 {"CHOICE": [
				[{"ACTION": "Player chooses 'Bafsk 100'"}],
				[{"ACTION": "Player chooses 'Salamand 200'"}],
				[{"ACTION": "Player chooses 'Semit Falls 300'"}],
				[{"ACTION": "Player chooses 'Kas'ion 400'"}]
		 	 ]},
		 	 {"Cid's buddy": "Alright, we got a deal. Now we'll prepare for takeoff, so come to the airfield outside this town."}
		 	],
		 	[{"ACTION": "Player chooses 'No'"}]
		 ]}
		 ],
		# choice 3
		[{"CHOICE":[
			[{"ACTION": "Player chooses 'Yes'"}, {"Man by Pub":"Deal! Okay, I'll see you at my ship docked outside this town."}],
			[{"ACTION": "Player chooses 'No'"}]
		]}],
	]

	o = open(fileName)
	html = o.read()
	o.close()
	
	html = html.replace("appear: Scott","appear- Scott")
	html = html.replace("remain clear and true:","remain clear and true -")
	html = html.replace("The Palamecian king then boasted:", "The Palamecian king then boasted- ")
	
	# hard replace some choices
	html = html.replace("""- Yes
No

&quot;Deal! Okay, I'll see you at my ship docked outside this town.&quot;
""", "HARDCODEDCHOICES_0\n")
	html = html.replace("""you-know-what.&quot;

Yes
- No""", "you-know-what.&quot;\n\nHARDCODEDCHOICES_1\n")

	html = html.replace("""you-know-what.&quot;

- Yes
No

Where to?

Bafsk 100
Salamand 200
Semit Falls 300
- Kas'ion 400

&quot;Alright, we got a deal. Now we'll prepare for takeoff, so come
to the airfield outside this town.&quot;""", "you-know-what.&quot;\n\nHARDCODEDCHOICES_1\n")


	html = html.replace("""to Paloom!&quot;

Yes
- No""", "to Paloom!&quot;\n\nHARDCODEDCHOICES_2\n")


	#html = html.replace("you-know-what.&quot;\nYes\n- No", "you-know-what.&quot;\nHARDCODEDCHOICES_1\n")
	#html = html.replace("you-know-what.&quot;\n- Yes\nNo", "you-know-what.&quot;\nHARDCODEDCHOICES_1\n")



	
	
	soup = BeautifulSoup(html, 'html5lib')
	
	d = soup.find("pre",{"id":"faqspan-1"}).get_text()
	d += "\n\n" + soup.find("pre",{"id":"faqspan-2"}).get_text() 

	d = d[d.index("In a distant land"):d.index("(Credits roll.)")]
	
	# Split into lines
	lines = []
	tmp = ""
	for line in d.split("\n"):
		newLine = False
		if line.count(":")>0 and line.index(":")<30 and (not line.strip().startswith("appear")):
			newLine = True
		if line.startswith("(") or line.startswith("-"):
			newLine = True
		if len(line.strip())==0:
			newLine = True
		if newLine:
			if len(tmp)>0:
				lines.append(tmp)
			tmp = line
		else:
			tmp += " " + line
	
	# Recognise lines
	out = []
	inChoice = False
	keyword = ""
	choiceText = None
	for line in lines:
		if line.count(":")>0:
			charName,dialogue = line.split(":",1)
			dialogue = cleanDialogue(dialogue)
			dialogue = dialogue.split('" "')
			# TODO: split lines by quotes
			if inChoice:
				inChoice = False
				choiceX = []
				if not choiceText is None:
					choiceX = [choiceText]
				out.append({"CHOICE":[[],choiceX+[{cleanName(charName):dx,"_Keyword":keyword} for dx in dialogue]]})
			else:
				out += [{cleanName(charName):dx} for dx in dialogue]
		elif line.count("HARDCODEDCHOICES")>0:
			cnum = line.split("_")[1].strip()
			out += hardcodedChoices[int(cnum)]
		elif line.strip().startswith("(") or line.strip().startswith('"'):
			out.append({"ACTION":cleanAction(line)})
		elif line.startswith("-"):
			out.append({"LOCATION":cleanAction(line)})
		elif line.strip().startswith("Ask -"):
			inChoice = True
			qchar = line.split("-")[-2].strip()
			keyword = line.split("-")[-1].strip()
			choiceText = {"ACTION": "Ask " + qchar + " about " + keyword}
		else:
			out.append({"SYSTEM":cleanAction(line)})
			inChoice = False
	

	
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)