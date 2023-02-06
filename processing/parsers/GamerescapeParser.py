# TODO: Currently, we organise choices by character dialogue options
#  with one response per option. But often there are multiple options with
#  the same response. So it would be better to have a choice representing 
#  the player dialogue options (within the larger choice), then a 
#  single copy of the reaction.

from bs4 import BeautifulSoup
import json,re


def cleanText(txt):
	txt = txt.strip()
	txt = txt.replace("..."," ... ")
	txt = re.sub("\n+"," ",txt)
	txt = re.sub(" +"," ",txt)
	txt = txt.replace('"',"")
	txt = re.sub("<(.+?)>","(\\1)",txt)
	return(txt)
	
def cleanName(txt):
	txt = txt.replace("(-","")
	txt = txt.replace("-)","")
	txt = txt.strip()
	return(txt)

def olParser(dialogue):
	outx = []	
	lines = [x.getText() for x in dialogue.find_all("li")]
	for l in lines:
		charName = l[:l.index(" ")].strip()
		tx = l[l.index(" "):]
		entry = {cleanName(charName):cleanText(tx)}
		#print(entry)
		outx.append(entry)
	return(outx)

def bubbleParser(bubbles):

	def dialoguePartsToStructure(cx,dialogueParts):
		# dialogue parts is a list of items
		#  some items are strings and some items are lists
		#  
		if(any([isinstance(x,list) for x in dialogueParts])):
			choiceTXT = ["",""]
			condition1 = {"STATUS":"PC is male"}
			condition2 = {"STATUS":"PC is female"}
			for dpart in dialogueParts:
				if isinstance(dpart,list):
					choiceTXT[0] += " " + dpart[0]
					choiceTXT[1] += " " + dpart[1]
					if len(dpart)>=4:
						condition1 = dpart[2]
						condition2 = dpart[3]
				else:
					choiceTXT[0] += dpart
					choiceTXT[1] += dpart
			return({"CHOICE":[
				[condition1,{cleanName(cx):cleanText(choiceTXT[0])}],
				[condition2,{cleanName(cx):cleanText(choiceTXT[1])}]]})
		else:
			dlg = cleanText(" ".join(dialogueParts))
			if dlg.count("►")>0:
				cx = "LOCATION"
			return({cleanName(cx):dlg})


	def makeEntry(cx,dBubbles):	
	
		def parseElement(element):
			if element.name=="hr":
				return(None)
			# I thought Horizontal rules meant alternative lines
			#  But that's not the case (maybe green lines are alt?)
			# But here's the code to make them different choices:
			#	if len(dialogueParts)>0:
			#		# string dialogues together
			#		choices.append(dialoguePartsToStructure(cx,dialogueParts))
			#	dialogueParts = []
			elif element.name=="span":
				# Check if it's gender related
				sty = element.get("style","")
				# Alternative text is in the "title" attribute
				t = element.get("title","")
				if sty.count('color:#6CA0DC')>0 and len(t)>0:
					# Span text depends on gender
					# Return word for choice 1, word for choice 2, condition for choice1, condition for choice 2
					return([element.getText(),t])
				else:
					return(element.getText())
			else:
				dlg = element.getText()
				if not element.name is None and "loremongerconditional" in element.get("class",[]):
					condition = element.get("title","").strip()
					if len(condition)>0:
						return([dlg, "", {"STATUS":condition}, {"STATUS":"Otherwise"}])
				return(dlg)

	
		# dBubbles is a list of bubble divs
		dialogueParts = []
		for bub in dBubbles:
			for element in bub:
				if element.name == "p":
					# just one level of recursion for p
					for pElem in element:
						dlg = parseElement(pElem)
						if not dlg is None:
							dialogueParts.append(dlg)
				else:
					dlg = parseElement(element)
					if not dlg is None:
						dialogueParts.append(dlg)
			

		choices = []
		if len(dialogueParts)>0:
			choices.append(dialoguePartsToStructure(cx,dialogueParts))
		
		if len(choices)==1:		
			entry = choices[0]
		else:
			entry = {"CHOICE":choices}
		return(entry)

	outx = []
	charName = "ACTION"
	currentLine = []
	for bubbleDiv in bubbles:
		# Identify whether bubble is dialogue or charName
		isCharName = bubbleDiv["style"].count("#b9b9b9")>0
		if isCharName:
			# Dump current line
			if len(currentLine)>0:
				outx.append(makeEntry(charName,currentLine))
				currentLine = []
			# Update charName
			charName = bubbleDiv.getText()
		else:
			# Add current dialogue
			currentLine.append(bubbleDiv)
	if len(currentLine)>0:
		outx.append(makeEntry(charName,currentLine))
	return(outx)
	
