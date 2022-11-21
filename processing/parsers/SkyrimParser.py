from bs4 import BeautifulSoup
import json,re,copy

# TODO: Scene changes

#  TODO: Quest options: "## IF YOU PICK HADVAR AS THE GUIDE"
	# TODO: "### RALOF/HADVAR SPLIT PATHS R"

# TODO: dialogue that appears after dialogue tree is incorporated 
#  into the last option of the choice e.g.:
# "You've shown yourself mighty, both in Voice and deed"
# Should be its own exit dialogue at end of tree


# Need to recognise dialogue choices from NPC options ("•")


# Balgruuf: What's this about Riverwood being in danger?
# 
#           A dragon destroyed Helgen. Gerdur/Alvor is afraid Riverwood is next.²
#           ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
#            • Alvor? The smith, isn't he? Reliable, solid fellow.
#            • Gerdur? Owns the lumber mill, if I'm not mistaken... Pillar of the
#              community.
# 
#           Not prone to flights of fancy...



#        Riverwood calls for the Jarl's aid.²
#        ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
#         Riverwood's in danger, too? You better go on in. You'll find the Jarl
#         at Dragonsreach, atop the hill.

# The last line is not part of the choice


def parseFile(fileName,parameters={},asJSON=False):
						
	def cleanText(txt):
		if txt.count("_______")>0:
			return("")
		txt = txt.replace("¯","").replace("_","").replace("|","")
		txt = txt.replace("²","").replace("¹","")
		txt = txt.replace("#","")
		txt = re.sub(" +"," ",txt).strip()
		return(txt)
		
	def getIndentLevel(line):
		if line.startswith(" "):
			return(len(re.findall("^ +",line)[0]))
		else:
			return(0)
	
	html_= open(fileName,'r', encoding = 'utf8')
	soup = BeautifulSoup( html_, "html.parser")
	text = soup.find("div", {"id": parameters["textDivId"]})
	text = text.get_text()
	text = text[text.index(parameters["startText"]):text.index(parameters["endText"])]
	text = text.replace("many people who've spoken to Hermaeus Mora.","many people who've spoken to Hermaeus Mora.\n\nSYSTEM: End")
	text = text.replace("         You both agree to this?","Arngeir: You both agree to this?")
	
	text = text.replace("        So who was it? Who had the contract?", "Astrid: ? \n        So who was it? Who had the contract?")

	text = text.replace("          A dragon destroyed Helgen. Gerdur/Alvor is afraid Riverwood is next.²\n          ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯",
						"Dragonborn: A dragon destroyed Helgen. Gerdur/Alvor is afraid Riverwood is next.\n\n")
	text = text.replace("          Not prone to flights of fancy...","Balgruuf: Not prone to flights of fancy...")
	text = text.replace("          What do you say now, Proventus?", "Balgruuf: What do you say now, Proventus?",)
	text = text.replace("          Yes. I had a great view while", "Balgruuf: ? \n\n          Yes. I had a great view while")
	text = text.replace("   wait on your word.","wait on your word.\n\nBalgruuf: ? \n\n")
	text = text.replace("No thanks to you.","No thanks to you.\n\nAela: ? \n\n")
	text = text.replace("So why take chances...","So why take chances...\n\nAstrid: ? \n\n")
	text = text.replace("What kind of business?","What kind of business?\n\nDelvin: ? \n\n")
	text = text.replace('You know, because of your use of...','You know, because of your use of...\n\nGianna: ? \n\n')
	text = text.replace("sending you to Windhelm. Deliver this axe to Ulfric Stormcloak.","sending you to Windhelm. Deliver this axe to Ulfric Stormcloak.\n\nBalgruuf: ? \n\n")
	text = text.replace("protector in an effort to hunt me down.","protector in an effort to hunt me down.\n\nValerica: ? \n\n")
	text = text.replace("   to be destroyed.", "   to be destroyed.\n\nValerica: ? \n\n")
	text = text.replace("he'll keep chasing us for the rest of our lives.", "he'll keep chasing us for the rest of our lives.\n\nSerana: ? \n\n")
	text = text.replace("        • your ambition outgrew your loyalty.","Harkon: • your ambition outgrew your loyalty.")
	text = text.replace("        Of course, if you've got any more adventures planned...", "Serana: Of course, if you've got any more adventures planned...")
	text = text.replace("               This is Apocrypha, where all knowledge is hoarded.","Hermaeus Mora: This is Apocrypha, where all knowledge is hoarded.")
	text = text.replace("               • Perhaps you will prove clever enough","Hermaeus Mora: • Perhaps you will prove clever enough")
	text = text.replace("        • your ambition outgrew your loyalty.","Harkon: • your ambition outgrew your loyalty.")
	text = text.replace("she'd return with hatred in her heart.","she'd return with hatred in her heart.\n\nHarkon: ?\n\n")
	text = text.replace("Your kind is a blight on this world.","Your kind is a blight on this world.\n\nDragonborn: ? \n\n")
	text = text.replace("Is Valerica next? Is Serana?","Is Valerica next? Is Serana?\n\nHarkon: ? \n\n")
	text = text.replace("will call you back. It is your fate.", "will call you back. It is your fate.\n\nHermaeus Mora: ? \n\n")
	text = text.replace("to my realm, as I knew it would.", "to my realm, as I knew it would.\n\nHermaeus Mora: ? \n\n")

	text = text.replace("          • Off to Bleak Falls Barrow with you.","[!]\n\nFarengar: • Off to Bleak Falls Barrow with you.")
	text = text.replace("\n           • Ask around the Ragged Flagon", "           • Ask around the Ragged Flagon")

	text = text.replace("           • You want me to let a dragon into the heart of the city","Balgruuf: • You want me to let a dragon into the heart of the city")

	text = text.replace("         hard-fought.","         hard-fought.\n\nAela: ? \n\n")

	text = text.replace("Ha! Not bloody\n          likely.","Ha! Not bloody likely.")

	# join "•" options into single lines.
	# But need a re-joiner after?
	#text = re.sub("\s+•"," •",text)
	
	# Add re-joiner (but not for actions or )
