from bs4 import BeautifulSoup, NavigableString
import json,re,copy


def cleanDialogue(txt):
	txt = txt.replace("...", "... ")
	txt = re.sub(" +"," ",txt)
	return(txt.strip())
	
	
def blockParser(bit,fileName,charName=""):
	choices = []
	subChoices = []
	for child in bit.children:
		if isinstance(child, NavigableString):
			pass
		else:
# 			print("====")
# 			print(child)
# 			print(type(child))
# 			print(child.get("class"))
# 			print(fileName)

			if child.name=="div" and "block" in child.get("class"):
				# Recursion
				subChoices.append(blockParser(child,fileName,charName))
				# If there are several blocks in a row,
				# then add them to the same choice level.
				# Otherwise just add it as a choice on its own
			else:
				# Not two blocks in a row, so reset subchoices and add
				if len(subChoices)>0:
					choices.append({"CHOICE":subChoices})
					subChoices = []
				if child.name=="p" and (child.get("class") is not None) and any([x in child.get("class") for x in ["indent","indent-nopad","indent-grey"]]):
					# Ordinary line of dialogue
					charName,dialogue = dialogueParser(child)
					if not dialogue is None and len(dialogue)>0:
						if len(choices)>0 and isinstance(choices[-1],list):
							choices.append({charName:dialogue})
						else:
							choices.append({charName:dialogue})
					else:
						# These are just a redundant list of options.
						pass
				elif child.name=="p":
				
					if child.get("class") is None:
						# Main character choice
						dialogueSpan = child.find("span")
						if dialogueSpan is not None:
							dialogue = dialogueSpan.get_text()
							if dialogue.strip().startswith("If "):
								if dialogue.count("in the party")>0:
									choices.append({"STATUS":dialogue})
								else:
									choices.append({"ACTION":dialogue})					
							else:
								if charName == "":
									choices.append({"Cloud":dialogue})
								else:
									choices.append({charName:dialogue})
						else:
							# Use character name from before
							dialogue = getDialogue(child)
							choices.append({charName:dialogue})
					else:
						if "block-inline-nopad" in child.get("class"):
							# dialogue resuming after action (use charName from before)
							# If there's a link, remove this
							if child.find("a"):
								child.find("a").extract()
							dialogue = getDialogue(child)#cleanDialogue(child.get_text())
							if len(dialogue)>0:
								choices.append({charName:dialogue})	
						elif  any([x in child.get("class") for x in ["italic-inline-nopad","italic-lineoption","action","block-grey"]]):
							# action
							if child.get_text().count("in the party")>0:
								choices.append({"STATUS":child.get_text()})
							else:
								choices.append({"ACTION":child.get_text()})			

						else:
							# Action description within a choice
							childClass = child.get("class")
							if childClass is not None and "italic" in childClass:
								if child.get_text().count("in the party")>0:
									choices.append({"STATUS":child.get_text()})
								else:
									choices.append({"ACTION":child.get_text()})		
							else:
								# CURRENTLY UNREACHABLE
								# There can be a difference between the option and your dialogue
								print((">>",child,fileName))
								# Then the above would be a cue
								dialogue = getDialogue(child)
								if len(dialogue)>0:
									charName = "Cloud"
									choices[-1] = {charName:dialogue,"_Cue":list(choices[-1].values())[0]}
				elif child.name=="blockquote":
					pt = partyResponsesParser(child)
					if pt is not None:
						choices.append(pt)
				elif child.name=="div":
					if child.get("class") is not None:
						if "highlight-nopad" in child.get("class"):
							if child.get_text().count("in the party")>0:
								choices.append({"STATUS":child.get_text()})
							else:
								choices.append({"ACTION":child.get_text()})	
						elif "highlight-white" in child.get("class"):
							# Cid flashback http://www.yinza.com/Fandom/Script/21.html
							charName = "Men"
							if child.find("b"):
								charName = child.find("b").get_text()
								child.find("b").extract()
							dialogue = getDialogue(child)
							choices.append({charName:dialogue})
						else:
							print(("&&",child,fileName))							
					else:
						print(("**",child,fileName))
				elif child.name=="ul":
					if child.get_text().count("dial (1)")>0:
						choices.append({"Letter":child.get_text()})
				elif child.name=="table":
					# Table of options depending on who is in the party
					# These are fixed manually later
					chars = [x.get_text().strip() for x in child.find_all("b")]
					charName = " or ".join(chars)
				elif child.name=="a":
					pass # Can ignore
				elif child.name=="br":
					pass
				else:
					
					print(("^^",child,fileName))
				
				
	if len(subChoices)>0:
		choices.append({"CHOICE":subChoices})		
				
	#print(choices)
	return(choices)


