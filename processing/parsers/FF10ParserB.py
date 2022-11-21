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
from urllib.request import urlopen

finalFantasy10WhoGallery = {}
FF10defaultCharacterName = "Tidus"
#FF10SkipSection = False  # No need to make global

def parseFile(fileName,parameters={},asJSON=False):


	print(fileName)
	html = open(fileName, 'r')
	html = html.read().replace('<span class="mov">(Whistles.)</span>','<span class="mov">(Whistles.)</span></span>')
	html = html.replace('div stage="sc"','div class="sc"')
	html = re.sub('M<(.+?)>other','<\\1>Mother',html )
	html = re.sub('Man in <(.+?)>yellow, blue and green','<\\1>Man in yellow, blue and green',html )
	html = re.sub('Roving Luca <(.+?)>guard','<\\1>Roving Luca guard',html )
	html = re.sub('Fancy <(.+?)>woman','<\\1>Fancy woman',html )
	html = re.sub('<(.+?)>Male<(.+?)> and <(.+?)>female<(.+?)> warrior monks on stadium end of causeway','Warrior monks on stadium end of causeway', html)
	html = re.sub('<(.+?)>Crusader<(.+?)> and <(.+?)>warrior monk<(.+?)> at bar:', 'Crusader plus warrior monk at bar:', html)
	html = re.sub('<(.+?)>Woman<(.+?)> and <(.+?)>girl<(.+?)> conversing','Woman plus girl conversing',html)
	html = re.sub('<(.+?)>Man<(.+?)> and <(.+?)>woman<(.+?)> talking at stadium end:', 'Man plus woman talking at stadium end:',html)
	html = re.sub('Lefthand <(.+?)>guard<(.+?)> at railing', 'Lefthand guard at railing',html)
	html = re.sub('Righthand <(.+?)>guard<(.+?)> at railing', 'Righthand guard at railing',html)
	html = re.sub('<(.+?)>woman in white halter top<(.+?)>, portly <(.+?)>guy in blue vest<(.+?)>','',html)
	html = re.sub('<(.+?)>Man<(.+?)> and <(.+?)>woman<(.+?)> talking on stadium end of causeway:','Man plus woman talking on stadium end of causeway:',html)
	html = re.sub('Kulukan&#8217;s <(.+?)>little sister<(.+?)>:',"Kulukan's little sister:",html)
	html = re.sub('-Yeah, those fiends really ruined the whole blitz experience','Woman talking at stadium end: Yeah, those fiends really ruined the whole blitz experience',html)
	html = re.sub('<p>This page is a hodgepodge of sidequests.+?</p>','',html)
	html = html.replace('<span class="M">Celestial Mirror</span>','Celestial Mirror')
	html = html.replace('(If have played before)</span>:','(If have played before)</span>-')
	html = html.replace('message from Cid. He says: We','message from Cid. He says- We')
	
	html = html.replace('class="TN">Narration: There was something I','class="T">Tidus: There was something I')
	html = html.replace('Narration: Maybe that','Tidus: Maybe that')
	html = html.replace('&#172;He&#8217;s fallen asleep.',' (He&#8217;s fallen asleep.)')
	
	html = html.replace('<a class="who sc-tooltip" data-image="../characters/beclem.jpg" data-desc="" href="../characters/beclem.jpg" target="screencap">Soldier</a> and <a class="who sc-tooltip" data-image="../characters/lilcrusader.jpg" data-desc="" href="../characters/lilcrusader.jpg" target="screencap">boy</a> fighting:','<a class="who sc-tooltip" data-image="../characters/beclem.jpg" data-desc="" href="../characters/beclem.jpg" target="screencap">Soldier and boy fighting</a>:')
	html = html.replace('<a class="who sc-tooltip" data-image="../characters/beakyP.jpg" data-desc="" href="../?attachment_id=488" target="screencap">Little beaky guy</a> talking to <a class="who sc-tooltip" data-image="../wp-content/uploads/2015/09/98redvest.jpg" data-desc="" href="../?attachment_id=518" target="screencap">Al Bhed in red vest</a>','<a class="who sc-tooltip" data-image="../characters/beakyP.jpg" data-desc="" href="../?attachment_id=488" target="screencap">Little beaky guy and Al Bhed in a red vest</a>')
	
	html = html.replace('<p>Warrior monk and Crusader at bar:<br />', '')
	html = html.replace('-The temple is a wreck. I really want to quit the warrior monks.<br />', '<p>Warrior monk: The temple is a wreck. I really want to quit the warrior monks.</p>')
	html = html.replace('-Then join the Crusaders! We&#8217;d love to have you join our force.</p>', '<p>Crusader at bar: -Then join the Crusaders! We&#8217;d love to have you join our force.</p>')
	html= html.replace('<p><span class="npc">Pair of warrior monks near Stadium:<br />', '<p><a class="who">Pair of warrior monks near Stadium</a>:<br />')
	
	html = html.replace('<p>Luca <a class="who sc-tooltip" data-image="../wp-content/uploads/2015/09/46guardgray.jpg" data-desc="" href="../?attachment_id=518" target="screencap">guard</a> on patrol:', '<p>Luca guard on patrol:')
	html = html.replace('<p>Luca <a class="who sc-tooltip" data-image="../wp-content/uploads/2015/09/37biggs.jpg" data-desc="" href="../?attachment_id=469" target="screencap">guard</a> on patrol:', '<p>Biggs:')
	
	html = html.replace('<p>Lefthand <a class="who sc-tooltip" data-image="../characters/warriormonk.jpg" data-desc="" href="../characters/warriormonk.jpg" target="screencap">warrior monk</a>', '<p>Lefthand warrior monk')
	html = html.replace('<p>Righthand <a class="who sc-tooltip" data-image="../characters/warriormonk.jpg" data-desc="" href="../characters/warriormonk.jpg" target="screencap">warrior monk</a>', '<p>Righthand warrior monk')
	
	html = html.replace('<p>Second <a class="who sc-tooltip" data-image="../characters/warriormonkf.jpg" data-desc="" href="../characters/warriormonkf.jpg" target="screencap">warrior monk</a>', '<p>Second warrior monk')
	html = html.replace('<p>Bustling <a class="who sc-tooltip" data-image="../characters/kiryuu.jpg" data-desc="" href="../characters/kiryuu.jpg" target="screencap">female sailor</a>', '<p>Bustling female sailor')	
	
	html = html.replace('<p>Little <a class="who sc-tooltip" data-image="../characters/boyGB.jpg" data-desc="" href="../characters/boyGB.jpg" target="screencap">boy w/green headband</a>','<p>Little boy w/green headband')
	
	html = html.replace('come back yet. Where could they be?','come back yet. Where could they be?</span>')
	
	html = html.replace('<p>Stadium <a class="who sc-tooltip" data-image="../wp-content/uploads/2015/09/31pompom.jpg" data-desc="" href="../?attachment_id=473" target="screencap">receptionist</a>', '<p>Stadium receptionist')
	
	html = html.replace('<p>Opportunistic <a class="who sc-tooltip" data-image="../characters/mifurey.jpg" data-desc="" href="../characters/mifurey.jpg" target="screencap">woman in green</a>', '<p>Opportunistic woman in green')
	
	html = html.replace('<p>Lefthand <a class="who sc-tooltip" data-image="../characters/guardbrown.jpg" data-desc="" href="../characters/guardbrown.jpg" target="screencap">Luca guard</a> at railing', '<p>Lefthand Luca guard at railing')
	
	html = html.replace('<p>Short <a class="who sc-tooltip" data-image="../characters/crusaderPG.jpg" data-desc="" href="../characters/crusaderPG.jpg" target="screencap">Crusader in purple &#038; green</a>', '<p>Short Crusader in purple &#038; green')
	
	html = html.replace("""<p><span class="clue"><span class="npc">Man in green and white: There are seven legends about Lord Mi&#8217;ihen&#8217;s statue&#8230; but they&#8217;re all so absurd!<br />
&nbsp;&#172;They say that they eyes follow you when you&#8217;re not looking, and that it gets up and walks around in the night! Silly, isn&#8217;t it?<br />
&nbsp;&#172;There&#8217;s a legend that Lord Mi&#8217;ihen&#8217;s sword still exists somewhere. I think it&#8217;s just an ancient myth.</span></span>""", """<p><span class="npc">Man in green and white: There are seven legends about Lord Mi&#8217;ihen&#8217;s statue&#8230; but they&#8217;re all so absurd!<br />
&nbsp;&#172;They say that they eyes follow you when you&#8217;re not looking, and that it gets up and walks around in the night! Silly, isn&#8217;t it?<br />
&nbsp;&#172;There&#8217;s a legend that Lord Mi&#8217;ihen&#8217;s sword still exists somewhere. I think it&#8217;s just an ancient myth.</span>""")

	html = html.replace('<span class="npc"> <a class="who sc-tooltip" data-image="../wp-content/uploads/2015/09/15chariss.jpg" data-desc="" href="../?attachment_id=221" target="screencap">Pious woman</a> (probably a temple-raised orphan; she never leaves it except during Yuna&#8217;s summoning)', '<span class="npc"> <a class="who sc-tooltip" data-image="../wp-content/uploads/2015/09/15chariss.jpg" data-desc="" href="../?attachment_id=221" target="screencap">Pious woman</a>')
	
	html = html.replace('<p><span class="npc"><a class="who sc-tooltip" data-image="../wp-content/uploads/2015/09/15chariss.jpg" data-desc="" href="../?attachment_id=221" target="screencap">Grieving woman</a> looking out to sea (possibly the one in the FMV)', '<p><span class="npc"><a class="who sc-tooltip" data-image="../wp-content/uploads/2015/09/15chariss.jpg" data-desc="" href="../?attachment_id=221" target="screencap">Grieving woman looking out to sea</a>')
	
	html = html.replace('<p><span class="npc"><a class="who sc-tooltip" data-image="../wp-content/uploads/2015/09/125nopants.jpg" data-desc="" href="../?attachment_id=264" target="screencap">Officer in need of pants</a>, W of Ochu', '<p><span class="npc"><a class="who sc-tooltip" data-image="../wp-content/uploads/2015/09/125nopants.jpg" data-desc="" href="../?attachment_id=264" target="screencap">Officer in need of pants</a>')
	
	html = html.replace('\nWoman in gold with brown leggings:','<p>Woman in gold with brown leggings:')
	html = html.replace('\nWoman in gold with brown leggings:','<p>Woman in gold with brown leggings:')
	html = html.replace('\nMan in white pants: Where have the Crusaders been hiding?','<p>Man in white pants: Where have the Crusaders been hiding?')
	html = html.replace('\nWoman in purple by vendor: What&#8217;s wrong', '<p>Woman in purple by vendor: What\'s wrong')
	
	html = html.replace('\nHorn player: Enjoy the beautiful','<p>Horn player: Enjoy the beautiful')
	html = html.replace('\nFrog drummer: If it','<p>Frog drummer: If it')
	
	html = html.replace('<div class="sc">The Gorge/Scar</div>', '<h4 class="sc">The Gorge/Scar</h4>')
	
	html = html.replace('<p>Fancy <a class="who sc-tooltip" data-image="../characters/womanB.jpg" data-desc="" href="../characters/womanB.jpg" target="screencap">woman in blue:</a>', '<p>Fancy <a class="who sc-tooltip" data-image="../characters/womanB.jpg" data-desc="" href="../characters/womanB.jpg" target="screencap">woman in blue</a>:')
	
	html = html.replace("""<span class="clue"><span class="npc">Blitzer against wall (Berrik): <span class="AB">My friend, he went to Baaj to explore. He told a story&#8230; In the deserted temple there, faintly the Hymn of the Fayth can be heard! Maybe it has something to do with the aeons I think.<br />
&nbsp;&#172;Baaj is a place of mystery. Mystery worth exploring, no?<br />
&nbsp;&#172;In ancient times a temple was in Baaj. Now it is a nest for fiend only. There is great treasure in the deserted temple, they say. But a great fiend lives there too, and guards the treasure.</span></span></span></p>""", """<span class="npc">Blitzer against wall (Berrik): <span class="AB">My friend, he went to Baaj to explore. He told a story&#8230; In the deserted temple there, faintly the Hymn of the Fayth can be heard! Maybe it has something to do with the aeons I think.<br />
&nbsp;&#172;Baaj is a place of mystery. Mystery worth exploring, no?<br />
&nbsp;&#172;In ancient times a temple was in Baaj. Now it is a nest for fiend only. There is great treasure in the deserted temple, they say. But a great fiend lives there too, and guards the treasure.</span></span></p>""")
	
	html = html.replace('in order from the right:','in order from the right-')
	
	soup = BeautifulSoup(html, 'html5lib')
	try:
		soup.find("a",{"target":"screencap","href":"../characters/noy.jpg"})["class"] = 'who'
	except:
		pass
	

	posts = soup.find('div', 'entry-content')
	
	# remove font objects
	#for tag in posts.find_all("font",recursive=True):
	#	tag.replace_with(tag.getText())
	
	def cleanDialogue(txt):
		txt = txt.replace("\n"," ")
		txt = txt.replace("¬"," ")
		txt = txt.replace("¬"," ")
		txt = txt.replace('“','"')
		txt = txt.replace('”','"')
		txt = txt.replace('’',"'")
		txt = txt.replace('‘',"'")
		txt = txt.replace(":","")
		txt = txt.replace("…"," ... ")
		txt = txt.replace("\\xa0", " ")
		txt = txt.replace("\xa0", " ")
		txt = re.sub(" +"," ",txt)
		txt= txt.replace(".entry-content","")
		txt = txt.replace('.entry-footer',"")
		if txt.startswith("-"):
			txt = txt[1:]
		txt = txt.strip()
		return(txt)
		
		
	def flatten(S):
		if S == []:
			return S
		if isinstance(S[0], list):
			return flatten(S[0]) + flatten(S[1:])
		return S[:1] + flatten(S[1:])
		
	def cleanName(txt):
		global previousCharNames
		txt = txt.replace("¬","")
		txt = txt.replace('’',"'")
		txt = txt.replace('“','"')
		txt = txt.replace('”','"')
		txt = txt.replace(">","")
		txt = txt.replace("¬"," ")
		txt = txt.strip()
		if txt.startswith("(") and txt.endswith(")"):
			txt = txt[1:-1]
		txt = txt.strip()
		
		# Sometimes the name in an <a> tag is re-used
		# later, but in a curtailed form
		# for example "Woman in long skirt" becomes just "Woman"
		# We only want to set the character name if this is not the case
		
		if txt == "Priest":
			return(txt)
		
		# (Yuna part, because there's also "Yunalesca", and not Tidus because "Tidus's Mom")
		matchingNames = [x for x in previousCharNames[-6:] if x.startswith(txt) and (not x.startswith("Yuna")) and (not x.startswith("Tidus")) and (not x.startswith("Luzzu"))]
		if len(matchingNames)>0:
			#if txt!=matchingNames[-1]:
			#	print(txt + " > " + matchingNames[-1])
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
			for gift in element.find_all("span",{"class":"gift"}):
				gift.extract()
			# For e.g. "[Buy items. | Leave.]"
			for choices in element.find_all("span",{"class":"choices"}):
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
		