def choiceParser(choice):
	outx = []
	caption = choice.find("caption")
	if not caption is None:
		outx.append({"ACTION":cleanText(caption.getText())})
	
	captionCharName = "ACTION"
	if caption is None or caption.getText().count("What will you say?")>0:
		captionCharName = "PC"

	headers = choice.find_all("th")
	headers = [{cleanName(captionCharName):cleanText(x.getText())} for x in headers]
	headerResponses = []
	
	body = choice.find("tbody")
	parts = body.find_all("tr",recursive=False)
	if len(parts)>1:
		# there's some dialogue following the player choice
		parts = parts[1]
		tds = parts.find_all("td",recursive=False)
		for i in range(len(tds)):
			td = tds[i]
			bubbles = td.find_all("div",{"class":"bubble"})
			dlg = bubbleParser(bubbles)
			numOfResponseCols = int(td.get("colspan","1"))
			for hrIndex in range(numOfResponseCols):
				headerResponses.append(dlg)

	choices = []	
	for i in range(len(headers)):
		choice = [headers[i]]
		if len(headerResponses)>i:
			choice += headerResponses[i]
		choices.append(choice)
	outx.append({"CHOICE":choices})
	return(outx)

def parseFile(fileName,parameters={},asJSON=False):
	print(fileName)
	o = open(fileName)
	d = o.read()
	o.close()
	
	
	
	# Main parsing
	
	def isChoiceTable(table):
		if table.get("class","")!="":
			# If it's a class="datatable-GEtable", then it's a choice
			return("datatable-GEtable" in table["class"])
		return(False)

	def isActionTable(table):
		# TODO: Figure out how to read attributes 
		#  if item has none
		if table.get("style","")!="":
			# If it has a style, and the style has background:#222222, then it's an ACTION. (Just get text)
			return(table["style"].count("background:#222222")>0)
		return(False)

	def getQuestDetails(soup):
		qtable = soup.find("table").find("table")
		td = qtable.find_all("td")[1]
		
		td = [x for x in td]
		
		level = td[0].getText().strip()
		qTitle = td[1].getText().strip()
		scenario = td[2].getText().strip()
		
		xp = soup.find("a",{"title":"Experience Points"})
		if xp is None:
			xp = "NA"
		else:
			xp = xp.find_previous_sibling("div").getText().strip()
			xp = xp.replace(",","")


		qdetails = {"SYSTEM":qTitle,
				"_Level":level,
				"_Scenario": scenario,
				"_XP":xp}
		
		gilMarker = soup.find("a",{"title":"Gil"})
		if not gilMarker is None:
			gil = gilMarker.find_previous_sibling("div").getText().strip()
			gil = gil.replace(",","")
			qdetails["_Gil"]=gil
			
		# NPCs
#		interactions = soup.find("div",{"title":"Interactions"})
#		if not interactions is None:
#			trs = interactions.find("table").find("tbody").find("td",{"colspan":"2"},recursive=True)
#			npcs = trs.find_all("a",recursive=True)
#			print(len(npcs))
		
		return(qdetails)

	out = []
	if len(d)>2:
		soup = BeautifulSoup(d,'html5lib')
		questDetails = getQuestDetails(soup)
		out.append({"ACTION":"---"})
		out.append(questDetails)
		
		dialogue = soup.find("div",{"title":"Dialogue"})
		# Find all top-level tables
		tables = dialogue.find_all("table",recursive=False)
		
		#x = dialogue.find("td",{"colspan":2}, recursive=True)
		#if not x is None:
		#	print("!!!!!")
		#	print(fileName)
		
		for table in tables:
			if isChoiceTable(table):
				cx = choiceParser(table)
				out += cx
			elif isActionTable(table):
				cx = "ACTION"
				txt = table.getText().strip()
				if txt.count("►")>0:
					cx = "LOCATION"
				out.append({cx: txt})
			else:
				# Otherwise, it's passed to the bubble parser
				bubbles = table.find_all("div",{"class":"bubble"})
				if len(bubbles)>0:
					out += bubbleParser(bubbles)
				else:
					out += olParser(table)
	
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)