def getDialogue(bit):
	dialogue = ""
	for x in bit.children:
		if isinstance(x,NavigableString):
			if not x.string.strip().startswith("-"):
				dialogue += " " + x.string
		else:
			if not x.get_text().startswith("-"):
				dialogue += " " + x.get_text()
	dialogue = cleanDialogue(dialogue)
	return(dialogue)	

def dialogueParser(bit):
	bx = bit.find("b")
	if not bx is None:
		charName = bx.get_text()
		bx.extract()
		for a in bit.find_all("a"):
			a.extract()
		dialogue = getDialogue(bit)
		return((charName,dialogue.strip()))
	return((None,None))
	
	
def partyResponsesParser(bit):
	choices = []
	for part in bit.find_all("p",recursive=False):
		c,d = dialogueParser(part)
		if not c is None:
			choices.append([{"STATUS":"Party includes "+c},{c:d, "_Party":c}])
	if len(choices)>0:
		return({"CHOICE":choices})
	return(None)
#	return({"CHOICE":[[{"STATUS":"Party includes "+c},{c:d, "_Party":c}] for c,d in [dialogueParser(part) for part in bit.find_all("p")]]})
	
def tableParser(bit):
	# First, build a representation of the table
	tab = []
	for tr in bit.find_all("tr"):
		tab.append([])
		for td in tr.find_all('td'):
			if td.get("colspan"):
				charName,dialogue = dialogueParser(td)
				dx = {charName:dialogue,"_Party":charName}
				tab[-1].append(dx)
				for i in range(int(td.get("colspan"))-1):
					tab[-1].append(dx)
	choices = []
	for j in range(len(tab[0])):
		column = [tab[i][j] for i in range(len(tab))]
		partyMembers = list(set([list(x.keys())[0] for x in column]))
		column = [{"STATUS":"Party includes "+", ".join(partyMembers)}] + column
		choices.append(column)
	return({"CHOICE":choices})

def parseFile(fileName,parameters={"characterClassIdentifier":"ff7"},asJSON=False):
	
	o = open(fileName)
	d = o.read()
	o.close()
	
	# Make sure p tags are closed
