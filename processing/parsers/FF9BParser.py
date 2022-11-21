from bs4 import BeautifulSoup, NavigableString
import json,re,copy,csv
from os.path import exists

# TODO

# In other places, dialogue will be compacted without that
# single-spaced portion, which denotes that it's either text
# said in unison, like this similar example:
# 
# Zidane: "Hey!"
# 
# Eiko: "What's crackin'?"
# Steiner: "You startled me!"
# 
# In addition to that context, NPC dialogue may have compact
# dialogue to show that the speaker says something new after
# the initial talk, like this example:
# 
# Soldier: "Sure is hot out here!"
# Soldier: "I wish it'd rain..."

# Real example, though this seems very rare
# Queen Brahne: &quot;Here, take this... And go find my daughter!&quot;
# Queen Brahne: &quot;Still no sign of Garnet?&quot;

# ----

# Currently, the parser does not code some possible player
#Ê choices that do not have dialogue consequences
#  see the lines with "can't find" below
#
# But this causes some problems e.g. the line of dialogue after R3 is 
# recorded, but not given its own choice
# 
# Mosh: &quot;Can I help you, kupo?&quot;
#       R1 --&gt; Save
#       R2 --&gt; Tent
#       R3 --&gt; Mognet
#       R4 --&gt; Cancel
#
#       R3 --&gt; &quot;I want mail! Kupo!&quot;

# ----


def parseFile(fileName,asJSON=False):

	def cleanLine(txt):
		txt = txt.replace("#","")
		txt = re.sub("\.\.\.([A-Za-z])","... \\1",txt)
		txt = re.sub("^:","",txt)
		txt = txt.replace("_"," ")
		txt = txt.replace('"',"")
		txt = txt.replace('\n'," ")
		txt = re.sub(" +"," ",txt)
		txt = txt.replace("\\","")
		txt = txt.replace("<","(")
		txt = txt.replace(">",")")
		txt = txt.replace("{","(")
		txt = txt.replace("}",")")
		# replace square brackets with round brackets
		txt = txt.replace("[","(").replace("]",")")
		txt = txt.strip()
		return(txt)
		
	def cleanCharName(txt):
		txt = txt.strip()
		return(txt)
		
	def parseLineupOption(part):
		choices = []
		bits = part.split("\n[")
		if len(bits)==1:
			bits = re.split("\n +\[",part)
		for bit in bits:
			bit = bit[bit.index("]")+1:]
			#print("8888")
			#print(bit)
			charName,dialogue = bit.split(":",1)
			charName = cleanCharName(charName)
			choices.append([{"STATUS": charName + " is in party"},
				 {charName: cleanLine(dialogue)}])
		return({"CHOICE": choices})
		
	def parseDecision(txt, decisionID="D1"):
		
		# Sometimes, there is no specified action for R1 and R2 
		#  (e.g. "Save", "Tent")
		
		if txt.count("R2 --> Tent")>0 and txt.count("R2:")==0:
			# find pace to first put 
			if txt.count("\n\n")>0:
				ix = txt.index("\n\n")
				txt = txt[:ix] + "\n\n     R2 (ACTION): Tent" + txt[ix:]
		
		if txt.count("R1 --> Save")>0 and txt.count("R1:")==0:
			# find pace to first put 
			if txt.count("\n\n")>0:
				ix = txt.index("\n\n")
				txt = txt[:ix] + "\n\n     R1 (ACTION): Save" + txt[ix:]
			

		# Divide parts
		#print("###")
		#print(txt)
		initialLine = txt[:txt.index("R1 -->")]
		p2SplitText = "R1:"
		p2 = ""
		p3 = ""
		
		# Sometimes first marker has brackets
		#  R1 (Dagger): "Yes
		if txt.count(p2SplitText)==0:
			p2SplitText = "R1 ("
		# Sometimes there is no R2 or R3
		if txt.count(p2SplitText)==0:
			p2SplitText = "R2:"
		if txt.count(p2SplitText)==0:
			p2SplitText = "R3:"
		if txt.count(p2SplitText)==0:
			# Raw choices without responses
			p2 = txt[txt.index("R1 -->"):]
		else:
			p2 = txt[txt.index("R1 -->"):txt.index(p2SplitText)]
			p3 = txt[txt.index(p2SplitText):]
		
		outx = []
		# Initial line
		xx = parseOrdinaryLine(initialLine)
		initiatingCharName, dialogue = initialLine.split(":",1)
		#outx.append({initiatingCharName: cleanLine(dialogue)})
		if len(xx)>0:
			outx += xx
		
		playerOptions = {}
		
		# parse initial options
		firstOptions = [x for x in p2.split("\n") if len(x.strip())>0]
		for op in firstOptions:
			if op.strip().startswith("NOTE") or op.count("-->")==0:
				outx.append({"ACTION":cleanLine(op)})
			else:
				opID, dial = [x.strip() for x in op.split("-->",1)]
				playerOptions[opID] = cleanLine(dial)
		
		# main body
		options = {}
		opIDList = []
		resps = re.split("\n *(R[1-9][0-9]?(?: \([A-Za-z ]+\))?:)","\n"+p3)
		resps = [x+y for x,y in zip(resps[1::2],resps[2::2])]
		
		
		for resp in resps:
			respBit = []
			
			xx = re.split("(R[0-9][0-9]?)",resp,1)
			opID = xx[1]
			rest = xx[2]
			opIDList.append(opID)
			
			respBit = []
			if opID in playerOptions:
				respBit.append({"ACTION": "Player chooses '"+playerOptions[opID]+"'"})
			
			rest = re.sub("\n[ \t]+\n","\n\n",rest).strip()

			# Work out first character to speak
			charName = initiatingCharName
			charName = cleanCharName(charName)
			# TODO: it might be an action line
			
			# Check to see if a character is specified
			if rest.startswith("(")>0:
				charName = rest[rest.index("(")+1:rest.index(")")].replace(")","").strip()
				charName = cleanCharName(charName)
				rest = rest[rest.index(")")+1:].strip()
			# First line of response
			firstLineOfResponse = rest
			if rest.count("\n\n")>0:
				firstLineOfResponse = rest[:rest.index("\n\n")]
				rest = rest[rest.index("\n\n"):]
			if firstLineOfResponse.count("-->"):
				firstArrow = firstLineOfResponse.index("-->")
				firstNewLineBeforeArrow = firstLineOfResponse[:firstArrow].rindex("\n")
				firstLineOfResponse = firstLineOfResponse[:firstNewLineBeforeArrow]
			firstLineOfResponse = cleanLine(firstLineOfResponse)
			if len(firstLineOfResponse)>0:
				respBit.append({charName: cleanLine(firstLineOfResponse),
							 "_ID": decisionID + ":" +opID})


			# Now look at other lines
			#sublines = re.split("\n +([A-Za-z]+):", rest)
			#sublines = [(cn,d) for cn,d in zip(sublines[::2],sublines[1::2])]
			
			# find links at end of resp
			links = re.findall("R[1-9][0-9]? -->.+?\n", rest+"\n")
			links = [x.strip() for x in links]
			rest = re.sub("R[1-9][0-9]? -->.+?\n","",rest+"\n")
			# Could be bare links after firstLineOfResponse, so remove
			if rest.count("\n")<=2:
				rest = ""
			
			
			
			# Responses can have multiple lines
			sublines = rest.split("\n\n")
			sublines = [x for x in sublines if len(x.strip())>0]
			for subline in sublines:
				#print("++++====")
				#print(subline)
				if subline.strip().startswith("["):
					if subline.strip().startswith("[-]"):
						# option
						subline = subline.replace("(","").replace(")","")
						respBit.append(parseLineupOption(subline))
					else:
						respBit.append({"ACTION": cleanLine(subline.replace("[","").replace("]",""))})
				else:
					#print("SSSSS")
					#print(subline)
					if subline.strip().startswith("-") or subline.count(":")==0:
						respBit.append({"SYSTEM": cleanLine(subline)})
					else:
						cn, dx = subline.split(":",1)
						cn = cleanCharName(cn)
						dx = dx.strip()
						if dx.startswith("["):
							# Action
							respBit.append({"ACTION": cleanLine(dx.replace("[","").replace("]",""))})
						else:
							if len(cn)>0:
								respBit.append({cn: cleanLine(dx)})
			# Add links to other responses	
			if len(links)>0:
				respBit.append(links)
			#for link in links:
			#	idx, optionText = [x.strip() for x in link.split("-->")]
			#	respBits.append((idx,optionText))
			options[opID] = respBit
		# Now we've got all the bits, put them together in a decision structure
		
		def parseResp(respBits):
			global seenIDs
			choiceBits = []
			for line in respBits:
				if not isinstance(line, list):
					# Ordinary line
					choiceBits.append(line)
				else:
					# list of links
					idsAndOptexts = [[x.strip() for x in y.split("-->")] for y in line]
					nextChoices = []
					for idx,opText in idsAndOptexts:						
						if idx in seenIDs:
							# We've seen this already, just goto
							nextChoices.append([
									{"Zidane": opText},
									{"GOTO": decisionID + ":" +idx}])
						else:
							# Embed
							if idx in options:
								embed = options[idx]
								seenIDs.append(idx)
								cx = parseResp(embed)
								# "Main character" here is the player option
								nextChoices.append([{"ACTION": "Player chooses '"+opText+"'"}]+cx)
							else:
								print("Can't find "+idx)
								print(line)
								# See if we can find a quote directly after a link
								lx = [x for x in line if x.count(idx)>0][0]
								if lx.count('"')>0:
									dlg = lx[lx.index(">")+1:].strip().replace('"',"")
									# This should really be a new choice, but this function
									#  doesn't have access to that level
									cx = parseResp([{"ACTION":idx},{charName:dlg}])
									nextChoices.append(cx)

					# If there's just one option, it's not really a choice
					if len(nextChoices)==1:
						choiceBits += (nextChoices[0])
					else:
						# Otherwise, return a choice
						choiceBits.append({"CHOICE":nextChoices})
			return(choiceBits)


		# Main parsing bit
		choices = []
		global seenIDs
		seenIDs = []
		for rID in opIDList:
			if not rID in seenIDs:
				seenIDs.append(rID)
				respBits = options[rID]
				choiceBits = parseResp(respBits)
				#print(choiceBits)
				choices.append(choiceBits)
		if len(choices)>0:
			outx.append({"CHOICE": choices})
		return(outx)
	
	def parseOrdinaryLine(part):
		outx = []
		bits = [part]
		if len(re.findall("\n.+?: ",part))>0:
			bits = re.split("(\n.+?:)",part.strip())
			bits = [bits[0]] + [x[0]+x[1] for x in zip(bits[1::2],bits[2::2])]
		for bit in bits:
			charName, dialogue = bit.split(":",1)
			charName = cleanCharName(charName)
			dialouge = cleanLine(dialogue)
			if len(dialogue)>0:
				outx.append({charName: cleanLine(dialogue)})
		return(outx)
		
		
