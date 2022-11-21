from bs4 import BeautifulSoup
import json, re

# TODO
#{"ACTION": "If Serah or Noel are on or near a chocobo, they may get any of the following auto-talks..."},
#{"ACTION": "He's mighty fast. Nice. Oh. He's a grand one."},

# TODO
# "(auto-talk)" for NPCs can indicate multiple separate lines.

# TODO: "If ..." parse to choice?
#		{"ACTION": "If they talk with her again..."},
#		{"Chocolina": "Howdy, time-buddies! Care to help a choco-girl out by spending some gil?"},


def cleanLine(txt):
	if txt.strip().startswith(">"):
		return("")
	txt = re.sub("^:","",txt)
	txt = txt.replace("*"," ")
	# don't include player input options
	txt = txt.replace("\n"," ")
	# Remove lines that start with parentheses and have nothing else
	txt = txt.replace("...","... ")
	txt = txt.replace("[sic]"," ")
	txt = txt.strip()
	if txt.startswith("-"):
		txt = txt[1:].strip()
	# Orthography for "sped up talking": replace dashes with spaces
	# Serah: He-has-this-amazing-body-and-his-face-is-so-handsome-he's-tall-and-broad-and-makes-me-feel-so-safe! 
	if txt.count("-")>6:
		txt = txt.replace("-"," ")
	txt = re.sub(" +"," ",txt)
	txt = txt.strip()
	return(txt)
	
def cleanName(txt):
	txt = re.sub('\(.+?\)',"",txt).strip()
	if txt.count("(")>0:
		txt = txt[:txt.index("(")]
	return(txt)

def makeTalkAgainChoices(bits,charName):
	outx = [{charName: cleanLine(bits[0])}]
	choices = []
	# reverse list and embed
	for bit in reversed(bits[1:]):
		if len(choices)>0:
			choices = {"CHOICE":[[{charName:cleanLine(bit), "_TalkAgain":"True"},choices],[]]}
		else:
			choices = {"CHOICE":[[{charName:cleanLine(bit), "_TalkAgain":"True"}],[]]}
	outx.append(choices)
	return(outx)
	

def lineParser(line,param):

	if line.startswith("There seems to be destruction everywhere"):
		return({"ACTION":cleanLine(line)})
	if len(line.strip())==0:
		return(None)
	if line.strip().startswith(param["actionCue"]):
		# action
		return({"ACTION":cleanLine(line.replace("(","").replace(")","")).replace("[","").replace("]","")})
	elif line.startswith("!!!"):
		# Lines at different times:
		#Resident: Kitties just love to crawl inside boxes, don't they?
		#- Looks like you found your kitty-cat! Isn't that great?
		#- Your kitty's all sleek and brushed today!
		#- I think 'Esmerelda' suits your cat much better.
		charName = line[3:line.index(":")].strip()
		line = line[line.index(":")+1:]
		bits = line.split("\n-")
		# First option is usually default and mandatory, not a choice
		#return([{charName: cleanLine(bits[0])},
		#		{"CHOICE":[[{charName:cleanLine(bit), "_TalkAgain":"True"}] for bit in bits[1:]]}])
		talkAgainList = makeTalkAgainChoices(bits,charName)
		return(talkAgainList)
		
	elif line.startswith('“') or line.startswith('"') or line.count(":")==0:
		return({"ACTION":cleanLine(line)})
	elif line.startswith("Live Trigger"):
		return({"ACTION":cleanLine(line.replace("Live Trigger", "Live Trigger: ",1))})
	elif line.count(":")>0:
		charName = cleanName(line[:line.index(":")].strip())
		dialogue = cleanLine(line[line.index(":")+1:].strip())
		return({charName:dialogue})	
	return(None)
	
def decisionParser(dchunk,param):
	parts = [x.strip() for x in dchunk.split("\n") if len(x.strip())>0]
	if len(parts) >1:
		decisions = [[{"ACTION": "Player chooses "+x}] for x in parts]
		# The choices can include embedded choices, 
		topLevelDecisions = []
		seenButtons = []
		for dx in decisions:
			button  = dx[0]["ACTION"].split(" ")[2]
			if not button in seenButtons:
				topLevelDecisions.append(dx)
				seenButtons.append(button)
		return(topLevelDecisions)
		
def yesNoParser(line):
	yesNoPrompt = line[:line.index("Yes\n")].replace("\n-","").strip()
	yesNoPromptLine = {"SYSTEM": cleanLine(yesNoPrompt)}
	selectedOption = 0
	if "- Yes" in line:
		selectedOption = 1
	return yesNoPrompt,yesNoPromptLine,selectedOption
	