# 	d2 = ""
# 	for line in d.split("\n"):
# 		if line.strip().startswith("<p") and not line.strip().endswith("</p>"):
# 			line += "</p>"
# 	d2 += line +"\n"
# 	d = d2
	d = d.replace("But really he's not so......","But really he's not so......</p>")
	
	d = d.replace("<p>Leave it alone</p>",'<p class="indent"><b>ACTION</b><br/>Player chooses \'Leave it alone\'</p>')
	d = d.replace('<p class="block-inline-nopad">Mission Orders: ','<p class="indent"><b>SYSTEM</b><br/>Mission Orders: ')

	#soup = BeautifulSoup(d, 'html.parser')
	# Parsing with html5lib so that p tags are closed
	soup = BeautifulSoup(d, "html5lib")
	script = soup.find('div', class_='content')
	
	# Manual fix 1 (no longer needed due to html5lib parsing above)
	#if script.find("p", string="Leave it alone") is not None:
	#	script.find("p", string="Leave it alone").replaceWith(BeautifulSoup('<p><span class="highlight">Leave it alone</span></p>', 'html.parser'))

	out = []
	choices = []
	charName = ""

	for bit in script.children:
		if not bit is None:
			if bit.name in ['h1','h4']:
				out.append({"LOCATION":getDialogue(bit)})
			elif bit.name=="hr":
				out.append({"ACTION":"---"})
			if bit.name is not None and bit.get("class") is not None:
				if bit.name == "div" and "block" in bit.get("class"):
					# CHOICE
					choices.append(blockParser(bit,fileName))
				else:
					# no more consecutive blocks, so reset choices and ad to out.
					if len(choices)>0:
						out.append({"CHOICE":choices})
						choices = []
						
					if bit.name == "p" and ("italic" in bit.get("class") or "italic-inline" in bit.get("class")):
						out.append({"ACTION":bit.get_text()})
					elif bit.name == "p" and ("indent" in bit.get("class") or "indent-grey" in bit.get("class")):
						charName,dialogue = dialogueParser(bit)
						if (not dialogue is None) and (len(dialogue)>0):
							out.append({charName:dialogue})
					elif bit.name == "p" and "block-inline" in bit.get("class"):
						# Resuming dialogue after action description
						# so use charName from last processing
						dialogue,cn = dialogueParser(bit)
						if cn is None:
							dialogue = getDialogue(bit)
							out.append({charName:dialogue})							
						else:
							out.append({cn:dialogue})				
							charName = cn
					elif bit.name == "p" and "block-grey" in bit.get("class"):
						# Sourceless voice
						dialogue = bit.get_text()
						dialogue = re.sub("(\.+)","\\1 ",dialogue)
						dialogue = dialogue.replace("?","? ")
						charName = "????"
						out.append({charName:cleanDialogue(dialogue)})
					elif bit.name=="div" and "highlight" in bit.get("class"):
						# This can include flashbacks, like in #http://www.yinza.com/Fandom/Script/31.html
						#out.append({"ACTION":'"'+getDialogue(bit.find("p"))+'"'})
						hilightBits = blockParser(bit,fileName)
						out += hilightBits
						if len(hilightBits)>2:
							out.append({"ACTION":"---"})
					elif bit.name=="p" and "block-color" in bit.get("class"):
						charName = "Voice in Cloud's head"
						out.append({charName:getDialogue(bit)})
					elif bit.name=="blockquote" and "party" in bit.get("class"):
						pt = partyResponsesParser(bit)
						if pt is not None:
							out.append(pt)
					elif (bit.name=="p" and "center" in bit.get("class")):
						out.append({"LOCATION":bit.get_text()})
					#elif bit.name=="table":
					#	out.append(tableParser(bit))
					else:
						print(bit)
						print(fileName)
						#print((bit.name,bit.get("class")))
		
		
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)

#---

def postProcessing(out):
	out2 = splitOrDialogue(out)
	out3 = fixCloudOptions(out2)
	out4 = fixNonMarkedChoices(out3)	
	
	# Individual line fixes
	out5 = []
	for line in out4:
		if line == {"Lucrecia": "Sephiroth... | Vincent..."}:
			out5.append({"CHOICE":[[{"Lucrecia": "Vincent..."}],[{"Lucrecia": "Sephiroth..."}]]})
		elif line == {"ACTION": "If he misses it he'll say either \"Jumped too soon...\" or \"Jumped too late...\""}:
			out5.append({"CHOICE":[[{"ACTION":"Cloud makes the jump."}],[{"Cloud": "Jumped too soon..."}],[{"Cloud":"Jumped too late..."}]]})
		elif line == {"????": "Kiiiiin..."}:
			out5.append({"ACTION": "... riiing ..."})
		else:
			out5.append(line)
	
	out6 = fixChoiceChunks(out5)
	
	return(out6)