# 	lastWasDot = False
# 	seenSpace = False
# 	xx = ""
# 	currChar = ""
# 	for line in text.split("\n"):
# 		if re.match("^[A-Z\?]\.?[A-Za-z\?' 0-9\-]+: ",line):
# 			currChar = line[:line.index(":")].strip()
# 
# 		if line.count("•")>0:
# 			lastWasDot = True
# 			seenSpace = False
# 
# 		if seenSpace and lastWasDot:
# 			if line.count(":")==0 and line.count("[")==0:
# 				xx += "888" + currChar + ":" + line.strip() + "\n"
# 			else:
# 				xx += line + "\n"
# 			lastWasDot = False
# 			seenSpace = False
# 		else:
# 			xx += line + "\n"
# 		if len(line.strip())==0:
# 			seenSpace = True
	#text = xx
	
	#text = re.sub("(•.+?\n\n +)([^:]+?\n)","\\1PREV:\\2",text)

	# These two regex replaces many bullet points with equivalent "STATUS" choices
	#text = re.sub("\n( *?)• ","\n\\1 STATUS\n\\1 ¯¯¯¯¯¯¯¯\n\\1  ",text)
	
	def refix1(m):
		initialSpaces = m.group(1)
		charName = m.group(2)
		
		indent = initialSpaces + (" "* len(charName))
		
		# Original line with question mark
		ret = "\n" + initialSpaces +charName + " ?\n\n"
		# Add first status 
		ret += indent + "  STATUS\n"
		ret += indent + "  ¯¯¯¯¯¯¯¯\n" 
		ret += indent + "  " # line continues
		return(ret)
	
	#text = re.sub("\n( *?)(.+?:)? ?• ",refix1,text)
	
	# Attempt to add names into re-start of choice
	# (sort of working, but who knows what effects it's having?)