################
### Main loop		
	o = open(fileName)
	d = o.read()
	o.close()
	

	#soup = BeautifulSoup(d, 'html.parser')
	# Parsing with html5lib so that p tags are closed
	soup = BeautifulSoup(d, "html5lib")
	script = soup.find('div', id='faqtext')
	
	script = script.getText()
	
	startCue = "01. Alexandria (AL01)"
	endCue = ".+--+--+--+--+--+--+--+--+"
	script = script[script.index(startCue):script.index(endCue)]
	
	# Take out mid-way index
	indStart = "    ######  # ###### #####      #     #"
	indEnd = "Back and forth in Pand. elev. room"
	script = script[:script.index(indStart)]+"\n"+script[script.index("\n",script.index(indEnd)):]
	
	script = script.replace("{They go to see the watchmen;","[They go to see the watchmen;")
	script = re.sub("####+","[Break]",script)
	
	script = script.replace("R5 --> Sure","R1 --> Sure")
	script = script.replace("R6 --> No Way","R2 --> No Way")
	script = script.replace('R5 --> "Thanks, kupo!" [He gives the letter.]','R1 --> "Thanks, kupo!" [He gives the letter.]')
	script = script.replace('R6 --> "I\'m so sad, kupo..." [He doesn\'t give the letter.]','R2 --> "I\'m so sad, kupo..." [He doesn\'t give the letter.]')

	fix1 = ''' Zidane: "Looks like the mayor isn't here..."
         R1 --> Check the room
         R2 --> Go outside

         R1: [See below.]
         R2: [Zidane leaves quietly.]

 [When Zidane chooses to look around:]

 Zidane: "Where should I check?"'''
	fix1b = """ Zidane: "Looks like the mayor isn't here..."
         R1 --> Check the room
         R2 --> Go outside

         R1 (Zidane): "Where should I check?"
               R3 --> Desk
               R4 --> Ladder
               R5 --> Heater
               R6 --> Shelf
               R7 --> Quit
         
         R2: [Zidane leaves quietly.] """

	script = script.replace(fix1,fix1b)
	
	fix3 = """R1 --> Save\n +R2 --> Tent\n +R3 --> Mognet\n +R4 --> Cancel"""
	fix3b = """R1 --> Save\n        R2 --> Tent\n        R3 --> Mognet\n        R4 --> Cancel\n\n        R1: [Save]\n\n        R2: [Tent]"""
	script = re.sub(fix3,fix3b,script)
	
	fix2 = """ [After R3 again:]\n\n Mogrika: "I have a favor to ask, kupo! I want you to deliver a
          letter to Moolan!"
          R5 --> "Thanks, kupo!" [She gives the letter.]
          R6 --> "I'm so sad, kupo..." [You receive the letter.]"""

	fix2b = """             [After R3 again:]\n\n            Mogrika: "I have a favor to ask, kupo! I want you to deliver a letter to Moolan!"
          R5 --> "Thanks, kupo!"
          R6 --> "I'm so sad, kupo..."
          
          R5: [She gives the letter.]
          
          R6: [You receive the letter.]"""
	script = script.replace(fix2,fix2b)
	script = script.replace('Mogrika: "I told Artemecion not to use it!"\n\n', 'Mogrika: "I told Artemecion not to use it!"\n    \n')
	
	script = script.replace('R3: "Wow, a visitor! Kupo! I need you to deliver', '\n      R1: [Save]\n\n       R2: [Tent]\n\n      R3: "Wow, a visitor! Kupo! I need you to deliver')
	
	script = script.replace("\n [He also says \"I haven't received any mail lately, kupo.\" when you\n inquire on R3 afterwards.]", "       R5 --> [Ask again]\n    R6 --> [Leave]\n\n       R5: \"I haven't received any mail lately, kupo.\"\n     R6: [Leave]")
	
	# separate action at end of dialogue 
	script = re.sub('(     +)([^\n]+?") (\[.+\])','\\1\\2\n\\1\\3\n\\1',script) 

	script = script.replace(' [After putting weights on the scales:]',"")
	script = script.replace(' Regent Cid: "Now what <ribbit>?"','            Regent Cid: "Now what <ribbit>?"')

	# Deal with folder format