# 	def mainCharacterParser(element,classList):
# 		# e.g. span class="T"
# 		mcOut = []
# 		thisCharName = ""
# 		if element is not None:
# 			
# 			bits = [lineRecogniser(line) for line in element]
# 			bits = [b for b in bits if not b is None]
# 					
# 			for line in element:
# 				if isinstance(line,bs4.element.NavigableString) or isinstance(line,str):
# 					txt = getTextFromUnknownObject(line)
# 					if txt.startswith(":"):
# 						txt = txt[1:]
# 					elif txt.count(":")>0:
# 						# (also captures lines ending in ":")
# 						thisCharName = txt[:txt.index(":")].strip()
# 						txt = txt[txt.index(":")+1:]
# 					dialogue = cleanDialogue(txt)
# 					if len(dialogue)>0:
# 						if thisCharName!="":
# 							mcOut.append({cleanName(thisCharName):dialogue})
# 						else:
# 							print("ERROR: No char name: ")
# 							print(element)
# 				elif line.name == "span" and "mov" in line.get("class"):
# 						mcOut.append({"ACTION":cleanName(thisCharName)+": "+ getTextFromUnknownObject(line)})
# 				elif line.name=="br":
# 					pass
# 				else:
# 					print("OTHER")
# 					print(element)
# 		return(mcOut)
			

		
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
	
	def backupNPCParser(element):
		global lastNPC
		
		for x in element:
			if getTextFromUnknownObject(x) == " ":
				x.extract()
		txt = getTextFromUnknownObject(element)
		lines = txt.split("\n")
		ret = []
		for line in lines:
			if line[:60].count(":")>0:
				charNames= [""]
				if line.index(":")>0:
					dialogue = cleanDialogue(line[line.index(":")+1:].strip())
					charNames = []
				# TODO: Add lastNPC part from "who" in cases like
				# [<a class="who">Crusader</a>, " lying just past the fork"]
					if line.startswith(" "):
						line = lastNPC + line
					
					for x in splitNames(line[:line.index(":")]):
						charNames.append(x)
				else:
					dialogue = cleanDialogue(line[1:])
					charNames = [lastNPC]
				ret += [{cleanName(charName):dialogue} for charName in charNames]
				lastNPC = charNames[-1]
			else:
				dialogue = cleanDialogue(line.strip())
				if dialogue.startswith("["):
					ret.append({"ACTION":dialogue})
				else:
					ret.append({lastNPC:dialogue})
		return(ret)
	
	# Split names by commas, except when commas are inside parentheses
	def repl(m):
		return('#' * len(m.group()))
	def splitNames(nameString):
		exceptions = ["Guado guard, green hair","Slumped Crusader, survivor of Operation Mi’ihen", "Stadium entrance guard, left (Biggs)", "Stadium entrance guard, right (Wedge)", "Crusader in red, white and blue", "Crusader in red, white, blue", "Guard for dock 4, slumped"]
		if nameString in exceptions:
			return([nameString])
		if any([nameString.count(x)>0 for x in ["red,","white,","blue,","yellow,"]]):
			return([nameString])
	
		# replace text inside parentheses with equal number of '#'
		nx = re.sub("\(.+?\)",repl,nameString)
		locationsOfCommas = [0] + [i for i, ltr in enumerate(nx) if ltr == ","]
		retNames = [nameString[i:j] for i,j in zip(locationsOfCommas, locationsOfCommas[1:]+[None])]
		retNames = [x.replace(",","").strip() for x in retNames]
		return(retNames)

	def npcParser(element):
		global lastNPC
		# Step 1: identify names	
		# Multiple NPCs can be defined
		whos = element.find_all("a",{"class":"who"})
		if len(whos)>0:
			# There are explicit <a> tags, so use those:
			for whox in whos:
				finalFantasy10WhoGallery[whox.get_text()] = whox.get("href")
			if (len(element.find_all(["p","ul"])))==0:
				return(backupNPCParser(element))
			else:
				bits = [lineRecogniser(x) for x in element]
				bits = [x for x in bits if not x is None]
				return(bits)
		else:
			# Plain text.
			# Check if there's a character name in plain text
			txt = getTextFromUnknownObject(element)
			if txt.count(":")==1 and txt.index(":") < 60:
				charNames = txt[:txt.index(":")].strip()
				charNames = splitNames(charNames)
				lastNPC = charNames[-1]
			elif txt.count(":")>1:
				# Multiple bits of dialogue, need to parse each element
				# (switch back to html elements)
				bits = [lineRecogniser(x) for x in element]
				bits = [x for x in bits if not x is None]
				if len(bits)>0:
					#lastNPC = bits[-1]
					return(bits)
				else:
					# Back off to parsing strings
					bits = [lineRecogniser(x) for x in txt.split("\n")]
					bits = [x for x in bits if not x is None]
					if len(bits)>0:
						return(bits)
					else:
						return(None)
			elif txt.startswith("["):
				charNames = ["ACTION"]
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
			lastNPC = charNames[-1]
		else:
			return(None)

	def ulParser(line):
		global FF10defaultCharacterName
		mainOut = []
		choice = []
		for bit in line:
			if bit.name== "li":
				if bit.get("class") is None:
					xx = [lineRecogniser(child) for child in bit.children]
					xx = [x for x in xx if not x is None]
					if len(xx)>0:
						choice += xx
				elif "choice" in bit.get("class"):
					if len(choice)>0:
						mainOut.append(choice)
					choice = [{FF10defaultCharacterName:cleanDialogue(bit.get_text())}]
				elif "reply" in bit.get("class"):
					for subline in bit:
						lx = lineRecogniser(subline)
						if lx is not None:
							if isinstance(lx,list):
								choice += flatten(lx)
							else:
								choice.append(lx)
			else:
				pass
		if len(choice)>0:
			#mainOut.append({"CHOICE":choice})
			mainOut.append(choice)
		return({"CHOICE":mainOut})	
		
	def divAltParser(lines):
		bits = flatten([lineRecogniser(x) for x in lines])
		bits = [x for x in bits if not x is None]
		opt = [cleanDialogue(x.get_text()) for x in lines.find_all("span",{"class":"tri"})]
		choices = []
		for bit in bits:
			# if text matches choices, make new 
			if any([txt in opt for txt in [x for x in bit.values()]]) or len(choices)==0:
				choices.append([])
			choices[-1].append(bit)
		return({"CHOICE":choices})
					
	def stringLineParser(line):
		global lastNPC
		txt = getTextFromUnknownObject(line)
		if txt.startswith(":") or txt.startswith("):"):
			if txt.startswith(")"):
				txt = txt[1:]
			charName = lastNPC
			dx = cleanDialogue(txt[1:])
			if len(dx)>0:
				return({cleanName(lastNPC):dx})
		elif txt.endswith("("):
			# (pass)
			txt = ""
		elif txt.count(":")>0:
			# (also captures lines ending in ":")
			charName = txt[:txt.index(":")].strip()
						
			if txt.startswith(" ") or any([charName.startswith(x) for x in ["outside", "by","in ","on ","beside ","at ","near ","not ","conversing ","barring ","with ","talking ","running ","standing ", ",", "("]]):
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
		avoid = ["[The", "and the","are running around and around the mast. ]"]
		if len(dx)>0 and not (dx in avoid):
			charName = cleanName(charName)
			lastNPC = charName
			return({charName:dx})
		else:
			return(None)
		
	def lineRecogniser(line):
		global lastNPC
		global FF10defaultCharacterName
		#print((line,fileName))
		
		if isinstance(line,bs4.element.NavigableString) or isinstance(line,str): # or string?
			# Raw line of dialogue, attribute it to the last NPC
			return(stringLineParser(line))
		elif line.name == "p":
			bitNames = [bit.name for bit in line]
			if not any([x in bitNames for x in ["span","a"]]):
				# Weird cluster with just raw text
				return(stringLineParser(line))
			elif "font" in bitNames:
				# Handle font object by just treating text line
				return(stringLineParser(line))
			else:
				# Recursive xxx
				lineParse = [lineRecogniser(x) for x in line]
				lineParse = [x for x in lineParse if x is not None]
				# TODO: unlist?
				if len(lineParse)>0:
					return(lineParse)
				else:
					return(None)

		elif line.name == "ul":
			return(ulParser(line))
		
		elif line.name == "div":
			choices = [lineRecogniser(bit) for bit in line]
			choices = [x for x in choices if x is not None]
			if len(choices)>0:
				choices = flatten(choices)
			if ("optional" in line.get("class")) or ("backtrack" in line.get("class")):
				return({"CHOICE":[[],choices]})
			elif "tri" in line.get("class"):
				return({"ACTION":line.get_text()})
			elif "alt" in line.get("class"):
				return(divAltParser(line))
			elif "sc" in line.get("class"):
				return({"LOCATION": line.get_text()})
			else:
				# Could be e.g. flashback
				return(choices)
		
		elif line.name == "span":
		
			if "bs" in line.get("class"):
				ret = [lineRecogniser(bit) for bit in line]
				return([x for x in ret if x is not None])
			elif "npc" in line.get("class"):
				return(npcParser(line))
			elif ("TN" in line.get("class") or "clue" in line.get("class")):
				dlg = line.get_text()
				dlg = dlg.replace("Narration:","").strip()
				dlg = cleanDialogue(dlg)
				return({"NARRATION":dlg,"_NARRATION":"True"})
			elif any([x in line.get("class") for x in ["stage","mov","tri"]]):
				return({"ACTION": cleanDialogue(line.get_text())})
			elif "choices" in line.get("class"):
				tx = line.get_text().replace("[","").replace("]","").split("|")
				if len(tx)>0:
					return({"CHOICE": [[{"Tidus":cleanDialogue(x)} for x in tx]]})
			elif "gift" in line.get("class"):
				return({"ACTION": "Gift : "+cleanDialogue(line.get_text())})
			else:
				return(npcParser(line))
				#return(mainCharacterParser(line,line.get("class")))
				
		elif ((line.name == "h3" or line.name == "h4") and ("where" in line.get("class") or "sc" in line.get("class"))):
			if "where" in line.get("class") and line.get_text()=="Monster Arena":
				FF10defaultCharacterName = "Monster Arena Guy"
			else:
				FF10defaultCharacterName = "Tidus"
			return({"LOCATION": cleanDialogue(line.get_text())})

		# In case we get a 'who' tag, just set the last npc name
		elif line.name == "a":
			if line.get("class") is None or "who" in line.get("class"):
				finalFantasy10WhoGallery[line.get_text()] = line.get("href")
				xx = line.get_text()
				if len(xx)>0:
					lastNPC = xx
				return(None)
			
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
	FF10SkipSection = False

	for child in posts.children:
		if child.name=="h4":
			if child.get_text()=="Bikanel":
				FF10SkipSection = True
			else:
				FF10SkipSection = False
		if not FF10SkipSection:
			parsedLine = lineRecogniser(child)
			if parsedLine is not None:
				if isinstance(parsedLine,list):
					parsedLine = flatten(parsedLine)
					out += parsedLine
				else:
					out.append(parsedLine)
	
	#open('tmp_'+ fileName[fileName.rindex("/")+1:]+'.txt','w').write(json.dumps({"text":out}))
	
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)


