#TODO
# Handyman (and Beatles fan): I’m fixing a hole where the rain gets in.
# Girl with doggie (usually): 

# Note: AB class is Al Bhed

# TODO:
#					{"CHOICE": [
#							[
#								{"Tidus": "Yes. [Give him some Gil.]"},
#								{"O’aka": "You’re really gonna give me X Gil?"},
#								[
#									{"Tidus": "Yes."},
#									{"O’aka": "I guess it pays to ask! Thank ye kindly, lad! Fine seed money for the O’aka merchant empire! Much obliged, lad! I’ll be sure to pay ye back!"}],

# TODO:
# http://auronlu.istad.org/ffx-script/chapter-iv-luca/
# Sailor with blue cap on gangway: I’m sorry, sir, but the ferry will remain at anchor for a while.


# TODO:
# 	{"Man in red shorts": "Couple talking on mainland side of causeway ("},
# 	{"woman in white halter top": ", portly"},

# TODO:
# Unlist recursive lineRecogniser
#		{"ACTION": "[Wakka lets him go. Fade to black]"},
#		[
#			{"Tidus": "I know."}],

# TODO:
# "tri" and "mov" spans

#	{"Redheaded woman": "(AKA \"5th from the right\")"},


from bs4 import BeautifulSoup, NavigableString, Tag
import json, re
import bs4

def parseFile(fileName,parameters={},asJSON=False):


	print(fileName)
	html = open(fileName, 'r')
	html = html.read().replace('<span class="mov">(Whistles.)</span>','<span class="mov">(Whistles.)</span></span>')
	
	soup = BeautifulSoup(html, 'html5lib')
	try:
		soup.find("a",{"target":"screencap","href":"../characters/noy.jpg"})["class"] = 'who'
	except:
		pass
	

	posts = soup.find('div', 'entry-content')
	
	def cleanDialogue(txt):
		txt = txt.replace("\n"," ")
		txt = txt.replace("¬"," ")
		txt = txt.replace("¬"," ")
		txt = txt.replace('“','"')
		txt = txt.replace('”','"')
		txt = txt.replace('’',"'")
		txt = txt.replace('‘',"'")
		txt = txt.replace("…"," ... ")
		txt = txt.replace("\\xa0", " ")
		txt = txt.replace("\xa0", " ")
		txt = re.sub(" +"," ",txt)
		if txt.startswith("-"):
			txt = txt[1:]
		txt = txt.strip()
		return(txt)
		
	def cleanName(txt):
		global previousCharNames
		txt = txt.replace("¬","")
		txt = txt.replace('’',"'")
		txt = txt.replace('“','"')
		txt = txt.replace('”','"')
		txt = txt.strip()
		if txt.startswith("(") and txt.endswith(")"):
			txt = txt[1:-1]
		txt = txt.strip()
		
		# Sometimes the name in an <a> tag is re-used
		# later, but in a curtailed form
		# for example "Woman in long skirt" becomes just "Woman"
		# We only want to set the character name if this is not the case
		
		# (Yuna part, because there's also "Yunalesca")
		matchingNames = [x for x in previousCharNames[-6:] if x.startswith(txt) and (not x.startswith("Yuna"))]
		if len(matchingNames)>0:
			txt = matchingNames[-1]
		else:
			previousCharNames.append(txt)
		
		return(txt)

	def getTextFromUnknownObject(element):
		scriptLine = ""
		if type(element) == str:
			scriptLine = element
		elif isinstance(element, bs4.element.NavigableString):
			element = str(element)
			scriptLine = element
		else:
			# Gift tags are removed
			for gift in soup.find_all("span",{"class":"gift"}):
				gift.extract()
			# For e.g. "[Buy items. | Leave.]"
			for choices in soup.find_all("span",{"class":"choices"}):
				choices.extract()
			scriptLine = element.getText()
		return(scriptLine)

	def lineOfDialogueParser(element):
		scriptLine = getTextFromUnknownObject(element)
		if scriptLine.count(":") > 0:
			characterName = scriptLine[:scriptLine.index(":")].strip()
			dialogue = scriptLine[scriptLine.index(":")+1:].strip()
			return({cleanName(characterName):cleanDialogue(dialogue)})
		return(None)

	def bracketParser(element):
		bracketLine = ""
		scriptLine = element
		if scriptLine is not None:
			if scriptLine.count("(") > 0:
				bracketLine = scriptLine[scriptLine.index(":")+1].strip()
			return({bracketLine})
		return(None)
		

	def mainCharacterParser(element,classList):
		# e.g. span class="T"
		mcOut = []
		thisCharName = ""
		if element is not None:
			
			bits = [lineRecogniser(line) for line in element]
			bits = [b for b in bits if not b is None]
					
			for line in element:
				if isinstance(line,bs4.element.NavigableString) or isinstance(line,str):
					txt = getTextFromUnknownObject(line)
					if txt.startswith(":"):
						txt = txt[1:]
					elif txt.count(":")>0:
						# (also captures lines ending in ":")
						thisCharName = txt[:txt.index(":")].strip()
						txt = txt[txt.index(":")+1:]
					dialogue = cleanDialogue(txt)
					if len(dialogue)>0:
						if thisCharName!="":
							mcOut.append({cleanName(thisCharName):dialogue})
						else:
							print("ERROR: No char name: ")
							print(element)
				elif line.name == "span" and "mov" in line.get("class"):
						mcOut.append({"ACTION":cleanName(thisCharName)+": "+ getTextFromUnknownObject(line)})
				elif line.name=="br":
					pass
				else:
					print("OTHER")
					print(element)
		return(mcOut)
			

		