def splitOrDialogue(bits):
	#"Aeris or Tifa":
	# 		{"Cloud, Tifa, or Cid": "Two!?"},
	#"Tifa or Aeris":
	ret = []
	for bit in bits:
		if isinstance(bit,dict):
			charName = [x for x in bit.keys() if not x.startswith("x")][0]
			if charName == "CHOICE":
				ret.append({"CHOICE":splitOrDialogue(bit["CHOICE"])})
			else:
				if charName.count(" or ")>0:
					# Replace commans with "or", e.g. "Cloud, Tifa, or Cid"
					# This is tricky, because the oxford comma can cause multiple
					#  "or"s in a row
					charNameX = charName.replace(", "," or ")
#					charNameX = re.sub(", (?!o)"," or ",charName)
#					charNameX = charNameX.replace(","," ")
#					charNameX = charName.replace(", ", ' or ')
					otherValues = [x for x in bit.items() if x[0].startswith("_")]
					choices = []
					for newChar in [re.sub("^or ","",x).strip() for x in charNameX.split(" or ")]:
						newDial = {newChar:bit[charName]}
						for o in otherValues:
							newDial[o[0]] = o[1]
						choices.append([{"STATUS":"Party includes "+newChar},newDial])
					ret.append({"CHOICE":choices})
				else:
					ret.append(bit)
		elif isinstance(bit,list):
			# list 
			ret.append(splitOrDialogue(bit))
	return(ret)

def getCharName(obj):
	return([k for k in obj if not k.startswith("_")][0])

def fixCloudOptions(out):
	for item in out:
		if "CHOICE" in item:
			for choiceList in item["CHOICE"]:
				if getCharName(choiceList[0]) == "Cloud" and getCharName(choiceList[1]) == "":
					choiceList[0]["ACTION"] = choiceList[0].pop("Cloud")
					choiceList[1]["Cloud"] = choiceList[1].pop("")
					choiceList[1]["_ChoicePrompt"] = copy.deepcopy(choiceList[0]["ACTION"])
				#for choice in choiceList:
				#	if "CHOICE" in choice:
				#		choice = fixCloudOptions([choice])
		if "" in item:
			item["ACTION"] = item.pop("")
	return(out)
			