def createNPCImageGallery():
	# Write gallery of NPCs
	print("Creating gallery of NPCs")
	gallery= "<html><body>"
	for npc in finalFantasy10WhoGallery:
		srcx =finalFantasy10WhoGallery[npc]
		if not srcx is None:
			srcx = srcx.replace("..?","../?")
			srcx = srcx[srcx.index("/")+1:]
			imageURL = "http://auronlu.istad.org/ffx-script/"
			if srcx.startswith("?"):
				imageURL += "index.html" + srcx
				attachmentHTML =  urlopen(imageURL).read().decode('utf-8')
				bits = re.findall("http://auronlu.istad.org/ffx-script/wp-content/uploads/.+?.jpg'",attachmentHTML)
				if len(bits)>0:
					imageURL = '<img src="'+ bits[0][:-1] + '" max-height="600">'
				else:
					imageURL = '<a href="' + imageURL +  '">LINK</a>'
				#<img width="98" height="300" src="http://auronlu.istad.org/ffx-script/wp-content/uploads/2015/08/5woman-glasses-98x300.jpg" class="attachment-medium size-medium" alt="Woman with Quistis glasses">
			else:
				imageURL += srcx
				imageURL = '<img src="'+ imageURL + '" max-height="600">'
			gallery += npc + "</br>" + imageURL + "</br></br>"
	gallery += "</body></html>"
	o = open("../data/FinalFantasy/FFX_B/NPC_Gallery.html",'w')
	o.write(gallery)
	o.close()