#	script = script.replace('    ______','\n\nX    ______')
#	script = script.replace("\n____","\n\nX")
#	script = script.replace("\n ____","\n\nX")
#	# End of folder  - to help parsing of captions?
#	script = script.replace("____\n","____\n\n")
	script = re.sub("\n +__+\n ?_+/(.+?)\|","\n\n[\\1]\n\n", script)
	script = re.sub("\n ?_+\n\|(.+?)\__+", "\n\n[\\1]\n\n",script)
	
	script = script.replace("<A> Action Abilities:","<A> Action Abilities-")
	script = script.replace("<S> Support Abilities:","<S> Support Abilities-")
	
	script = script.replace("\"You need MP to use magic","SYSTEM: \"You need MP to use magic")
	
	# This inserts "GOTO" commands
	script = re.sub("\[(Same as R([1-9]).*?)\]", "\n   R\\2 --> (\\1)", script)
	#script = script.replace("\n____","\n\nX")
	
	# Colons confuse the parser
	script = script.replace("is why I travel:","is why I travel-")
	script = script.replace('Receive:','Receive')
	script = script.replace('Get:','Get')
	script = script.replace("think like this:","think like this - ")
	script = script.replace("la vista:","la vista- ")
	script = script.replace("mission:","mission -")
	script = script.replace("Then let me ask you this:","Then let me ask you this")
	script = script.replace("First Act: The End of Ugly","First Act- The End of Ugly")
	script = script.replace("That's all you humans ever think about:","That's all you humans ever think about,")
	script = script.replace("the Path of Souls:","the Path of Souls,")
	script = script.replace("And all you guys:","And all you guys,")
	script = script.replace("involved in this:","involved in this,")
	script = script.replace("World only have two things:","World only have two things,")
	
	script = script.replace('No --&gt; Current location: Bohden Station','')
	script = script.replace('{Yes/No}{Same as above}',"")
	script = script.replace("[A mage comes down and says its signature line.]",'Black Mage: "KILL!"')
	
	# Some response dialogue does not have two lines between character dialogue. 
	# Attempt to fix that:
	# see e.g. Zidane: &quot;We can't go that way! Here, let's try this way!&quot;
	script = re.sub("(\n            [^ ].+?)(\n            [A-Z\[])","\n\\1\n\\2",script)	
	
	# Letters
	#script = script.replace('\n         From','\n         SYSTEM: From')
	script = re.sub('\n( +)From','\n\\1SYSTEM: From',script)
	
	#script = script.replace("[Receive: Kupo Nut] \"I\n", "[Receive: Kupo Nut] \n                 \"I")
	
	script = script.replace("I''ve","I've")
	
	goblins1a = """Goblin?: "Rally-ho!"
Goblin?: "Rally-ho!"
Goblin?: "Rally-ho!\""""
	goblins1b = """Harold Pathknower: "Rally-ho!"
Jenny Greeter: "Rally-ho!"
Male Dwarf: "Rally-ho!\""""
	script = script.replace(goblins1a,goblins1b)

	goblins2a = """Goblin?: "Rally-ho!"
Goblin?: "Rally-ho!\""""	
	goblins2b = """Jenny Greeter: "Rally-ho!"
Male Dwarf: "Rally-ho!\""""
	script = script.replace(goblins2a,goblins2b)
	
	goblins3a = """Goblin?: "Rally-ho!\""""	
	goblins3b = """Harold Pathknower: "Rally-ho!"
Male Dwarf: "Rally-ho!\""""
	script = script.replace(goblins3a,goblins3b)
	
	goblins4a = """Villager: "Rally-ho's oor sacred greetin'!"

Villager: "If ye dinnae say Rally-Ho, then ye cannae enter Conde
          Petie, hametoon o' the dwarves!"

Zidane: "Now, wait just a minute here..."

Villager: "Rally-ho!"
Villager: "Rally-ho!\""""
	goblins4b = """Harold Pathknower: "Rally-ho's oor sacred greetin'!"

Jenny Greeter: "If ye dinnae say Rally-Ho, then ye cannae enter Conde
          Petie, hametoon o' the dwarves!"

Zidane: "Now, wait just a minute here..."

Harold Pathknower: "Rally-ho!"
Jenny Greeter: "Rally-ho!\""""
	script = script.replace(goblins4a, goblins4b)
	
	manx1 = """R2: [You can change your party. Afterwards, the Crewman
             will say: "Godspeed!"]"""
	manx2 = """R2: [You can change your party.] "Godspeed!\""""
	script = script.replace(manx1,manx2)
	
	script = script.replace("R1: - Chocobo Navigation -", "R1 (SYSTEM): - Chocobo Navigation -")
	script = script.replace("\n\n            (O)","\n            (O)")
	script = script.replace("\n\n            [SELECT]","\n            [SELECT]")
	script = script.replace("\n\n            [L1][R1]","\n            [L1][R1]")
	script = script.replace("\n\n            [L2]","\n            [L2]")
	
	script = script.replace("""[A mage outside yells: "The humans are here!"]""","""Friendly Black Mage: "The humans are here!\"""")

	# Split identical lines
	script = script.replace('\nWatchman: "Stop, thief!"','\nMatthew Watchman: "Stop, thief!"', 1)
	script = script.replace('\nWatchman: "Stop, thief!"','\nRichard Watchman: "Stop, thief!"', 1)
	
	script = script.replace(' Oracle: "Aaaa!"\n Oracle: "Aaaa!"',' Flower Maiden Sharon: "Aaaa!"\n Water Maiden Shannon: "Aaaa!"')
	
	script = script.replace("  (Lisa)","\n      Lisa")
	script = script.replace("same thing these days:","same thing these days-")
	script = script.replace("Hint: ","Hint- ")
	
	# Moogle name fixes
	
	mn1a = """ Eiko: "Go, _______!

 Chosen Moogle: "Kupo!"

 Eiko: "Who should dig up potatoes?" {Options = unchosen moogles}

 [Eiko makes her choices.]

 Eiko: "Go, ______!"

 Chosen Moogle: "Kupo!"

 Eiko: "______, you help me in the kitchen.\""""
	mn1b = """ Eiko: "Go, Momatose!

 Momatose: "Kupo!"

 Eiko: "Who should dig up potatoes?" {Options = unchosen moogles}

 [Eiko makes her choices.]

 Eiko: "Go, Mocha!"

 Mocha: "Kupo!"

 Eiko: "Chimomo, you help me in the kitchen.\""""
	
	script = script.replace(mn1a,mn1b)
	
	mn2a = """      all the people I listed? I'll get the ingredients."

 Moogle: "Kupo!\""""
	mn2b = """      all the people I listed? I'll get the ingredients."

 Chimomo: "Kupo!\"""" 
	script = script.replace(mn2a,mn2b)
	
	mn3a = """      R1: "______! Let go of that one and catch another one!"

           Moogle: "Kupo!\""""
	mn3b = """      R1: "Momatose! Let go of that one and catch another one!"

           Momatose: "Kupo!\""""
	script = script.replace(mn3a,mn3b)
	
	mn4a = """Moogle: "Kupo!"

 Mogrich: "W-We're really good friends! Can I help you, kupo?\""""
	mn4b = """Mogrich: "Kupo!"

 Mogrich: "W-We're really good friends! Can I help you, kupo?\""""
	script = script.replace(mn4a,mn4b)
	
	rx1a = """ Narrative: Choose option.

            R1 --> Save

            R2 --> Tent

            R3 --> Select party members

            R4 --> Cancel"""
	rx1b = """ Narrative: Choose option- Save, Tent, Select Party Members, Cancel."""
	script = script.replace(rx1a, rx1b)
	
	script = script.replace('R3 --> "There\'s a letter for Zidane!"','R3: "There\'s a letter for Zidane!"')
	script = script.replace('R5 --> "A letter from Kupo?','R5: "A letter from Kupo?')
	script = script.replace('R3 --> "Hey, you gotta deliver a letter', 'R3: "Hey, you gotta deliver a letter')
	script = script.replace('R3 --> "What do you want to do?','R3: "What do you want to do?')
	script = script.replace('R5 --> "A letter from Kupo?','R5: "A letter from Kupo?')
	script = script.replace('R6 --> "I want mail! Kupo!','R6: "I want mail! Kupo!')
	script = re.sub('R([1-9]) --> "', 'R\\1: "',script)
	script = script.replace("R6 --> How Ya Doin'?","R6: \"How Ya Doin'?")
	
	
	open("../data/FinalFantasy/FFIX_B/raw/tmp.txt",'w').write(script)
	
	parts = re.split("\n\n ?([A-Za-z\[=\?])",script)
	parts = parts[1:]
	
	parts = [x+y for x,y in zip(parts[::2],parts[1::2])]

	out = []
	choices = []
	choiceIDCounter = 0

	for part in parts:
		
		if part.startswith("====="):
			#ÊLocation
			part = part.replace("_","").replace("=","")
			part = re.sub("--+","",part)
			part = re.sub("\[.+?\]","",part).strip()
			out.append({"LOCATION": part})
		elif part.count("__________________")>0:
			# Parse a "Folder" section
			#print(part)
			#print("*****")
			caption = [x for x in part.split("\n") if x.count("|")>0]
			if len(caption)>0:
				caption = caption[0]
				caption = caption.replace("_","").replace("/","").replace("|","").replace("\\","")
				if len(caption)>0:
					part = part[part.index(caption)+len(caption)+1:].replace("_","").replace("|","").replace("\\","")
					if len(part.strip())>0:
						if len(re.findall("  +R[0-9][0-9]? *-->", part))>0:
							# decision
							choiceIDCounter += 1
							dec = parseDecision(part,"D"+str(choiceIDCounter))
							if len(dec)>0:
								out += dec
						else:
							lxx = parseOrdinaryLine(part)
							if len(lxx)>0:
								out += lxx
		elif part.startswith("["):
			# Probably an action, with two exceptions:
			if part.startswith("[*]"):