# 	xx= ""
# 	slevel = ""
# 	prevSLevel = ""
# 	currChar = ""
# 	inStatus = False
# 	for line in text.split("\n"):
# 		slevel = len(line) - len(line.lstrip())
# 		if(line.strip().startswith("STATUS")):
# 			inStatus = True
# 		else:
# 			if(inStatus and (slevel< prevSLevel) and (len(line.strip())>0)):
# 				if not re.match("[A-Z\?]\.?[A-Za-z\?' 0-9\-]+: ",line):
# 					line = currChar + ": " + line.strip()
# 				inStatus = False
# 		if re.match("^[A-Z\?]\.?[A-Za-z\?' 0-9\-]+: ",line):
# 			currChar = line[:line.index(":")].strip()
# 		if len(line.strip())>0:
# 			prevSLevel = slevel
# 		xx += line + "\n"
	#text = xx


	open("../data/ElderScrolls/Skyrim/raw/tmp.txt",'w').write(text)
	
	lines = text.split("\n")
	
	inDescription = False
	inChoice = False
	#inNPCOption = False
	descriptionText = ""
	dialogueText = ""
	#npcOptionText = ""
	charName = ""
	choices = []
	#npcOptions = []
	
	# Greedy algorithm to join lines into coherent parts
	out = []
	for i in range(len(lines))[:-1]:
		line = lines[i]
		
		if line.count("....")>0:
			continue
			
# 		if line.count("•")>0:
# 			if inNPCOption:
# 				# a new option within the same list
# 				if len(npcOptionText)>0:
# 					# dump
# 					npcOptions.append(npcOptionText)
# 					npcOptionText = line.strip()
# 			else:
# 				inNPCOption = True
# 				npcOptionText = line.strip()

		# Is this an action line?
		if line.startswith("[") or line.startswith("###"):
			# We may already be at the end of another description?		
			if inDescription:
				if len(cleanText(descriptionText))>0:
					if descriptionText.count('===')==0:
						out.append({"ACTION":cleanText(descriptionText)})				
				descriptionText = ""
			# We may have a line in memory?
			if len(cleanText(dialogueText))>0:
				out.append({charName:cleanText(dialogueText)})
				dialogueText = ""
			# start of a description
			inDescription = True
			descriptionText = line

			inChoice = False
			if len(choices)>0:
				out.append({"CHOICE":choices})
				choices = []
# 			inNPCOption = False
# 			if len(npcOptions)>0:
# 				if len(npcOptionText)>0:
# 					npcOptions.append(npcOptionText)
# 					npcOptionText = ""
# 				#out.append({"CHOICE":npcOptions})
# 				npcOptions = []	
		if line.strip().endswith("]") or line.strip().endswith("###"):
			# end of description 
			if inDescription:
				#(could be same line as the start)
				if line.count("[")==0:
					descriptionText += " "+ line.strip()
				inDescription = False 
			if len(cleanText(descriptionText))>0:
				if descriptionText.count('===')==0:
					out.append({"ACTION":cleanText(descriptionText)})
			descriptionText = ""
		elif inDescription:
			# description line text continuing
			#descriptionText += line
			pass
		else:
			# plain line
			if len(cleanText(descriptionText))>0:
				if descriptionText.count('===')==0:
					out.append({"ACTION":cleanText(descriptionText)})
				descriptionText = ""
			# Process plain line			
			if re.match("^[A-Z\?]\.?[A-Za-z\?' 0-9\-]+: ",line):
				if inChoice:
					# Add choices
					out.append({"CHOICE":choices})
					inChoice = False
					choices = []
