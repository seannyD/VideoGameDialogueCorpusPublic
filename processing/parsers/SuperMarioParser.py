from bs4 import BeautifulSoup
import json,re


def parseFile(fileName,parameters={},asJSON=False):

	debugOn = False
	def debugPrint(x):
		if debugOn:
			print(x)
						
	def cleanText(txt):
		txt = txt.replace("¯","").replace("_","")
		txt = txt.replace("..."," ... ")
		txt = re.sub("--+"," ",txt)
		txt = re.sub("__+"," ",txt)
		txt = re.sub(" +"," ",txt)
		for title in ["-the jinx scripts-","-the gardener scripts-","-the culex scripts-"]:
			txt = txt.replace(title,"")
		return(txt.strip())
	
	html_= open(fileName,'r', encoding = 'utf8')
	soup = BeautifulSoup( html_, "html.parser")
	text = soup.find("div", {"id": parameters["textDivId"]})
	text = text.get_text()
	text = text[text.index(parameters["startText"]):text.index(parameters["endText"])]
	lines = text.split("\n")
	
	inDescription = False
	inChoice = False
	inOptionalDialogue = False
	descriptionText = ""
	dialogueText = ""
	charName = ""
	choices = []
	
	out = []
	for i in range(len(lines)):
		line = lines[i]
		debugPrint(line)
		debugPrint((inDescription,inChoice, inOptionalDialogue, len(descriptionText),len(choices)))
		if line.startswith("____"):
			debugPrint("|1")
			if lines[i+1].count(">>")==0:
				debugPrint("|1.1")
				# start of a description
				inDescription = True
			else:
				debugPrint("|1.2")
				# possible end of optional dialogue
				inOptionalDialogue = False		
			if len(cleanText(dialogueText))>0:
				debugPrint("|1.3")
				# leftover dialogue after a description within someone's lines
				if inChoice:
					choices[-1].append({charName:cleanText(dialogueText)})
				else:
					out.append({charName:cleanText(dialogueText)})
				dialogueText = ""
			if len(choices)>0:
				debugPrint("|1.4")
				out.append({"CHOICE":choices})
				choices = []
			inChoice = False
		elif line.startswith("¯¯¯¯¯¯") and not (lines[i-1].startswith(">>")):
			debugPrint("|2")
			# end of description  (and not just an outline of an option)
			inDescription = False
			inOptionalDialogue = False
			if len(descriptionText)>0:
				out.append({"ACTION":cleanText(descriptionText)})
			descriptionText = ""
		elif inDescription:
			debugPrint("|3")
			# description line text
			if not descriptionText.strip().endswith(" "):
				descriptionText += " "
			descriptionText += line
		else:	
			# plain line
			if re.match("^[A-Za-z\?'0-9&\\.\\(\\) ]+: ",line) and (not inOptionalDialogue) and (line.count("The orders are")==0):
				debugPrint("|4")
				# add dialogue
				if re.match("^ +¯¯",lines[i-1]):
					debugPrint("|4.1")
					# We're still in the choice, adding dialogue from new character
					dialogueText = cleanText(line[line.index(":")+1:].strip())
					charName = line.split(":")[0].strip()
					if len(dialogueText)>0:
						if len(choices)>0:
							choices[-1].append({charName:dialogueText})
						else:
							choices = [{charName:dialogueText}]
						dialogueText = ""
				else:
					debugPrint("|4.2")
					# New line of dialogue outside choice
					dt = cleanText(dialogueText)
					if len(dt)>0:
						debugPrint("|4.3")
						out.append({charName:dt})
					dialogueText = line[line.index(":")+1:].strip()
					# change Character
					charName = line.split(":")[0].strip()
					# Add choices
					if inChoice:
						debugPrint("|4.4")
						out.append({"CHOICE":choices})
						inChoice = False
						choices = []
			elif line.strip().startswith("[") or line.startswith("+"):
				# action
				debugPrint("|5")
				# We might already have some dialogue to add.
				if len(cleanText(dialogueText))>0:
					out.append({charName:cleanText(dialogueText)})
					dialogueText = ""
									
				action = line.replace("[","").replace("]","").replace("+","").strip()
				if len(cleanText(action))>0:
					out.append({"ACTION":cleanText(action)})
			elif line.strip().startswith("::"):
				# Choice
				debugPrint("|6")
				# We might already have some dialogue to add.
				if len(cleanText(dialogueText))>0:
					out.append({charName:cleanText(dialogueText)})
					dialogueText = ""
				
				inChoice = True
				choiceDialogue = line.replace("::","").replace("(","").replace(")","").strip()
				choices.append([{parameters["playerCharacter"]: choiceDialogue}])
			elif line.strip().startswith(">>"):
				debugPrint("|7")
				# TODO: It's not always a dialogue choice
				inChoice = True
				inOptionalDialogue = False
				choiceAction = line.replace(">>","").replace("(","").replace(")","").strip()
				# This is most often an action, rather than dialogue?
				choices.append([{"ACTION": choiceAction}])				
			else:
				if line.startswith("¯¯"):
					debugPrint("|8")
					inOptionalDialogue = True
					#if len(choices)>0:
					#	# some optional text hung over
					#	out.append({"CHOICE":choices})
					#choices = []
					inChoice = True
				elif inChoice:
					debugPrint("|9")
					# overhang line from NPC in choice
					# (treat as different lines for now)

					if re.match("^[A-Za-z\?'0-9&\\.\\(\\) ]+: ",line):
						# New speaker within a choice
						debugPrint("|10")
						# Add old dialogue	
						if len(cleanText(dialogueText))>0:
							if len(choices)>0:
								choices[-1].append({charName:cleanText(dialogueText)})			
							else:
								choices = [[{charName:cleanText(dialogueText)}]]

						# Switch to new character
						charName = line.split(":")[0].strip()
						line = line[line.index(":")+1:].strip()
						dialogueText = line.strip()

						
					elif len(choices)==0 and len(line.strip())>0:
						debugPrint("|11")
						#choices = [[{charName:cleanText(dialogueText)}]]
						dialogueText += " "+line.strip()
							
					elif len(choices)>0 and len(line.strip())>0:
						if lines[i-1].strip().startswith("__"):
							debugPrint("|12")
							# description within a choice
							if len(cleanText(line.strip()))>0:
								choices[-1].append({"ACTION":cleanText(line.strip())})
						else:
							debugPrint("|13")
							dialogueText += " " + line.strip()
							if len(cleanText(dialogueText))>0:
								# This used to just append 'line', not dialogue text
								choices[-1].append({charName:cleanText(dialogueText.strip())})
								dialogueText = ""
				else:
					# overhang line, just add to dialogue text
					if lines[i-1].strip().startswith("__"):
						debugPrint("|14")
						# action within some dialogue
						# Add dialogue so far
						if len(cleanText(dialogueText))>0:
							out.append({charName:cleanText(dialogueText)})
							dialogueText = ""
						# Add action
						out.append({"ACTION": line.strip()})
					elif (lines[i-1].count("-¯-")>0) and (lines[i+1].count("-¯-")>0):
						debugPrint("|15")
						out.append({"LOCATION":cleanText(line).strip()})
					elif len(line)>0 and line.count("-¯-_")==0:							
						debugPrint("|16")
						if line.strip().startswith("__"):
							if len(cleanText(dialogueText))>0:
								if len(choices)==0:
									out.append({charName:cleanText(dialogueText)})
									dialogueText = ""
						else:
							dialogueText += " " + line.strip()


	
	# ... code to parse a list (dialogue options)
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)
	


	


	

	

	
	