#                 [*]   Denotes speech that will always be said  
#                       if the character is in the party.  
				bits = part.split("\n[")
				for bit in bits:
					bit = bit[bit.index("]")+1:]
					charName,dialogue = bit.split(":",1)
					charName = cleanCharName(charName)
					out.append({"CHOICE": [
						[{"STATUS": charName + " is in party"},
						 {charName: cleanLine(dialogue)}],
						 []
					]})
			if part.startswith("[-]"):
#				  [-] Denotes speech that can be said by a     
#                		party member, but depends on the party's 
#		                lineup. Although there may be many who   
#       		        can say a line here, only one actually will
				out.append(parseLineupOption(part))
			else:
				# Plain action description
				part = part.replace("[","").replace("]","")
				out.append({"ACTION": cleanLine(part)})
		elif part.count("_______________")>0:
			part = part[1:].strip()
			part = re.sub("[^A-Za-z \.0-9,:;?\[\]]","",part)
			part = re.sub(" +"," ",part)
			if len(part)>0:
				out.append({"LOCATION": part})
		elif part.count(":")>0 and part.index(":")< 30:
			# dialogue
			# TODO: Main character monologue in parentheses
			
			if len(re.findall("  +R[0-9][0-9]? *-->", part))>0:
				# decision
				choiceIDCounter += 1
				dec = parseDecision(part,"D"+str(choiceIDCounter))
				if len(dec)>0:
					out += dec
			else:
				lxx = parseOrdinaryLine(part)
				if len(lxx)>0:
					out += lxx
			

	return(out)

#---

def postProcessing(out):