def postProcessing(out):
	finalOut = []
	for o in out:
		if not o is None and o!= {"slumped": "Seems to have been put to sleep."}:
			if isinstance(o,list):
				finalOut += o
			else:
				finalOut.append(o)
	# Create NPC image gallery
	if(False):
		createNPCImageGallery()

	# Fix in-line alternatives
	finalOut2 = []
	for o in finalOut:
		charName = [key for key in o if not key.startswith("_")][0]
		if not charName in ["ACTION","CHOICE","LOCATION","COMMENT","SYSTEM"]:
			if o[charName].count("(If")>0:
				parts = re.split("(\(.+?\))",o[charName])
				# Pre option
				if len(parts[0].strip())>0:
					finalOut2.append(parts[0].strip())
				# Options
				choice = {"CHOICE": []}
				it = iter(parts[1:])
				pairs = zip(it,it)
				for pair in pairs:
					choice["CHOICE"].append([{"ACTION":pair[0]},{charName:pair[1]}])
				finalOut2.append(choice)
			else:
				finalOut2.append(o)
		else:
			# Ordinary line
			finalOut2.append(o)
			
# 	def walkNarration(outx):
# 		for line in outx:
# 			if "CHOICE" in line:
# 				for choice in line["CHOICE"]:
# 					walkNarration(choice)
# 			else:
# 				k = [x for x in line if not x.startswith("_")][0]
# 				print(line)
# 				origDlg = line[k]
# 				if origDlg.startswith("Narration:"):
# 					# Swap lines
# 					line.pop(k)
# 					line["Tidus"] = origDlg.replace("Narration:","").strip()
# 					line["_NARRATION"] = "True"
	#walkNarration(finalOut2)
	
	finalOut3 = []
	for line in finalOut2:
		if line == "Let's begin, shall we?":
			finalOut3.append({"Chocobo trainer":"Let's begin, shall we?"})
		else:
			finalOut3.append(line)
	
	# Take out the very final entry, which is actually
	# part of FFX-2
	finalOut4 = []
	for line in finalOut3:
		if line == {"LOCATION": "Gippal’s Sphere (FFX-2)"}:
			# stop collecting after this
			break
		else:
			finalOut4.append(line)
			
	# remove some duplicated lines
	toRemove = [{"LOCATION": "Chambers of the Fayth"},
				{"ACTION": "[After Mika \"reveals\" that Yuna's not a traitor, you can re-visit temples and talk to the Fayth within. In the remaster, you'll have to bat aside a few Dark Aeons (Besaid, Macalania and the Cavern of the Stolen Fayth) first. ]"},
				{"Valefor in Besaid": "Sin is cursed. Sin prays. It curses its form, it prays for dissolution. Sin sees dreams of its own destruction. Sin is looking at us. We live in a fading echo of time left us by the destroyer. Free him from Yu Yevon. Free him — the fayth that has become Sin."},
				{"Ifrit in Kilika": "Sin swam in the sea near Zanarkand. Perhaps the waking dream eased its suffering. Your father touched Sin and became real that night, foundering in the seas of Spira. How sad now, that he is caught in the tragic spiral. He is Sin. He is lost."},
				{"Ixion in Djose": "For a long time, we had forgotten how to go forward. You reminded us we must go forward. Yes, we must run. Let us go, you who share our dreaming. Come, and we will run till the dream's end."},
				{"Shiva in Macalania": "Should the dreaming end, you too will disappear–Fade into Spira's sea, Spira's sky. But do not weep, nor rise in anger. Even we were once human. That is why we must dream. Let us summon a sea in a new dream world. A new sea for you to swim."},
				{"Yojimbo in Cavern of the Stolen Fayth": "You are a fading dream, but one touched by reality. Spira will not forget its reality, nor the one who saved it. Run, dream; run on. Pass beyond the waking, and walk into the daylight."},
				{"Magus Sister 1": "Why couldn't we see to stop the dreaming? Why did we stay on in Spira? We had forgotten for so long. We had forgotten to move forward. We had forgotten to change."},
				{"Guard at lefthand exit": "Al Bhed in"},]
	finalOut5 = []
	for line in finalOut4:
		if not line in toRemove:
			finalOut5.append(line)

	#o = open("../data/FinalFantasy/FFX_B/tmp.txt",'w')
	#o.write(json.dumps({"text":finalOut2}, indent = 4))
	#o.close()
	
	return(finalOut5)
		