#	def TidusParser(element):
# 		if element is not None:
# 			txt = element.get_text()
# 			try:
# 				charName = txt[:txt.index(":")].strip()
# 				dialogue = txt[txt.index(":")+1:]
# 				dialogueWithoutParentheses = re.sub("\(.+?\)","",dialogue).strip()
# 				if len(dialogueWithoutParentheses)==0:
# 					return({"ACTION": cleanName(charName)+": "+cleanDialogue(dialogue).replace("(","").replace(")","")})
# 				else:
# 					return({cleanName(charName):cleanDialogue(dialogue)})
# 			except:
# 				pass

	def miscParser(element):
		if element is not None:
			txt = element.get_text()
			if txt.count(":")>0:
				if txt.count(":")==1:
					charName = txt[:txt.index(":")].strip()
					dialogue = txt[txt.index(":")+1:]
					return({cleanName(charName):cleanDialogue(dialogue)})
				else:
					bits = [lineRecogniser(x) for x in element]
					return(bits)
		return(None)

# 	def auronParser(element):
# 		if element is not None:
# 			txt = element.get_text()
# 			try:
# 				charName = txt[:txt.index(":")].strip()
# 				dialogue = txt[txt.index(":")+1:]
# 				return({cleanName(charName):cleanDialogue(dialogue)})
# 			except:
# 				pass