def fixNonMarkedChoices(out):

	# List of choice recognition parts, with number of following lines to include
	# within the choice. Assuming that the alternative is that nothing is heard
	choiceList = [
		({"ACTION": "If you try to move on to the next car, a train worker stops you."},1),
		({"ACTION": "If you talk to the dog, you enter a short controls tutorial, and then a finger appears over Cloud's head."}, 4),
		({"ACTION": "If Cloud fails to push the button at the right time..."},1),
		({"ACTION": "If Cloud runs back into the church, he finds two small children there."},5),
		({"ACTION": "If Cloud looks inside the shopkeeper's freezer..."}, 1),
		({"ACTION": "If Cloud tries to run away upstairs, Aeris comes after him."}, 1),
		({"ACTION": "If Cloud tries to leave the area..."}, 1),
		({"ACTION": "If they try to open the treasure chests..."},1), # in CHOICE
		({"ACTION": "If Cloud tries to go back down..."},1),
		({"ACTION": "If Cloud speaks to her after she enters one of the offices..."},1), # has whisper
		({"ACTION": "If Cloud tries to leave Kalm..."},1),
		({"ACTION": "If Cloud runs back to town instead of following Tifa..."},1),
		({"ACTION": "If Cloud tries to run out..."},1),
		({"ACTION": "If Cloud tries to run away..."},1),
		({"ACTION": "If Cloud goes back down the elevator..."},2),
		({"ACTION": "If by chance Cloud actually has the money to buy the villa..."},2),
		({"ACTION": "If Cloud kicks the soccer ball at Red XIII, he'll jump up and growl at him."},1),
		({"ACTION": "If Barret is in your party..."},1),
		({"ACTION": "If Cloud attempts to enter without paying, he's stopped by the admissions lady."},1),
		({"ACTION": "If Cloud tries to leave the Station alone, one of them will run up to him..."},1),
		({"ACTION": "If Cloud attempts to go upstairs without paying..."},1),
		({"ACTION": "If Cloud tries to leave Gold Saucer via the Ropeway..."},1),
		({"ACTION": "If Cloud tries to run out into the desert..."},1),
		({"ACTION": "If Cloud gets himself lost in the desert, eventually a mysterious chocobo carriage will appear."},1),
		({"ACTION": "If Cait Sith is in the party..."},3),
		({"ACTION": "If you try to go back out..."},1),
		({"ACTION": "If Cloud tries to get back in the Tiny Bronco to leave..."},1),
		({"ACTION": "If Cloud tries to run upstairs..."},2),
		({"ACTION": "If Cloud tries to leave Wutai..."},1),
		({"ACTION": "If Yuffie is in the party and they try to proceed to the second floor without fighting..."},1),
		({"ACTION": "If Yuffie tries to go to the next floor prematurely..."},1),
#		({"ACTION": "If Yuffie tries to go to the next floor prematurely..."},1),
#		({"ACTION": "If Yuffie tries to go to the next floor prematurely..."},1),
		({"ACTION": "If Cloud tries to search his belongings..."},1),
#		({"ACTION": "If the number of battles fought ends in two even numbers..."},1),
#		({"ACTION": "If the number of battles fought ends in two odd numbers..."},1),
		({"ACTION": "If he comes before obtaining the Tiny Bronco, the house is empty..."},1),
		({"ACTION": "If Cloud tries to open something without giving him Mythril..."},1),
		({"ACTION": "If Cloud walks to the bed..."},2),
		({"ACTION": "If Nanaki is in the party..."},1),
		({"ACTION": "If they try to leave the room..."},1),
		({"ACTION": "If Cloud has already taken the map..."},1),
		({"ACTION": "If Barret goes the wrong way..."},1),
		({"ACTION": "If you return to the Chocobo Farm after visiting the Chocobo Sage..."},3),
		({"ACTION": "On any subsequent visit after seeing the Chocobo Sage..."},3),
		({"ACTION": "If Vincent is not in the party..."},1),
		({"ACTION": "If, in following Diamond Weapon, the Highwind rams into it..."},1),
		({"ACTION": "If Cloud attempts to go down the path he didn't choose, he will stop and say:"},1),
		({"ACTION": "Cloud and his chosen party head off down one path. If they go left, they come to another fork."},2),
		({"ACTION": "If you try to move on to the next car, a train worker stops you."},1)
	]
	# Lookup for speed
	clFirstParts = [x[0] for x in choiceList]
	
	out2 = []
	i = 0
	while i < len(out):
		if out[i] in clFirstParts:
			for chx,numLinesToInclude in choiceList:
				if chx == out[i]:
					activeChoice = [out[i]]
					for extraLine in range(numLinesToInclude):
						i += 1
						activeChoice.append(out[i])
					out2.append({"CHOICE":[activeChoice,[]]})
		else:
			out2.append(out[i])
		i += 1

	return(out2)
	
	