# 				if len(npcOptions)>0:
# 					if len(npcOptionText)>0:
# 						options.append(npcOptionText)
# 						npcOptionText = ""
# 					out.append({"CHOICE":npcOptions})
# 					npcOptions = []	
				# add dialogue
				if len(cleanText(dialogueText))>0:
					out.append({charName:cleanText(dialogueText)})
				dialogueText = cleanText(line[line.index(":")+1:].strip())
				# change Character
				charName = line.split(":")[0].strip()
			#elif line.strip().startswith("::"):
			#	# Choice
			#	inChoice = True
			#	choiceDialogue = line.replace("::","").replace("(","").replace(")","").strip()
			#	choices.append([{parameters["playerCharacter"]: choiceDialogue}])
			elif (lines[i+1].count("¯¯")>0 or lines[i+1].count("|¯")>0) and (line.count("|¯")==0):
				# Add any existing lines
				if len(cleanText(dialogueText))>0:
					out.append({charName:cleanText(dialogueText)})
					dialogueText = ""
				inChoice = True
				if len(cleanText(line))>0:
					choiceIndentLevel = getIndentLevel(line)
					cxDialogue = cleanText(line)
					# Look ahead to next line to see if there's extra dialogue
					if line.count("|¯¯¯")==0 and lines[i+1].count("|¯¯¯")>0:
						cxDialogue += " " + lines[i+1]
						cxDialogue = cleanText(cxDialogue)
					choices.append([{parameters["playerCharacter"]: cxDialogue,"_INDENT":choiceIndentLevel}])
			elif line.count("|¯¯¯")>0:# and len(line.replace("¯","").strip())>1:
				# overhanging dialogue from a PC dialogue option
				# (dealt with above)
				pass
			else:
				if inChoice and line.count(".........")==0:
					# overhang line from NPC in choice				
					if len(choices)>0 and len(line.strip())>0:
							if len(cleanText(line))>0:
								if parameters["playerCharacter"] in choices[-1][-1]:
								# first line in new NPC 
									choiceIndentLevel = getIndentLevel(line)-1
									choices[-1].append({charName:cleanText(line).strip(),
														"_INDENT":choiceIndentLevel})
								else:
								# continuing line
									#if prev lines have •
									if line.count("•")==0 and len(lines[i-1].strip())==0 and any([x.count("•")>0 for x in lines[i-4:i]]):
										inChoice = False
										out.append({"CHOICE":choices})
										choices = []
										if len(cleanText(dialogueText))>0:
											out.append({charName:cleanText(dialogueText)})
										dialogueText = cleanText(line)
									else:
										# part of the previous line
										choices[-1][-1][charName] += " " + cleanText(line)
				elif len(line)>0 and line.count("¯¯¯")==0 and line.count("_____")==0 and line.count("=====")==0:
					dialogueText += " " + cleanText(line.strip())
					
	# Deal with options based on class/questline
	
	def findCharacterNameKey(d):
		for k in d:
			if not k.startswith("_"):
				return(k)
						
	# Process optional dialogue
	finalOut = []
	for item in out:
		charName = findCharacterNameKey(item)
		part = item[charName]	
		if isinstance(part,str):# and part!="ACTION" and part!="CHOICE":