def postProcessing(out):

	# Manual fixes for Two characters with same dialogue, see #366
	out2 = []
	attendants = ["Arrivals Attendant (Gridania)"]*4 + ["Arrivals Attendant (Limsa Lominsa)"]*4
	attendantI = 0
	for line in out:
		if "CHOICE" in line:
			for fc in line["CHOICE"]:
				if len(fc)>1 and "Arrivals Attendant" in fc[1] and fc[1]["Arrivals Attendant"] in ["Do you wish to leave the landing area?","We hope you have a pleasant voyage.",""]:
					fc[1][attendants[attendantI]] = fc[1].pop("Arrivals Attendant")
					attendantI += 1
			out2.append(line)
		else:
			out2.append(line)
	
	# Manual division of lines and character names
	swaps = [
		({"Citizen": "Look! The white dragon!"},
			[{"Male Citizen": "Look!"},{"Female Citizen": "The white dragon!"},]),
		({"Imperialsoldier": "Nothing to report, sir! We have received an anonymous warning that insurgent forces are near. We must redouble our vigilance. I shall recommend that patrols be increased."},
			[{"Imperial Sentry": "Nothing to report, sir!"}, {"Imperial Decurion": "We have received an anonymous warning that insurgent forces are near. We must redouble our vigilance. I shall recommend that patrols be increased."}]),
		({"Imperialsoldier": "What of the captive? Does she still refuse to speak? She may as well be a deaf-mute for all the information we've gotten out of her. The others aren't much better. The Elezen gets on my nerves most of all. Every time he opens his mouth, it's only to spout gibberish. I do wonder, why is the tribunus so obsessed with this Minfilia woman? They say she possesses some mystical power. Something we Garleans don't have. Mystical power? Like the kind the beastmen use? How am I supposed to bloody know? If you're so curious, why don't you ask the tribunus yourself? As well try to tumble her! I like my head where it is, thank you very much! Our break is over. Best we get back to our stations."},
			[{"Collected Voice": "What of the captive? Does she still refuse to speak?"},
			{"Youthful Voice": "She may as well be a deaf-mute for all the information we've gotten out of her."},
			{"Gruff Voice": "The others aren't much better. The Elezen gets on my nerves most of all. Every time he opens his mouth, it's only to spout gibberish."},
			{"Youthful Voice": "I do wonder, why is the tribunus so obsessed with this Minfilia woman?"},
			{"Gruff Voice": "They say she possesses some mystical power. Something we Garleans don't have."},
			{"Youthful Voice": "Mystical power? Like the kind the beastmen use?"},
			{"Gruff Voice": "How am I supposed to bloody know? If you're so curious, why don't you ask the tribunus yourself?"},
			{"Youthful Voice": "As well try to tumble her! I like my head where it is, thank you very much!"},
			{"Collected Voice": "Our break is over. Best we get back to our stations."}]),
		({"Yellowjacket": "Ah, you must be the adventurer of whom the Yellowjackets sent word. I hear you are to brave the depths of the Sastasha Seagrot. The occupants of those caves are rumored to be as numerous as they are bloodthirsty. No matter what the epic tales would have you believe, strolling into such a den of savagery alone would be the height of foolishness. No, you shall need companions. And you shall need the training we here at the Hall of the Novice can provide! I strongly suggest that you study the fundamentals of group combat before continuing on your mission. The Smith here oversees the training schedules. Speak with him, and you can register for exercises tailored to your particular field of expertise. When you have mastered all that our masters have to teach, then it will be time to head north once more. Report to the Yellowjacket scout at the mouth of the Sastasha Seagrot, and he will furnish you with the details of your duty. When your skills have been honed and your mind sharpened, continue onwards to the north. The Yellowjacket scout stationed before the Sastasha Seagrot will have the details of your mission. Please tell me you're here on Yellowjacket duty, and not some daft sod out for a stroll. I can't take any more of this blasted waiting. You are? Thank the gods. I assume you already know about the ship seen slipping around the Isles of Umbra? We've been on the lookout for pirate activity ever since that vessel was sighted, thinking a crew of cutthroats might have a den nearby. So when we received word that men of questionable quality had been seen passing in and out of Sastasha here, we weren't entirely surprised. I've yet to see them for myself, but if this lot belongs to those fishback-fancying Serpent Reavers ... Well, you can imagine the panic it'll cause. The kidnappings are still fresh in people's minds. Anyway, your task is to poke around in the caves, and find out exactly who we're dealing with. While you do that, I'll be keeping watch out here ... praying you don't spot any blue face tattoos."},
			[{"Seasoned Adventurer": "Ah, you must be the adventurer of whom the Yellowjackets sent word. I hear you are to brave the depths of the Sastasha Seagrot. The occupants of those caves are rumored to be as numerous as they are bloodthirsty. No matter what the epic tales would have you believe, strolling into such a den of savagery alone would be the height of foolishness. No, you shall need companions. And you shall need the training we here at the Hall of the Novice can provide! I strongly suggest that you study the fundamentals of group combat before continuing on your mission. The Smith here oversees the training schedules. Speak with him, and you can register for exercises tailored to your particular field of expertise. When you have mastered all that our masters have to teach, then it will be time to head north once more. Report to the Yellowjacket scout at the mouth of the Sastasha Seagrot, and he will furnish you with the details of your duty. When your skills have been honed and your mind sharpened, continue onwards to the north. The Yellowjacket scout stationed before the Sastasha Seagrot will have the details of your mission."}, {"Yellowjacket (Sastasha Seagrot)":"Please tell me you're here on Yellowjacket duty, and not some daft sod out for a stroll. I can't take any more of this blasted waiting. You are? Thank the gods. I assume you already know about the ship seen slipping around the Isles of Umbra? We've been on the lookout for pirate activity ever since that vessel was sighted, thinking a crew of cutthroats might have a den nearby. So when we received word that men of questionable quality had been seen passing in and out of Sastasha here, we weren't entirely surprised. I've yet to see them for myself, but if this lot belongs to those fishback-fancying Serpent Reavers ... Well, you can imagine the panic it'll cause. The kidnappings are still fresh in people's minds. Anyway, your task is to poke around in the caves, and find out exactly who we're dealing with. While you do that, I'll be keeping watch out here ... praying you don't spot any blue face tattoos."}]),
		#({"(Unknown Archer)": "Right. Time for my patrol ... I'll leave once my morning meal has had a chance to settle. I have spied not a scale nor a talon all day. Mayhaps the view would be better from Ashpool ... "},
		#	[{"Lancer01607": "Right. Time for my patrol ... I'll leave once my morning meal has had a chance to settle."},{"Archer01607": "I have spied not a scale nor a talon all day. Mayhaps the view would be better from Ashpool ... "}]),
		({"CHOICE": [
				[
					{"STATUS": "midday / evening"},
					{"(Unknown Archer)": "Right. Time for my patrol ... I'll leave once my morning meal has had a chance to settle. I have spied not a scale nor a talon all day. Mayhaps the view would be better from Ashpool ... "}],
				[
					{"STATUS": "Otherwise"},
					{"(Unknown Archer)": "Right. Time for my patrol ... I'll leave once my meal has had a chance to settle. I have spied not a scale nor a talon all day. Mayhaps the view would be better from Ashpool ... "}]]},
		[{"CHOICE": [
				[
					{"STATUS": "midday / evening"},
					{"Archer01607": "Right. Time for my patrol ... I'll leave once my morning meal has had a chance to settle."}],
				[
					{"STATUS": "Otherwise"},
					{"Archer01607": "Right. Time for my patrol ... I'll leave once my morning meal has had a chance to settle."}]]},
		 {"Lancer01607": "I have spied not a scale nor a talon all day. Mayhaps the view would be better from Ashpool ... "}])
	]
		


	out3 = []
	for line in out2:
		foundSwap = False
		for targ,swap in swaps:
			if line == targ:
				out3 += swap
				foundSwap = True
		if not foundSwap:
			out3.append(line)
		prevLine = line
			
	return(out3)
	
	
	
	
	
	
	
	