def fixChoiceChunks(out):

	choiceList = [
		({"Cloud": "You were selling flowers"},
		[{"Cloud": "You were selling flowers"},
		{"CHOICE": [
			[{"ACTION": "If you bought a flower:"},
			 {"Aerith": "Oh! I'm so happy! Thanks for buying my flowers."}],
			[{"ACTION": "Or, if you didn't buy a flower:"},
			 {"Aerith": "Oh! I'm so happy! You didn't buy any flowers from me though. Well, that's okay."}]
		]}], 3),
		({"Man": "To you it may be a junk yard, but to us its home."},
		[{"CHOICE":[
			[{"STATUS": "If Barret is in the party, he will instead say:"},
			 {"Man": "It might be full of junk, but this is the only home we got, Barret!!"},
			 {"Barret": "Of... of course! We're all born and raised in the coal mines!! No matter how tough it gets, our hearts burn bright red like coal!"}],
			[{"Man": "To you it may be a junk yard, but to us its home."}]
		]}], 3),
		({"ACTION": "If they try to open the treasure chests..."},
		[{"CHOICE":[[
			{"ACTION": "If they try to open the treasure chests..."},
		 	{"Shinra Cashier": "You opened up all those things without asking and, hey wait!"}
		],[]]}],1),
		({"Yuffie": "You spikey-headed jerk! One more time, let's go one more time!"},
		 [{"CHOICE":[
		 	[{"ACTION": "If Tifa is party leader:"},
			 {"Yuffie": "Hey, boobs! Try that again! Just one more time!"}],
			[{"ACTION": "Or, if Cid is party leader:"},
			 {"Yuffie": "Hey, you bow-legged ol' man! Give me another chance! I'll fight ya again!"}],
		 	[{"Yuffie": "You spikey-headed jerk! One more time, let's go one more time!"}]
		 ]}
		 ], 4),
		 ({"Yuffie": "Heh heh... thought so. You put me in a spot. Hmm, what should I do? But if you want me that bad, I can't refuse..."},
		 [
			{"CHOICE": [
				[{"ACTION": "If Cloud is the party leader"},
				 {"Yuffie": "Heh heh... thought so. You put me in a spot. Hmm, what should I do? But if you want me that bad, I can't refuse..."}],
				[{"ACTION": "If Tifa or Cid are party leader, the above line is slightly different:"},
				 {"Yuffie": "But if you want me that bad, I can't really say no... All right! I'll go with you!"}]
			]}], 2),
		({"Ester": "Too bad."},
		[{"Ester": "Too bad."},
		 {"CHOICE":[
			[{"ACTION": "If Cloud comes in 4th place or worse:"},
			 {"Ester": "You had a tough situation there."}],
			[{"ACTION": "If Cloud comes in 3rd place:"},
			 {"Ester": "I was expecting a little more from you."}],
			[{"ACTION": "If Cloud comes in 2nd place:"},
			 {"Ester": "You were so close."}]
		]}], 6)	,
		({"Red XIII": "Interesting... They were definitely waiting for us.", "_Party": "Red XIII"},
		[{"CHOICE":[
 			[{"ACTION":"If before Cosmo Canyon:"},
 			 {"Red XIII": "Interesting... They were definitely waiting for us.", "_Party": "Red XIII"}],
			[{"ACTION":"If after Cosmo Canyon:"},
			 {"Red XIII": "Hey, Cloud. How did the Turks know to wait and ambush us here?", "_Party": "Red XIII"}]
		]}],1),
		({"Tifa": "All right"}, [{"Tifa": "What did you say!?"}], 0),
		({"Cid": "All right"}, [{"Cid": "Give her a lickin'"}], 0),
		({"Tifa": "Not interested"}, [{"Tifa": "Don't fight"}], 0),
		({"Cid": "Not interested"}, [{"Cid": "Forget it!"}], 0),
		({"Cid": "......petrified."}, [{"Cid": "Something like that."}], 0),
		({"Tifa": "You're gonna lose again."}, [{"Tifa": "You're outta your league!"}],0),
		({"Cid": "You're gonna lose again."}, [{"Cid": "You're wasting your time"}],0),
		({"Tifa": "Go ahead..."}, [{"Tifa": "Yeah, so?"}], 0),
		({"Cid": "Go ahead..."}, [{"Cid": "GO, then!"}], 0),
		({"Cid": "Wait a second!"}, [{"Cid": "......Hold on!"}], 0),
		###############
		# http://www.yinza.com/Fandom/Script/10.html
		({"CHOICE": [
				[
					{"STATUS": "Party includes Yuffie"},
					{"Yuffie": "......That's right."}],
				[
					{"STATUS": "Party includes Yuffie"},
					{"Yuffie": "......That's right."}],
				[
					{"STATUS": "Party includes Cloud"},
					{"Cloud": "......That's right."}],
				[
					{"STATUS": "Party includes Tifa"},
					{"Tifa": "......That's right."}],
				[
					{"STATUS": "Party includes Cid"},
					{"Cid": "......That's right."}]]},
		[{"CHOICE": [
				[{"ACTION": "Cloud is party leader"},
				 {"Yuffie": "What is it, you still have somethin' for me? ...... Hmmm. So is that it? I know you want my help because I'm so good! You want me to go with you?"}],
				[{"ACTION": "Tifa or Cid are party leaders"},
				 {"Yuffie": "What, you still want somethin'? ...Hmm. So is that it? You want my help 'cause I'm so good! You want me to go with you! Is that what you're saying?"}]
			]},
		 {"CHOICE":[
		 	[
					{"STATUS": "Party includes Cloud"},
					{"Cloud": "......That's right."}],
				[
					{"STATUS": "Party includes Tifa"},
					{"Tifa": "......That's right."}],
				[
					{"STATUS": "Party includes Cid"},
					{"Cid": "......That's right."}]]}], 0),
		############
		({"CHOICE": [
			[
				{"STATUS": "Party includes Yuffie"},
				{"Yuffie": "You kiddin'?"}],
			[
				{"STATUS": "Party includes Yuffie"},
				{"Yuffie": "You kiddin'?"}],
			[
				{"STATUS": "Party includes Cloud"},
				{"Cloud": "You kiddin'?"}],
			[
				{"STATUS": "Party includes Tifa"},
				{"Tifa": "You kiddin'?"}],
			[
				{"STATUS": "Party includes Cid"},
				{"Cid": "You kiddin'?"}]]},
		 [{"CHOICE": [
			[
				{"STATUS": "Party includes Cloud"},
				{"Cloud": "You kiddin'?"}],
			[
				{"STATUS": "Party includes Tifa"},
				{"Tifa": "No way!"}],
			[
				{"STATUS": "Party includes Cid"},
				{"Cid": "What're you sayin'!"}]]}], 0),
		##########		
		({"Tifa": "Like to help but..."},
		[{"Tifa": "I'm sorry... really"}],0),
		({"Tifa": "I guess we'll help you"},
		[{"Tifa": "All right, we'll help"}],0),
		### https://gamefaqs.gamespot.com/boards/197341-final-fantasy-vii/61401193
		({"Beautiful Bro": "Ummm, not quite there."},
			[{"CHOICE":[
				[{"ACTION":"If Cloud is wearing a poor combination of clothes/jewelry/perfume"},
				 {"Beautiful Bro": "Ummm, not quite there."},],
				[{"ACTION":"If Cloud is wearing a middling combination of clothes/jewelry/perfume"},
				 {"Beautiful Bro": "Ehhhh, so so."}],
				[{"ACTION":"If Cloud is wearing a good combination of clothes/jewelry/perfume"},
				 {"Beautiful Bro": "Hmm, pretty good."}]
			]}], 2)
	]
	
	choiceListFirstParts = [x[0] for x in choiceList]
	
	def walkChunks(outx):
		ret = []
		i = 0
		while i < len(outx):
			line = outx[i]
			if line in choiceListFirstParts:
				for targetLine,repLines,numSkip in choiceList:
					if line == targetLine:
						ret += repLines
						i += numSkip
						#break
			else:			
				if "CHOICE" in line:
					choices = []
					for choice in line["CHOICE"]:
						choices.append(walkChunks(choice))
					ret.append({"CHOICE": choices})
				else:
					ret.append(line)
			i += 1
		return(ret)
	
	out2 = walkChunks(out)
	
	return(out2)