# 	def ALTnpcParser(element):
# 		# TODO: Sometimes, multiple NPCs can be defined for the same line
# 		# e.g.: Skate rat, man in yellow pants, another kid: Good luck!
# 		global lastNPC
# 		outx = []
# 		for bit in element:
# 			if bit.name=="a": # It's a clear definition of a character name
# 				lastNPC = bit.get_text()
# 			else:  # Could be plain text, or span object.
# 				dialogue = getTextFromUnknownObject(bit).strip()
# 				if dialogue.count(":")>0:
# 					newCharName = dialogue[:dialogue.index(":")].strip()
# 					newCharName = re.sub("\(.+?\)","",newCharName).strip()
# 					if len(newCharName)>1 and len(newCharName)<60:
# 						# Sometimes the name in an <a> tag is re-used
# 						# later, but in a curtailed form
# 						# for example "Woman in long skirt" becomes just "Woman"
# 						# We only want to set the character name if this is not the case
# 						if not lastNPC.startswith(newCharName):
# 							lastNPC = newCharName
# 					dialogue = dialogue[dialogue.index(":")+1:].strip()
# 				if len(cleanDialogue(dialogue))>1:
# 					outx.append({cleanName(lastNPC): cleanDialogue(dialogue)})
# 		return(outx)
				
	
# 	def npcParser2(element):
# 		global lastNPC
# 		# recognise line
# 		multiChar = []
# 		for line in element:
# 			if line.name=="a" and "who" in line.get("class"):
# 				multiChar.append(line.get_text())
# 			else:
# 				bit = lineRecogniser(line)
# 				if not bit is None:
# 					if isinstance(bit,)
		# if it's a char name, and we haven't seen dialogue, add to list of speakers
		# if it's mov, return an action dict
		# if it's dialogue, return a dialogue dict
	

	def npcParser(element):
		global lastNPC
		# Step 1: identify names	
		# Multiple NPCs can be defined
		whos = element.find_all("a",{"class":"who"})
		if len(whos)>0:
			# There are explicit <a> tags, so use those:
			charNames = [who.get_text() for who in whos]
			charNames = [re.sub("\(.+?\)","",charName).strip() for charName in charNames]
			for who in whos:
				who.extract()
		else:
			# Plain text.
			# Check if there's a character name in plain text
			txt = getTextFromUnknownObject(element)
			if txt.count(":")==1 and txt.index(":") < 60:
				charNames = txt[:txt.index(":")].strip()
				charNames = re.sub("\(.+?\)","",charNames).strip()
				charNames = charNames.split(",")
				charNames = [x.replace(" and ","").strip() for x in charNames]
			elif txt.count(":")>1:
				# Multiple bits of dialogue, need to parse each element
				# (switch back to html elements)
				bits = []
				for x in element:
					bits.append(lineRecogniser(x))
				bits = [x for x in bits if not x is None]
				if len(bits)>0:
					# TODO: is this returning embedded lists?
					return(bits)
				else:
					# Back off to parsing strings
					bits = [lineRecogniser(x) for x in txt.split("\n")]
					if len(bits)>0:
						return(bits)
					else:
						return(None)
			else:
				# Continuing dialogue from previous character
				charNames = [lastNPC]
		
		# At this point, we've just set the character name(s)
		dialogue = getTextFromUnknownObject(element)
		if dialogue.count(":")>0:
			dialogue = dialogue[dialogue.index(":")+1:].strip()
		dialogue = cleanDialogue(dialogue)
		if len(dialogue)>0:
			# xx
			if len(charNames)==1:
				return({cleanName(charNames[0]):dialogue})
			else:
				return([{cleanName(charName):dialogue} for charName in charNames])
		else:
			return(None)

	def ulParser(line):
		mainOut = []
		choice = []
		for bit in line:
			if bit.name== "li" and "choice" in bit.get("class"):
				if len(choice)>0:
					mainOut.append(choice)
				choice = [{"Tidus":cleanDialogue(bit.get_text())}]
			elif bit.name== "li" and "reply" in bit.get("class"):
				for subline in bit:
					lx = lineRecogniser(subline)
					if lx is not None:
						if isinstance(lx,list):
							if isinstance(lx[0],list):
								# embedded list
								for x in lx:
									if isinstance(x,list):
										for xx in x:
											choice += xx
									else:
										choice += x
							else:
								choice += lx
						else:
							choice.append(lx)
			else:
				pass
		if len(choice)>0:
			#mainOut.append({"CHOICE":choice})
			mainOut.append(choice)
		return({"CHOICE":mainOut})	
					
	def stringLineParser(line):
		global lastNPC
		txt = getTextFromUnknownObject(line)
		if txt.startswith(":"):
			charName = lastNPC
			dx = cleanDialogue(txt[1:])
			if len(dx)>0:
				return({cleanName(lastNPC):dx})
		elif txt.count(":")>0:
			# (also captures lines ending in ":")
			charName = txt[:txt.index(":")].strip()
			
			if any([charName.startswith(x) for x in ["in ","on ","beside ","at ","near ","not ","conversing ","barring ","with ","talking ","running ","standing "]]):
				# This is pat of the name but not in the <a> tag
				charName = lastNPC + " " +charName
				charName = re.sub(" +"," ",charName)
			elif len(re.sub("\(.+?\)","",charName).strip())==0:
				charName = lastNPC
				
			if (not lastNPC.startswith(charName)) or charName.startswith("Yuna"):
				lastNPC = charName
			txt = txt[txt.index(":")+1:].strip()
		else:
			# Text is dialogue, attribute to last speaker
			charName = lastNPC
		dx = cleanDialogue(txt)
		if len(dx)>0:
			return({cleanName(charName):dx})
		else:
			return(None)
		
	def lineRecogniser(line):
		global lastNPC
		#print((line,fileName))
		
		if isinstance(line,bs4.element.NavigableString) or isinstance(line,str): # or string?
			# Raw line of dialogue, attribute it to the last NPC
			return(stringLineParser(line))
		elif line.name == "p":
			# Recursive
			lineParse = [lineRecogniser(x) for x in line]
			lineParse = [x for x in lineParse if x is not None]
			# TODO: unlist?
			if len(lineParse)>0:
				retChoice = []
				for lx in lineParse:
					if isinstance(lx,list):
						retChoice += lx
					else:
						retChoice.append(lx)
				return({"CHOICE":[[],retChoice]})
			else:
				return(None)