# Not needed because we're converting • to choices first
# 			if "•" in part:
# 				partIndent =getIndentLevel(part)
# 				# There may be central dialogue before the option
# 				preOption = part[:part.index("•")].strip()
# 				if len(preOption)>0:
# 					finalOut.append({charName:preOption})
# 				part = part[part.index("•"):]
# 				opts = [x.strip() for x in part.split("•") if len(x.strip())>0]
# 				rep = {"CHOICE": [[{"STATUS":"Player race/questline", "_INDENT":partIndent},
# 									{charName:opt}] for opt in opts]}
# 				finalOut.append(rep)
# 			else:
# 				# no change necessary
 				finalOut.append(item)
		else:
			# part is a choice that needs to be processed as well
			for choices in part:
				outChoices = []
				for choice in choices:
		# --- THIS CODE REPEATED FROM ABOVE. BAD!
					charName = findCharacterNameKey(choice)
					part = choice[charName]
					if isinstance(part,str) and part!="ACTION" and part!="CHOICE":
						if "•" in part:
							partIndent =getIndentLevel(part)
							# There may be central dialogue before the option
							preOption = part[:part.index("•")].strip()
							if len(preOption)>0:
								#finalOut.append({charName:preOption})
								# TODO: FIX????
								outChoices.append({charName:preOption})
							part = part[part.index("•"):]
							opts = [x.strip() for x in part.split("•") if len(x.strip())>0]
							
							rep = {"CHOICE": [[{"STATUS":"Player race/questline", "_INDENT":partIndent},
													{charName:opt}] for opt in opts]}
							outChoices.append(rep)
						else:
							# no change necessary
							outChoices.append(choice)
				finalOut.append({"CHOICE":outChoices})
		# --- THIS CODE REPEATED FROM ABOVE. BAD!
			#finalOut.append(item)
	
	
	def buildChoiceStructureOLD(choices,prevLevel=0):
		outx = {"CHOICE":[]}
		for i in range(0,len(choices)):
			cx = choices[i]
			thisLevel = prevLevel # assume prevLevel if not available.
			if not isinstance(cx["CHOICE"][0],list):
				thisLevel = cx["CHOICE"][0]["_INDENT"]
			# choose where to put	
			if thisLevel == prevLevel:
				outx["CHOICE"].append(cx["CHOICE"])
			elif thisLevel > prevLevel:
				outx["CHOICE"].append(buildChoiceStructure(choices[i:],thisLevel))
			else:
				if thisLevel>0:
					return(outx)
		return(outx)
	
	
	# Build dialogue tree
	def buildChoiceStructure(choices,prevLevel=-1):
		outx = {"CHOICE":[]}
		
		if prevLevel==-1:
			if isinstance(choices[0]["CHOICE"][0],list):
				prevLevel = choices[0]["CHOICE"][0][0]["_INDENT"]
			else:
				prevLevel = choices[0]["CHOICE"][0]["_INDENT"]
		
		for i in range(0,len(choices)):
			cx = choices[i]
			cLevel = prevLevel # assume prevLevel if not available.
			if not isinstance(cx["CHOICE"][0],list):
				cLevel = cx["CHOICE"][0]["_INDENT"]
				
			if cLevel>prevLevel and prevLevel>0:
				# don't need to process this item at this level,
				# but there may be others later
				continue 
			if cLevel<prevLevel:
				return(outx)

			# Look ahead to next level
			try:
				nextx = choices[i+1]
			except:
				nextx = {"CHOICE":[{"_INDENT":0}]}
			
			nextLevel = cLevel # assume prevLevel if not available.
			
			cx = copy.deepcopy(cx)
			for xxx in range(len(cx["CHOICE"])):
				if "_INDENT" in cx["CHOICE"][xxx]:
					del cx["CHOICE"][xxx]["_INDENT"]

			if not isinstance(nextx["CHOICE"][0],list):
				nextLevel = nextx["CHOICE"][0]["_INDENT"]
			# choose where to put current item
			if nextLevel == prevLevel:
				outx["CHOICE"].append(cx["CHOICE"])
			elif nextLevel > prevLevel:
				outx["CHOICE"].append(cx["CHOICE"]) #x
				outx["CHOICE"][-1].append(buildChoiceStructure(choices[i+1:],nextLevel))
			else:
				outx["CHOICE"].append(cx["CHOICE"])
				return(outx)
		return(outx)
	
	
	finalOut2 = []
	tmpChoices = []
	inChoice = False
	for item in finalOut:
		if "CHOICE" in item:
			inChoice = True
			tmpChoices.append(item)
		else:
			if inChoice:
				# Post process choices
				if len(tmpChoices)==1:
					finalOut2.append(tmpChoices[0])
				else:
					choiceStructure = buildChoiceStructure(tmpChoices)
					finalOut2.append(choiceStructure)
				inChoice = False
				tmpChoices = []
			# Add normal item that tripped the choice
			if not "" in item:
				finalOut2.append(item)
				
	finalOut3 = []
	for item in finalOut2:
		k = findCharacterNameKey(item)
		dlg = item[k]
		if (not isinstance(dlg,str)) or (dlg.strip()!="?"):
			finalOut3.append(item)
	
	
	repl = [
		(		{"CHOICE": [
				{"Dragonborn": "They seem to think he's hiding out in Riften.", "_INDENT": 10},
				{"CHOICE": [
						[
							{"STATUS": "Player race/questline", "_INDENT": 0},
							{"Delphine": "Talk to Brynjolf. He's...well-connected. A good starting point, at least."}],
						[
							{"STATUS": "Player race/questline", "_INDENT": 0},
							{"Delphine": "Ask around the Ragged Flagon, in the Ratway. It's at least a good starting point."}]]}]},
				{"CHOICE": [
					[{"Dragonborn": "They seem to think he's hiding out in Riften.", "_INDENT": 10},
					{"Delphine": "Riften, eh? Probably down in the Ratway, then. It's where I'd go. You'd better get to Riften."},
					{"CHOICE": [
						[
							{"STATUS": "Player race/questline", "_INDENT": 0},
							{"Delphine": "Talk to Brynjolf. He's...well-connected. A good starting point, at least."}],
						[
							{"STATUS": "Player race/questline", "_INDENT": 0},
							{"Delphine": "Ask around the Ragged Flagon, in the Ratway. It's at least a good starting point."}]]},
					{"Delphine": "Delphine: Oh, and when you find Esbern...if you think I'm paranoid...you may have some trouble getting him to trust you. Just ask him where he was on the 30th of Frostfall. He'll know what it means."}]]}),
	########
		({"Delphine": "Oh, and when you find Esbern...if you think I'm paranoid...you may have some trouble getting him to trust you. Just ask him where he was on the 30th of Frostfall. He'll know what it means."},{"ACTION":"---"}),
		({"Delphine": "Riften, eh? Probably down in the Ratway, then. It's where I'd go. You'd better get to Riften."}, {"ACTION":"---"}),
		({"CHOICE": [
				[
					{"Dragonborn": "You know I wouldn't ask if it wasn't important. (Persuade)"},
					{"Balgruuf": "Of course. You already saved Whiterun from that dragon. I owe you a great deal. But I don't understand. Why let a dragon into the heart of my city when we've been working so hard to keep them out?"}],
				[
					{"Dragonborn": "You heard right. It's the only way to stop the dragons."},
					{"Balgruuf": "What you're asking for is insane. Impossible!"}],
				[
					[
						{"STATUS": "Player race/questline", "_INDENT": 0},
						{"Balgruuf": "You want me to let a dragon into the heart of the city, with the threat of war on my doorstep?"}],
					[
						{"STATUS": "Player race/questline", "_INDENT": 0},
						{"Balgruuf": "Why would I agree to let a dragon into the heart of my city, after working so hard to keep them out?"}]]]},
		{"CHOICE": [
				[
					{"Dragonborn": "You know I wouldn't ask if it wasn't important. (Persuade)"},
					{"Balgruuf": "Of course. You already saved Whiterun from that dragon. I owe you a great deal. But I don't understand. Why let a dragon into the heart of my city when we've been working so hard to keep them out?"}],
				[
					{"Dragonborn": "You heard right. It's the only way to stop the dragons."},
					{"Balgruuf": "What you're asking for is insane. Impossible!"},
					{"CHOICE":[
					[
						{"STATUS": "Player race/questline", "_INDENT": 0},
						{"Balgruuf": "You want me to let a dragon into the heart of the city, with the threat of war on my doorstep?"}],
					[
						{"STATUS": "Player race/questline", "_INDENT": 0},
						{"Balgruuf": "Why would I agree to let a dragon into the heart of my city, after working so hard to keep them out?"}]]}]]})
	]
	finalOut4 = []
	for line in finalOut3:
		found = False
		for rx in repl:
			if line==rx[0]:
				finalOut4.append(rx[1])
				found = True
				break
		if not found:
			finalOut4.append(line)
			
	finalOut5 = []
	for line in finalOut4:
		k = [x for x in line if not x.startswith("_")][0]
		if k == "CHOICE" and not isinstance(line[k][0],list):
			finalOut5.append({"CHOICE":[line[k]]})
		else:
			finalOut5.append(line)
			
# 	def replPoint(lines):
# 		out = []
# 		for line in lines:
# 			k = [x for x in line if not x.startswith("_")][0]
# 			if k=="CHOICE":
# 				choices = []
# 				for choice in line[k]:
# 					choices.append(replPoint(choice))
# 				out.append({"CHOICE":choices})
# 			else:
# 				print(line)
# 				dlg = line[k]
# 				if dlg.count("•")>0:
# 					bits = dlg.split("•")
# 					end = ""
# 					if bits[-1].count("888")>0:
# 						bits[-1],end = bits[-1].split("888")
# 					out.append({"CHOICE":[[{k:bit}] for bit in bits]})
# 					if len(end)>0:
# 						if end.count(":")>0:
# 							end = end[end.index(":")+1:]
# 						out.append({k:end})
# 				out.append(line)
# 		return(out)
# 	
# 	finalOut4 = replPoint(finalOut3)		
	
	if asJSON:
		return(json.dumps({"text":finalOut5}, indent = 4))
	return(finalOut5)
	


	


	

	

	
	