# "Same as" - conversations are copied to other characters
# Card Freak Gon: [Same as LB91]
#ÊNeed to log all of these and re-use
	
	dx = {}
	currLoc = ""
	for line in out:
		mainKey = [x for x in line if not x.startswith("_")][0]
		if mainKey!="CHOICE":
			if mainKey == "ACTION":
				if "--" in line[mainKey]:
					currLoc = line[mainKey][:line[mainKey].index(" ",1)].strip()
			else:
				dx[(currLoc,mainKey)] = line
	out2 = []	
	for line in out:
		mainKey = [x for x in line if not x.startswith("_")][0]
		if mainKey!="CHOICE":
			dialogue = line[mainKey]
			dialouge = dialogue.replace(" as in", " as")
			if dialogue.count("(Same as")>0:
				kstart = dialogue.index("(Same as")+9
				k = dialogue[kstart:].strip()
				if " " in k:
					k = k[:k.index(" ")].strip()
				if "." in k:
					k = k[:k.index(".")].strip()
				if ")" in k:
					k = k[:k.index(")")].strip()
				if len(k)==4:
					if (k,mainKey) in dx:
						#print(k)
						line = dx[(k,mainKey)]			
		out2.append(line)

	# Identify whispers versus action text	
	whisperFile = "../data/FinalFantasy/FFIX_B/whispers.csv"
	
	nonWhisperLines = [
		"(Options = unchosen moogles)",
		"(The Pointy-hat boy leaves.)",
		"(The Blank scene that takes place afterwards starts immediately with this option.)",
		"(The fight starts.)",
		"(She shows her wares.)",
		"(Said if you haven't talked to Vivi yet.)",
		"(Zidane and Dagger go down.)",
		"(Hatch is closed, unentered.)",
		"(They head back to the village, etc.)",
		"(Garnet kicks him through the bag.)",
		"(Garnet kicks him; dialogue cancelled.)",
		"(Steiner runs to the other side, past Dagger.)",
		"(Zidane follows them into the next screen, safely.)",
		"(They head to the right bridge.)",
		"(d-left)",
		"(d-right)",
		"(The fireplace pulls back to reveal a stairway.)",
		"(No action taken.)",
		"(You do the entire procedure over again.)",
		"(They jump off; see below.)",
		"(They can run back into the forest.)",
		"(Zidane pokes it.)",
		"(Zidane kicks recklessly.)",
		"(Inside, Lani holds a flailing Eiko by the back of her dress.)",
		"(Zidane can walk around again.)",
		"(Zidane can change party members.)",
		"(The menu opens.)",
		"(The process is completed; Zidane can run in, now.)",
		"(Party select screen opens.)",
		"(Menu opens.)",
		"(She chases him.)",
		"(You'll have to try again.)",
		"(Says this without any stimulus.)",
		"(P.S. -- This is Blank, which is he's no title given to him. ;)",
		"(Get Elixir)",
		"(You can't speak with him for some reason.)",
		"(She only sells potions.)",
		"(Doesn't look in.)",
		"(She sells items.)",
		"(She sells items.)",
		"(They stay and rest up.)",
		"(Hal goes back to sleep.)",
		"(Says same thing.)",
		"(Letter is received.)",
		"(Letter isn't received.)",
		"(Zidane opens the door and is attacked by 2 Ghosts.)",
		"(Zidane doesn't open the door.)",
		"(Letter is received.)",
		"(Letter isn't received.)",
		"(Zidane stays.)",
		"(Zidane doesn't stay.)",
		"(She sells items.)",
		"(You can synth items, then.)",
		"(She runs off down the street.)",
		"(Is no longer here.)",
		"(No dialogue; right to buy/sell screen.)",
		"(No dialogue; right to buy/sell screen.)",
		"(Isn't here any longer.)",
		"(Mogster can go over the tutorial options again.)",
		"(Dialogue is cancelled.)",
		"(S/he joins up permanently.)",
		"(The game starts.)",
		"(Zidane can buy Gysahl Greens, 80gil/per)",
		"(Current Funds: )",
		"(Garnet kicks Steiner through the bag.)",
		"(Repeats this phrase.)",
		"(Garnet boards.)",
		"(Zidane moves Kal out from underneath a statue, before it falls.)",
		"(A Burmecian soldier runs in.)",
		"(The three Burmecians flee.)",
		"(Letter is given.)",
		"(Letter isn't given to Zidane.)",
		"(Can buy/sell items and such from the moogle! =o)",
		"(They stay; no dialogue spoken.)",
		"(Steiner penny-pinches and doesn't contribute.)",
		"(Rest ensues.)",
		"(The thief runs off.)",
		"(She gets the Stellazzio.)",
		"(The scene plays out again like she told Marcus she needed more time to get ready.)",
		"(No actions taken.)",
		"(Sand stops flowing one way, and goes the other.)",
		"(No actions are taken.)",
		"(Weapon buy/sell screen opens up.)",
		"(Equip. shop opens)",
		"(Equipment shop opens up.)",
		"(No dialogue spoken)",
		"(The fight against Tantarian ensues.)",
		"(Actions are cancelled.)",
		"(No longer in this screen.)",
		"(Lowell runs off, with the starstruck soldier chasing after him.)",
		"(Zidane can excavate stuff.)",
		"(The wall collapses and a moogle is (thrown out.)",
		"(You quit digging.)",
		"(You keep digging.)",
		"(The party sleeps.)",
		"(She also says this after you've slept in the inn.)",
		"(Weapons buy/sell reluctantly opens.)",
		"(Dagger leaves.)",
		"(Actions cancelled.)",
		"(You get the stone as a Key Item.)",
		"(You don't do anything.)",
		"(Get Moonstone)",
		"(Quina walks on a high wall.)",
		"(Quina jumps into the water stream.)",
		"(The ATE 'Eiko's Feelings' plays.)",
		"(Last three kupos repeated on any further attempts to get in kitchen.)",
		"(Party switch-out screen opens up.)",
		"(She repeats the option Vivi picked.)",
		"(You get Hippaul's Shiva and Ramuh cards.)",
		"(You go back down the ladder.)",
		"(Zidane gets the key item Burman Coffee!)",
		"(Zidane takes no action.)",
		"(Zidane receives: Mini-Brahne)",
		"(Zidane gets a Mayor's Key)",
		"(Zidane leaves)",
		"(Zidane leaves quietly.)",
		"(And then:)",
		"(An ATE (The Rally) automatically plays.)",
		"(Five little rat kids run over.)",
		"(They all say this.)",
		"(Not in screen any longer.)",
		"(Not in screen any longer.)",
		"(Blue Narciss disembarks.)",
		"(No actions are taken.)",
		"(Said when you leave.)",
		"(Current funds: )",
		"(She repeats the last line on subsequent talks.)",
		"(Zidane dives off w/ Choco and into the foam below, finding the treasure beneath the waves)",
		"(This one results in failure)",
		"(This one results in failure)",
		"(This one results in failure)",
		"(The regent can remove weights.)",
		"(If the Regent can't make it up:)",
		"(If you inspect it, Receive Promist Ring)",
		"(If you inspect it, Receive Anklet)",
		"(Y/N} (If you inspect it, Receive Shield Armor)",
		"(If you inspect it, Receive N-Kai Armlet)",
		"(Y/N} (If you inspect it, Receive Venetia Shield)",
		"(If you look at the bloodstone, Receive Black Hood)",
		"(Leave)",
		"(Said after giving him K. Nut.)",
		"(Said upon leaving the shop.)",
		"(She gives the letter.)",
		"(You receive the letter.)",
		"(Said after party ranks have been seen.)",
		"(Yes = Go to W. Map)",
		"(Zidane can make Aquamarines out of the Ore)",
		"(Rank assessment again)",
		"(If he inspects the bar next:)",
		"(The lift now goes up to the third floor.)",
		"(Can only cue this conversation (after you've inspected the ? by the balcony.)",
		"(After pushing it)",
		"(Eiko can jump rope.)",
		"(After missing a jump.)",
		"(PS - This is a moogle)",
		"(Nothing new + I haven't received any mail lately, kupo.)",
		"(Party stays.)",
		"(Zidane walks away)",
		"(Allows option R3 to be used)",
		"(Zidane pushes on the relief; option R4 opens.)",
		"(Zidane pounds on it; Option R5 opens)",
		"(Zidane kicks the wall; R6 becomes Kick from now on; R7 opens)",
		"(The mural twists open)",
		"(This opens a new stairway in the first room in Ipsen's Castle)",
		"(You can change your party.)",
		"(Said after giving him K. Nut.)",
		"(Nothing said.)",
		"(Can't speak with her; resting)",
		"(Amarant joins the party.)",
		"(Said after giving him K. Nut.)",
		"(Letter you no get-y)",
		"(List of 4 party members + Cancel)",
		"(Win: Circlet)",
		"(You don't get the Stellazio back.)",
		"(The two run off, passing Zidane.)",
		"(Quina imagines a gigantic feast around.)",
		"(S/he heads to balcony)",
		"(Fight w/ Hades initiates)"
	]
	
	def walkWhisper(outx):
		for line in outx:
			k = [x for x in line if not x.startswith("_")][0]
			if "CHOICE" in line:
				for choice in line["CHOICE"]:
					for res in walkWhisper(choice):
						yield res
			else:
				if not k in ["ACTION","SYSTEM","LOCATION"]:
					dlg = line[k]
					if "(" in dlg:
						for w in re.findall("\(.+?\)",dlg):
							if any([w.startswith(x) for x in ["(Save)","(Tent)","(Same","(Receive","(Dialogue cancelled","(See","(Buy","(+","(Cancel","(Explained","(He doesn't give you the letter",'(He gives you the letter',"(You don't get the letter","(You get the letter",'(He ','(note)','(SELECT)','(START)',"(Synth","(Item"]]):
								# No change
								pass
							elif w in nonWhisperLines:
								# No change
								pass
							elif dlg.lower().count("kweh")>0:
								# Chocobo translation, no change
								pass
							#elif any([w.count(x)>0 for x in ["...","Umm","Okay","Aww","Wow","Ahh"]]) or w.startswith("(I "):
							else:
								# This is dialogue
								dlg2 = dlg.replace(w,w.replace("(","").replace(")",""))
								line[k] = dlg2
								line["_WHISPER"] = dlg
								if len(w)>4:
									yield (k,dlg,w)

	whispers = [x for x in walkWhisper(out2)]
	if not exists(whisperFile):
		with open(whisperFile, 'w') as csvfile:
			csvwriter = csv.writer(csvfile)
			for charName,dlg,w in whispers:
				csvwriter.writerow([charName,dlg,w])
	
	manualFixes = [
		({"Aviator": "Board the Invincible? Board, then go to the bridge/ Board, then go to the world map/Don't board", "_WHISPER": "Board the Invincible? (Board, then go to the bridge/ Board, then go to the world map/Don't board)"},
			[{"Aviator": "Board the Invincible?", "_CHOICES": "(Board, then go to the bridge/ Board, then go to the world map/Don't board)"}]),

		({"Crew Member": "Would you like to change your party members? Y/N", "_WHISPER": "Would you like to change your party members? (Y/N)"},
			[{"Crew Member (Sailor)": "Would you like to change your party members?", "_CHOICES": "Y/N"},
			{"CHOICE":[[{"Zidane": "Yes"}],[{"Zidane": "No"}]]}]),

		({"Mozme": "Danger ahead, kupo! Do you still want to go on, kupo? Y/N", "_WHISPER": "Danger ahead, kupo! Do you still want to go on, kupo? (Y/N)"},
			[{"Mozme": "Danger ahead, kupo! Do you still want to go on, kupo?", "_CHOICES": "Y/N"},
			 {"CHOICE":[[{"Zidane": "Yes"}],[{"Zidane": "No"}]]}]),
		({"Alexandrian Soldier": "Would you like to go to the harbor? Y/N", "_WHISPER": "Would you like to go to the harbor? (Y/N)"},
			[{"Alexandrian Soldier": "Would you like to go to the harbor?", "_CHOICES": "Y/N"},
			{"CHOICE":[[{"Zidane": "Yes"}],[{"Zidane": "No"}]]}]),
		({"Alexandrian Soldier": "Would you like to go to the castle? Y/N", "_WHISPER": "Would you like to go to the castle? (Y/N)"},
			[{"Alexandrian Soldier": "Would you like to go to the castle?", "_CHOICES": "Y/N"},
			{"CHOICE":[[{"Zidane": "Yes"}],[{"Zidane": "No"}]]}]),
		({"Slai's Father": "We're not usually open during the day. He's a special case. Do you need medicine? Y/N", "_WHISPER": "We're not usually open during the day. He's a special case. Do you need medicine? (Y/N)"},
			[{"Slai's Father": "We're not usually open during the day. He's a special case. Do you need medicine?", "_CHOICES": "Y/N"},
			{"CHOICE":[[{"Zidane": "Yes"}],[{"Zidane": "No"}]]}]),
		({"Bishop": "Welcome to Esto Gaza. The stars are the source of all life. We receive life from the stars and live our lives with them. This is the one place holy enough to worship the Path of Souls, the way of the Shimmering Island. Pilgrims come from afar to follow the Path of Souls. But you see... Soon after the black mages came, terrible monsters appeared here. Thanks to them, very few people come to visit nowadays. Would you care to rest here for 100 Gil? Y/N (He repeats dialogue from Thanks to... on subsequent talks.)", "_WHISPER": "Welcome to Esto Gaza. The stars are the source of all life. We receive life from the stars and live our lives with them. This is the one place holy enough to worship the Path of Souls, the way of the Shimmering Island. Pilgrims come from afar to follow the Path of Souls. But you see... Soon after the black mages came, terrible monsters appeared here. Thanks to them, very few people come to visit nowadays. Would you care to rest here for 100 Gil? (Y/N) (He repeats dialogue from Thanks to... on subsequent talks.)"},
			[{"Bishop": "Welcome to Esto Gaza. The stars are the source of all life. We receive life from the stars and live our lives with them. This is the one place holy enough to worship the Path of Souls, the way of the Shimmering Island. Pilgrims come from afar to follow the Path of Souls. But you see... Soon after the black mages came, terrible monsters appeared here. Thanks to them, very few people come to visit nowadays. Would you care to rest here for 100 Gil?", "_CHOICES": "Y/N"},
 			 {"CHOICE":[[{"Zidane": "Yes"}],[{"Zidane": "No"}]]}, 
			 {"ACTION": "(He repeats dialogue from Thanks to... on subsequent talks.)"}]),
		({"Bishop": "Welcome to Esto Gaza. The stars are the source of all life. We receive life from the stars and live our lives with them. This is the one place holy enough to worship the Path of Souls; the way of the Shimmering Island. Would you care to rest here for 100 Gil? Yes/No", "_WHISPER": "Welcome to Esto Gaza. The stars are the source of all life. We receive life from the stars and live our lives with them. This is the one place holy enough to worship the Path of Souls; the way of the Shimmering Island. Would you care to rest here for 100 Gil? (Yes/No)"},
			[{"Bishop": "Welcome to Esto Gaza. The stars are the source of all life. We receive life from the stars and live our lives with them. This is the one place holy enough to worship the Path of Souls; the way of the Shimmering Island. Would you care to rest here for 100 Gil?", "_CHOICES": "Yes/No"},
		 {"CHOICE":[[{"Zidane": "Yes"}],[{"Zidane": "No"}]]}]),
			({"Erin": "Do you have a new destination? Y/N (Yes = Go to W. Map)", "_WHISPER": "Do you have a new destination? (Y/N) (Yes = Go to W. Map)"},
		[{"Erin": "Do you have a new destination?", "_CHOICES": "Y/N (Yes = Go to W. Map)"},
		 {"CHOICE":[[{"Zidane": "Yes"},{"ACTION":"Go to W. Map"}],[{"Zidane": "No"}]]}]),
		({"Fish Man": "It's 100 per night. Will you be staying? Y/N", "_WHISPER": "It's 100 per night. Will you be staying? (Y/N)"},
			[{"Fish Man": "It's 100 per night. Will you be staying?", "_CHOICES": "Y/N"},
			{"CHOICE":[[{"Zidane": "Yes"}],[{"Zidane": "No"}]]}]),
		({"Freya": "Do you wish to rest, too, Zidane? Y/N", "_WHISPER": "Do you wish to rest, too, Zidane? (Y/N)"},
			[{"Freya": "Do you wish to rest, too, Zidane?", "_CHOICES": "Y/N"},
			{"CHOICE":[[{"Zidane": "Yes"}],[{"Zidane": "No"}]]}]),
		({"Librarian": "Grandpa Kukuro is really getting forgetful these days... This is the reading room. In addition to tables and chairs, we also have hammocks for people who fall asleep while they are reading. Would you like to stay here for 100 Gil? Y/N", "_WHISPER": "Grandpa Kukuro is really getting forgetful these days... This is the reading room. In addition to tables and chairs, we also have hammocks for people who fall asleep while they are reading. Would you like to stay here for 100 Gil? (Y/N)"},
			[{"Librarian": "Grandpa Kukuro is really getting forgetful these days... This is the reading room. In addition to tables and chairs, we also have hammocks for people who fall asleep while they are reading. Would you like to stay here for 100 Gil?", "_CHOICES": "Y/N"},
			{"CHOICE":[[{"Zidane": "Yes"}],[{"Zidane": "No"}]]}]),
		({"Librarian": "This is the reading room. In addition to tables and chairs, we also have hammocks for people who fall asleep while they are reading. Would you like to rest here for 100 Gil? Yes/No", "_WHISPER": "This is the reading room. In addition to tables and chairs, we also have hammocks for people who fall asleep while they are reading. Would you like to rest here for 100 Gil? (Yes/No)"},
			[{"Librarian": "This is the reading room. In addition to tables and chairs, we also have hammocks for people who fall asleep while they are reading. Would you like to rest here for 100 Gil?", "_CHOICES": "Yes/No"},
			{"CHOICE":[[{"Zidane": "Yes"}],[{"Zidane": "No"}]]}]),
		({"Eiko": "...... That sounds good! Okay, our menu is rock-fisted potato stew and barbecued fish! Let's see... Who should do the fishing? Chimomo/Mocha/Momatose", "_WHISPER": "...... That sounds good! Okay, our menu is rock-fisted potato stew and barbecued fish! Let's see... Who should do the fishing? (Chimomo/Mocha/Momatose)"},
			[{"Eiko": "...... That sounds good! Okay, our menu is rock-fisted potato stew and barbecued fish! Let's see... Who should do the fishing?", "_CHOICES": "Chimomo/Mocha/Momatose"},
			{"CHOICE":[[{"Zidane": "Chimomo"}],[{"Zidane": "Mocha"}],[{"Zidane": "Momatose"}]]}]),
		({"Moogle": "people! Kupo! Pour Water / Think Again", "_WHISPER": "people! Kupo! (Pour Water / Think Again)"},
			[{"Moogle": "Two people! Kupo!", "_CHOICE": "Pour Water / Think Again"}]),
		({"Eiko": "Potato, potato (note) Pumpkin bomb (note) Lots and lots of nuts (note) Should I put in that oglop I found on the Conde Petie Mountain Path? Yes/No", "_WHISPER": "Potato, potato (note) Pumpkin bomb (note) Lots and lots of nuts (note) Should I put in that oglop I found on the Conde Petie Mountain Path? (Yes/No)"},
			[{"Eiko": "Potato, potato (note) Pumpkin bomb (note) Lots and lots of nuts (note) Should I put in that oglop I found on the Conde Petie Mountain Path?", "_CHOICE": "Yes/No"},
			 {"CHOICE":[[{"Zidane": "Yes"}],[{"Zidane": "No"}]]}]),
		({"Dutiful Daughter Slai": "I'm sorry, we're not open during the day. Or do you need medicine? Yes/No", "_WHISPER": "I'm sorry, we're not open during the day. Or do you need medicine? (Yes/No)"},
			[{"Dutiful Daughter Slai": "I'm sorry, we're not open during the day. Or do you need medicine?", "_CHOICES": "Yes/No"},
			 {"CHOICE":[[{"Zidane": "Yes"}],[{"Zidane": "No"}]]}]),
		({"Night Oracle Donnegan": "We have rooms for 100 Gil. Would you like to stay? Yes/No", "_WHISPER": "We have rooms for 100 Gil. Would you like to stay? (Yes/No)"},
			[{"Night Oracle Donnegan": "We have rooms for 100 Gil. Would you like to stay?", "_CHOICE": "Yes/No"},
			{"CHOICE":[[{"Zidane": "Yes"}],[{"Zidane": "No"}]]}]),
		({"Zidane": "What now? Jump Down/Stay here", "_WHISPER": "What now? (Jump Down/Stay here)"},
			[{"Zidane": "What now?", "_CHOICES": "Jump Down/Stay here"}]),
		({"Night Oracle Donnegan": "You may rest here. You need pay me nothing. Thanks!/No Thanks!", "_WHISPER": "You may rest here. You need pay me nothing. (Thanks!/No Thanks!)"},
			[{"Night Oracle Donnegan": "You may rest here. You need pay me nothing.", "_CHOICES": "Thanks!/No Thanks!"},
			{"CHOICE":[[{"Zidane": "Thanks!"}],[{"Zidane": "No Thanks!"}]]}]),
		({"Innkeeper": "It's 100 Gil per night. Do you wanna stay here? Yes/No", "_WHISPER": "It's 100 Gil per night. Do you wanna stay here? (Yes/No)"},
			[{"Innkeeper": "It's 100 Gil per night. Do you wanna stay here?", "_CHOICES": "Yes/No"},
			{"CHOICE":[[{"Zidane": "Yes"}],[{"Zidane": "No"}]]}]),
		({"Momatose": "Why don't you get some rest? It'll be good for you. Kupo! Rest/Don't Rest", "_WHISPER": "Why don't you get some rest? It'll be good for you. Kupo! (Rest/Don't Rest)"},
			[{"Momatose": "Why don't you get some rest? It'll be good for you. Kupo!", "_WHISPER": "Rest/Don't Rest"}]),
		({"ACTION": "Scarlet Hair will say a few things during battle w/ Zidane: Here I go! You're too slow! Ugh! Can't you predict when I'll attack?"},
		[{"ACTION": "Scarlet Hair will say a few things during battle w/ Zidane:"},
		  {"Scarlet Hair": "Here I go! You're too slow! Ugh! Can't you predict when I'll attack?"}]),
		({"Momatose": "Thanks for saving Eiko, kupo! Why don't you get some rest? It'll be good for you. Kupo! Rest/Don't Rest", "_WHISPER": "Thanks for saving Eiko, kupo! Why don't you get some rest? It'll be good for you. Kupo! (Rest/Don't Rest)"},
			[{"Momatose": "Thanks for saving Eiko, kupo! Why don't you get some rest? It'll be good for you. Kupo!", "_CHOICES": "Rest/Don't Rest"}]),
		({"Hippolady": "My husband can't run a business to save his life, so I'm training my son, Hippaul, early. It's 120 Gil per night. Stay/Don't Stay", "_WHISPER": "My husband can't run a business to save his life, so I'm training my son, Hippaul, early. It's 120 Gil per night. (Stay/Don't Stay)"},
			[{"Hippolady": "My husband can't run a business to save his life, so I'm training my son, Hippaul, early. It's 120 Gil per night.", "_CHOICES": "Stay/Don't Stay"}]),
		({"Soldier on Gondola": "Go to the castle? Yes/No", "_WHISPER": "Go to the castle? (Yes/No)"},
			[{"Soldier on Gondola": "Go to the castle?", "_CHOICES": "Yes/No"},
			 {"CHOICE":[[{"Zidane": "Yes"}],[{"Zidane": "No"}]]}]),
		({"Soldier on Gondola": "Would you like to go into town? Yes/No", "_WHISPER": "Would you like to go into town? (Yes/No)"},
			[{"Soldier on Gondola": "Would you like to go into town?", "_CHOICES": "Yes/No"},
			{"CHOICE":[[{"Zidane": "Yes"}],[{"Zidane": "No"}]]}]),
		({"Zidane": "I'm gonna need the key to open this up... It says Mayor's Key here. Open/Don't Open", "_WHISPER": "I'm gonna need the key to open this up... It says Mayor's Key here. (Open/Don't Open)"},
			[{"Zidane": "I'm gonna need the key to open this up... It says Mayor's Key here.", "_CHOICES": "Open/Don't Open"}]),
		({"Regent Cid": "Do you want to change your party? Yes/No", "_WHISPER": "Do you want to change your party? (Yes/No)"},
			[{"Cid": "Do you want to change your party?", "_CHOICES": "Yes/No"},
			{"CHOICE":[[{"Zidane": "Yes"}],[{"Zidane": "No"}]]}]),
		({"Zidane": "This ladder feels kinda damp... Go down/Forget it", "_WHISPER": "This ladder feels kinda damp... (Go down/Forget it)"},
			[{"Zidane": "This ladder feels kinda damp...", "_CHOICES": "Go down/Forget it"}]),
		({"Momatose": "Wanna sleep? It feels so good! Kupo! Rest/Don't rest", "_WHISPER": "Wanna sleep? It feels so good! Kupo! (Rest/Don't rest)"},
			[{"Momatose": "Wanna sleep? It feels so good! Kupo!", "_CHOICES": "Rest/Don't rest"}]),
		({"Zidane": "How did you two meet? Ask/Don't Ask", "_WHISPER": "How did you two meet? (Ask/Don't Ask)"},
			[{"CHOICE":[[{"Zidane": "How did you two meet?"},{"Jobless Jeff": "She seemed different from the others when I first met her. I had no job at the time, so I decided to help run the South Gate shop. Then the Mist cleared, and I couldn't get back because the cable card had stopped! So, I ended up staying with her longer than I had expected. Now I can't imagine living without her. I'm so glad the Mist cleared. I'm with a wonderful woman because of it."}],[{"ACTION": "Don't ask"}]]}]),
		({"ACTION": "If Zidane asks:"},[]),
		({"Part-time Worker Jeff": "She seemed different from the others when I first met her. I had no job at the time, so I decided to help run the South Gate shop. Then the Mist cleared, and I couldn't get back because the cable card had stopped! So, I ended up staying with her longer than I had expected. Now I can't imagine living without her. I'm so glad the Mist cleared. I'm with a wonderful woman because of it."},[{"ACTION":"NONE"}]),
		({"ACTION": "R2: No, I won't force it out of you."},[{"Freya": "No, I won't force it out of you."}]),
		({"ACTION": "Amarant: ......"}, [{"Amarant": " ......"}])
	]	
	
	
# 					{"Kupo": "Save, kupo? Save/Don't Save", "_ID": "D67:R1", "_WHISPER": "Save, kupo? (Save/Don't Save)"}],
# 				[
# 					{"ACTION": "Player chooses 'Tent'"},
# 					{"Kupo": "Rest inside a tent, kupo? Rest/Don't Rest", "_ID": "D67:R2", "_WHISPER": "Rest inside a tent, kupo? (Rest/Don't Rest)"}],
	out3 = []
#	found= []
	for i in range(len(out2)):
		line = out2[i]
		foundFix = False
		for targ,fix in manualFixes:
			if line == targ:
				#found.append(targ)
				out3 += fix
				foundFix = True
				break
		if not foundFix:
			out3.append(line)
			
	out4 = []
	for line in out3:
		k = [x for x in line if not x.startswith("_")][0]
		dlg = line[k]
		if k== "ACTION" and re.match("[A-Z][A-Z][0-9][0-9]? --",dlg):
			out4.append({"LOCATION": dlg})
		else:
			out4.append(line)
			
#	for prob in [x for x,y in manualFixes if not x in found]:
#		print(prob)
	
	return(out4)