# 			if len(lineParse)>0:
# 				if lineParse[0]==[]:
# 					lineParse = {"CHOICE":lineParse}
# 				elif isinstance(lineParse[0],list):
# 					finalParse = []
# 					for x in lineParse:
# 						finalParse.append(x)
# 					return(finalParse)									
# 				else:
# 					return(lineParse)
# 			else:
# 				return(None)
		elif line.name == "span":
			if "npc" in line.get("class"):
				return(npcParser(line))
			elif ("TN" in line.get("class") or "clue" in line.get("class")):
				return({"NARRATION":line.get_text()})
			elif any([x in line.get("class") for x in ["stage","mov","tri"]]):
				return({"ACTION": cleanDialogue(line.get_text())})
			else:
				return(npcParser(line))
				#return(mainCharacterParser(line,line.get("class")))
				
		elif (line.name == "h3" or line.name == "h4") and ("where" in line.get("class") or "sc" in line.get("class")):
			return({"LOCATION":line.get_text()})

		# In case we get a 'who' tag, just set the last npc name
		elif line.name == "a":
			if line.get("class") is None or "who" in line.get("class"):
				lastNPC = line.get_text()
				return(None)
			
		elif line.name=="ul":
			return(ulParser(line))
			
		else:
			return(None)

###############
#  MAIN LOOP
###############
	out = []
	outx = []
	
	global lastNPC
	lastNPC = ""
	global previousCharNames
	previousCharNames = []
	saveDialogue = ""

	for child in posts.children:
		
		if child.name == "p":
			for line in child:			
				parsedLine = lineRecogniser(line)
				if parsedLine is not None:
					if isinstance(parsedLine,list):
						if isinstance(parsedLine[0],list):
							# embedded list
							for x in parsedLine:
								out += x					
						else:
							out += parsedLine
					else:
						out.append(parsedLine)
						
		if child.name == "ul":
			choices = ulParser(child)
			#out.append({"CHOICE":choices})
			out.append(choices)

		if child.name == "div" and "optional" in child.get("class"):
			saveDialogue = ""
			for part in child:
				if part.name== "p":
					outx = []
					for line in part:
						# TODO: Some p tags have parts of npc spans as direct children
						parsedLine = lineRecogniser(line)
						if parsedLine is not None:
							#if it's a ul, then add it to the current outx as a choice
							if isinstance(parsedLine,list):
								if isinstance(parsedLine[0],list):
									# embedded list
									for x in parsedLine:
										outx += x					
								else:
									outx +=parsedLine
							else:
								outx.append(parsedLine)
							#if len(outx)>0 and "CHOICE" in outx[-1]:
							#	outx[-1]["CHOICE"][1].append({"CHOICE":parsedLine})
					if len(outx)>0:
						out.append({"CHOICE":[[],outx]})
				elif part.name=="div" and "tri" in part.get("class"):
					out.append({"ACTION":part.get_text()})
				else:
					# Could be ul
					parsedLine = lineRecogniser(part)
					if parsedLine is not None:
						if isinstance(parsedLine,list):
							if len(out)>0 and "CHOICE" in out[-1]:
								# TODO: List isn't always a choice
								out[-1]["CHOICE"][-1].append({"CHOICE":parsedLine})
							else:
								out += parsedLine
						else:
							out.append(parsedLine)
#					else:
					# Some optional tags have bits of character names and dialogue
					#   as direct children. So we need to go through each object
					#   and figure out what's going on
# 						txt = getTextFromUnknownObject(part).strip()
# 						print(txt)
# 						if txt.endswith(":"):  # It's a character name
# 							if len(saveDialogue)>0:
# 								out.append({cleanName(lastNPC):cleanDialogue(saveDialogue)})
# 								saveDialogue = ""
# 							lastNPC = txt[:txt.index(":")]
# 						elif txt.count(":")>0: # it's both char name and dialogue
# 							# first, finish adding any leftover dialogue from last char
# 							if len(saveDialogue)>0:
# 								out.append({cleanName(lastNPC):cleanDialogue(saveDialogue)})
# 								saveDialogue = ""
# 							cx = txt[:txt.index(":")].strip()
# 							if not lastNPC.startswith(cx):
# 								lastNPC = cx
# 							dx = txt[txt.index(":"):]
# 							if len(dx)>0:
# 								out.append({cleanName(cx):cleanDialogue(dx)})
# 						else: # It's a bit of dialogue spoken by the last mentioned char
# 							if len(txt)>0:
# 								saveDialogue += " " + txt

			

	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)



def postProcessing(out):
	finalOut = []
	for o in out:
		if not o is None and o!= {"slumped": "Seems to have been put to sleep."}:
			if isinstance(o,list):
				finalOut += o
			else:
# 				if "CHOICE" in o:
# 					cxout = []
# 					for cx in o["CHOICE"]:
# 						lines = []
# 						for cxx in cx:
# 							if isinstance(cx,list):
# 								lines += cxx
# 							else:
# 								lines.append(cxx)
# 						cxout.append(lines)
# 					finalOut.append({"CHOICE":cxout})
# 				else:
					finalOut.append(o)
	
#	o = open("../data/FinalFantasy/FFX_B/tmp.txt",'w')
#	o.write(json.dumps({"text":finalOut}))
#	o.close()
	
	return(finalOut)
		