def splitNoOptions(opts):
	# Some "no" choices have multiple responses
	if any(["--" in opt for opt in opts]):
		optOut = [{"ACTION": "Player chooses 'No'"},{"CHOICE":[[]]}]
		for opt in opts:
			if opt == {"ACTION": "Player chooses 'No'"}:
				pass
			elif "--" in opt:
				optOut[1]["CHOICE"].append([])
			else:
				opt["_TalkAgain"] = "True"
				optOut[1]["CHOICE"][-1].append(opt)
		return(optOut)
	else:
		return(opts)
# 
# 	optOut = []
# 	foundAlt = False
# 	for opt in opts:
# 		if "--" in opt:
# 			if not foundAlt:
# 				foundAlt = True
# 				optOut.append({"CHOICE":[[]]})
# 			else:
# 				optOut[-1]["CHOICE"].append([])
# 		else:
# 			if len(optOut)>0 and "CHOICE" in optOut[-1]:
# 				optOut[-1]["CHOICE"][-1].append(opt)
# 			else:
# 				optOut.append(opt)
# 	return(optOut)
	

def parseFile(fileName,parameters={},asJSON=False):

	choiceStoppers = ["Alyssa: I think I'm a bit jealous of you, Serah."]

	html = open(fileName,'r', encoding = 'utf8')
	html = html.read()
	html = html.replace('</pre><pre id="faqspan-3">','</pre><pre id="faqspan-3">\n\n')
	soup = BeautifulSoup( html, "html5lib")
	text = soup.find("div", {"id": parameters["textDivId"]})
	text = "".join([x.get_text() for x in text.children])
	text = text[text.index(parameters["startText"]):text.index(parameters["endText"])]
	
	# Replace lines with just spaces
	text = re.sub("\n[ \t]+\n","\n\n",text)
	
	text = text.replace("Where on Pulse could it be?","Where on Pulse could it be?\n")
	text = text.replace("(A cutscene begins. Serah holds the Eclipse Artefact","DummyAction: A cutscene begins. Serah holds the Eclipse Artefact")
	text = text.replace("Noel: Yes. Yes, it worked!","Noel: Yes. Yes, it worked!\n\n(--)\n\n")
	text = text.replace('\nMyta;','\nMyta:')
	text = text.replace('\nSerah;','\nSerah:')
	text = text.replace("Serah and Noel have come to Augusta Tower","(Serah and Noel have come to Augusta Tower")
	text = text.replace('Mission objective:', 'Mission objective - ')
	text = text.replace("Their mission was simple:", "Their mission was simple - ")
	text = text.replace("It's a message from my future self.","Noel: It's a message from my future self.")
	text = text.replace("Paradox Ending:", "(Paradox Ending:")
	text = text.replace('\nFragment -', "\n(Fragment -")
	text = text.replace('\nFragment Discovered!', "\n(Fragment Discovered!")
	text = text.replace('Female: Guard 1:','Female Guard 1:')
	text = text.replace('Tipur (auto-talk) You two are lifesavers!','Tipur: (auto-talk) You two are lifesavers!')
	text = text.replace('- We here at the Academy have a great','Researcher: - We here at the Academy have a great')
	
	# Tripple new line should break most sequences
	text = text.replace("\n\n\n","\n\n(---)\n\n")
	
	# Put yes/no options together with the questions
	text = text.replace("Accept the mission\n","Accept the mission?\n")
	text = text.replace("Yes \n","Yes\n")
	text = text.replace("?\n\n- Yes","?\n- Yes")
	text = text.replace("?\n\nYes","?\nYes")
	
	text = text.replace("No, that's not possible.\nNo way.","No, that's not possible. No way.")
	
	text = text.replace("Final Fantasy XIII-2: the story so far...","SYSTEM: Final Fantasy XIII-2: the story so far...")
	
	text = text.replace("Wise decision.\n\nChester: They say someone spotted", "Wise decision. They say someone spotted")
	
	# Split text that is attributed to a single character
	dsplits = [
		("- Wh-Whoa, I wasn't expecting that!", "Guard"),
		("- Noel doesn't seem to be a bad guy", "Yuj"),
		("- How about it, future boy?","Lebreau"),
		("- That meteorite is off-limits.", "Gadot"),
		("- You know, Maqui's been acting", "Yuj"),
		("- Let me tell you though, no o", "Roaming Male NORA Member 3"),
		("I apologized to Maqui about the necklace", "Rhett"),
		("- Oh. I'd love to own a pet, too!", "Female Researcher 3"),
		("- A sword and bow are a little out", "Guard"),
		("- I majored in animal behaviors, so my focus", "Female Researcher 1")
		]
	
	for repl,newCharName in dsplits:
		if not text.count(repl)>0:
			print("ERROR: "+repl)
		text = text.replace(repl, "\n\n"+newCharName+":"+repl)
	
	open('../data/FinalFantasy/FFXIII-2/raw/tmp.txt','w').write(text)
	
	chunks = text.split("\n\n")
	
	chunks = [x for x in chunks if len(x.strip())>0]
	
	def needsSplitting(chunk):
		return(chunk.count("\n-")>0 and 
			(not (chunk.count("\nYes")>0 or chunk.count("\nNo")>0)) and 
			(not chunk.startswith("(")))
	
	# Further divide chunks into lines
	lines = []
	for chunk in chunks:		
		if chunk.count(":")<=1:
			if needsSplitting(chunk):
				# Mark chunk as needs splitting
				lines.append("!!!"+chunk)		
			else:
				lines.append(chunk)
		else:
			bits = re.split("\n([A-Z][A-Za-z \-']+[1-9]?):",chunk)
			lines.append(bits[0])
			bits = [x for x in zip(bits[1::2],bits[2::2])]
			for bit in bits:
				bit = ":".join(bit)
				if needsSplitting(bit):
					bit = "!!!"+bit
				lines.append(bit)
	
	# Stuff for live action triggers
	inDecision = False
	choice = []
	cNum = 0
	choiceCue = ""
	embedChoice = False
	embedTxt = ""
	
	# Stuff for yes/no decisions
	inYesNo = False
	selectedYesNoOption = 0
	yesNoOptions = []
	prevYesNoPrompt = ""
	
	out =[]
	for line in lines:
		if line.strip().startswith("Triangle") and any([line.strip().count(x)>0 for x in ["Circle -","X -","Square -"]]):
			if not inDecision:
				inDecision = True
				choice = decisionParser(line,parameters)
				#cNum = 0
		elif line.count("Yes\n")==1 and line.count("No")>=1:
			inYesNo = True
			yesNoPrompt,yesNoPromptLine,selectedYesNoOption = yesNoParser(line)
			if yesNoPrompt != prevYesNoPrompt:
				out.append(yesNoPromptLine)
				yesNoOptions = [[{"ACTION": "Player chooses 'No'"}],[{"ACTION": "Player chooses 'Yes'"}]]
			else:
				# Assume alternative lines only happen for "no"
				if selectedYesNoOption==0:
					yesNoOptions[selectedYesNoOption].append({"--":"--"})
			prevYesNoPrompt = yesNoPrompt
		elif line.strip().startswith("Secret Ending"):
			inDecision = True
			cNum = 0
			choice = [[{"ACTION":line}],[]]
			embedChoice = False
			embedTxt = line
		elif any([line.strip().startswith(x) for x in ["Triangle -", "Circle -","X -","Square -"]]):
			# consequences of choosing a line
			choiceCue = line.strip()
			button, clue = [x.strip() for x in choiceCue.split("-",1)]
			# find which choice to add to
			for i in range(len(choice)):
				# Check if it's the second entry for this button
				# (new option after first triangle choice)
				if choice[i][0]["ACTION"].startswith("Player chooses "+button):
					cNum = i
					# if there's already lines in the sub-choice ...
					if len(choice[i]) > 1:
						#... then this is an embedded choice
						embedChoice = True
						embedTxt = "Player chooses "+choiceCue
					else:
						embedChoice = False
					break
		else:		
			outPart = lineParser(line,parameters)
			# this can be a list, so let's just make sure it's a list
			if not isinstance(outPart,list):
				outPart = [outPart]
			if outPart is not None:
				if inDecision:
					if "ACTION" in outPart[0] or any([line.strip().startswith(x) for x in choiceStoppers]):
						# End of decision
						inDecision = False
						embedChoice = False
						prevYesNoPrompt = ""
						out.append({"CHOICE": choice})
						out += outPart
					else:
						#outPart["_CUE"] = choiceCue
						if embedChoice:
							if "CHOICE" in choice[cNum][-1]:
								choice[cNum][-1]["CHOICE"][0] += outPart
							else:
								choice[cNum].append({"CHOICE": [[{"ACTION":embedTxt}]+ outPart,[]]})
						else:
							choice[cNum] += outPart
				elif inYesNo:
					if "ACTION" in outPart[0] or any([line.strip().startswith(x) for x in choiceStoppers]):
						inYesNo = False
						prevYesNoPrompt = ""
						yesNoOptions[0] = splitNoOptions(yesNoOptions[0])
						out.append({"CHOICE":yesNoOptions})
					else:
						yesNoOptions[selectedYesNoOption] += outPart
					
				else:
					out += outPart
	# Last bit happens to be a choice				
	out.append({"CHOICE": choice})		
				
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)
	
def postProcessing(out):
	out2 = []
	for line in out:
		if line == {"Soldier 2": "(If Serah attempts to move away) Stop resisting! Hey! Keep it movin'!"}:
			out2.append({"CHOICE":[[{"ACTION": "If Serah attempts to move away"}, {"Soldier 2": "Stop resisting! Hey! Keep it movin'!"}],[]]})
		else:
			out2.append(line)
	return(out2)