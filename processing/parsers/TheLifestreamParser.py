#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import json, re


def cleanText(txt):
	txt = txt.replace("’","'")
	txt = txt.replace("“",'"')
	txt = txt.replace("”",'"')
	txt = txt.replace("…","... ")
	txt = txt.replace("•","")
	txt = txt.strip()
	txt = txt.replace("\n"," ")
	txt = re.sub(" +"," ",txt)
	return(txt)


def paraParser(bit, avoidChars= ["Research Log","ATTN"]):
	outx = []
	# we can't just iterate over children, because some children are em tags
	# so build a list of strings first
	lines = []
	justDidEm = False
	if isinstance(bit,str):
		# (already processed into lines)
		lines = [x for x in bit.split("\n") if len(x.strip())>0]
	else:
		for lx in bit.children:
			if isinstance(lx,str):
				if justDidEm:
					lines[-1] += lx
					justDidEm = False
				else:
					# Verstael has some odd dialogue like
					# Verstael: <br/> Research log:
					if len(lines)>0 and lines[-1].endswith(":") and len(lines[-1])<20:
						lines[-1] += lx.strip()
					# TV lines are formatted a bit differently
					elif len(lines)>0 and lines[-1] in ["Newscaster","Ravus"]:
						lines[-1] += ":" + lx.strip()
					else:
						lines.append(lx.strip())
			else:
				if lx.name=="em" or lx.name=="a":
					if len(lines)>0:
						lines[-1] += lx.getText()
					else:
						lines.append(lx.getText().strip())
					justDidEm = True
	# Now process each line
	for lx in lines:
		if(lx.startswith("[")):
			if lx.startswith("[Note"):
				# Sometimes the subtitle and audio dialogue differs
				extraDialogue = re.search(' has ([A-Za-z \-]+?) say “(.+?)”',lx)
				if extraDialogue:
					charName = extraDialogue.group(1)
					charName = charName.replace(' first',"")
					dialogueText = extraDialogue.group(2)
					# Some of this is just adding an extra word
					if len(outx)==0 or isUniqueDialogue(dialogueText,charName,outx[-1]):
						# unique line of dialogue
						if (not charName in avoidChars) and len(cleanText(dialogueText))>0:
							outx.append({charName:cleanText(dialogueText), "_Subtitle":""})
					else:
						# re-transcription of previous line, so replace
						prevDial = [outx[-1][x] for x in outx[-1] if not x.startswith("_")][0]
						outx[-1] = {charName:cleanText(dialogueText), "_Subtitle":prevDial}
				else:
					tt = cleanText(lx.strip()[1:-1])
					if len(tt)>0 and tt!="collapse":
						outx.append({"NARRATIVE":tt})
			else:
				tt = cleanText(lx.strip()[1:-1])
				if len(tt)>0 and tt!="collapse":
					outx.append({"NARRATIVE":cleanText(lx.strip()[1:-1])})
		elif lx.startswith("—"):
			if len(outx)>0:
				lastLine = outx[-1]
				lastText = lastLine[[x for x in lastLine if not x.startswith("_")][0]]
				if lastText!="---":
					outx.append({"NARRATIVE":"---"})
			else:
				outx.append({"NARRATIVE":"---"})
		else:
			# remove stuff between brackets
			lx = re.sub(r'\([^\)]*\)', '', lx).strip()
			if len(lx)>0:
				if lx.count(":")>0 and lx.index(":")<20:
					charName = lx[:lx.index(":")].strip()
					txt = lx[lx.index(":")+1:].strip()
					if not charName in avoidChars and len(cleanText(txt))>0:
						outx.append({charName:cleanText(txt)})
				else:
					lx = lx.replace("_","")
					if len(lx)>1:
						outx.append({"SYSTEM": cleanText(lx)})
	return(outx)
	
def levenshtein_dist(s1, s2):
	if len(s1) < len(s2):
		return levenshtein_dist(s2, s1)
    # len(s1) >= len(s2)
	if len(s2) == 0:
		return len(s1)
	previous_row = range(len(s2) + 1)
	for i, c1 in enumerate(s1):
		current_row = [i + 1]
		for j, c2 in enumerate(s2):
			insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
			deletions = current_row[j] + 1       # than s2
			substitutions = previous_row[j] + (c1 != c2)
			current_row.append(min(insertions, deletions, substitutions))
		previous_row = current_row
	return previous_row[-1]
	
def isUniqueDialogue(dialogueText,charName,prevLine):
	# Sometimes, dialogue is coded twice with the second time
	#  just adding in "ah," or "oh,".
	# Returns True if current line is unique
	prevCharName = [x for x in prevLine if not x.startswith("_")][0]
	prevLineDialogue = prevLine[prevCharName]
	dtLower = dialogueText.lower().replace(",","").replace(".","").replace("!","").replace("?","").strip()
	dtLower = cleanText(dtLower)
	ptLower = prevLineDialogue.lower().replace(",","").replace(".","").replace("!","").replace("?","").strip()
#	print("---")
#	print(ptLower)
#	print(dtLower)
#	print(levenshtein_dist(ptLower,dtLower)/max(len(ptLower),len(dtLower)))
	# Check if previous line is a substring of the current line
	if (ptLower in dtLower) or (dtLower in ptLower):
#		print("Retranscription")
		return(False)
	# Check if line only differs by a small amount (e.g. "an" etc.)
	if len(dtLower) > 10 and levenshtein_dist(ptLower,dtLower)/max(len(ptLower),len(dtLower))<0.1:
#		print("Retranscription")
		return(False)
	# Also cases like this where not substring and levenshtein dist is high
	# There are also cases
	# ptLower = i've still got a few tricks up my sleeve too ain't no way i'm backing down now
	# dtLower = i’ve still got some tricks up my sleeve too
	# OR
	#ptLower  ="the rock of ravatogh lies in the west of cleigne it's got a real distinct shape you can see it from miles away"
	#dtLower = "the rock of ravatogh lies to the west of cleigne"
	ptWords = ptLower.split(" ") 
	dtWords = dtLower.split(" ")
	if sum([pt in dtWords for pt in ptWords])>5 or sum([dt in ptWords for dt in dtWords])>5:
#		print("Curtailing")
		return(False)
#	print("Unique")
	return(True)


def parseFile(fileName,parameters={},asJSON=False):
	# For this site: https://finalfantasy.fandom.com/wiki/Final_Fantasy_VI_SNES_script#Kefka.27s_Tower_.2F_Ending
	# the dialogue is split into main narrative and optional dialogue.
	# At the moment, everything is just dumped into the data.json
	# We could match up each optional dialogue to its section, then add it in as e.g.:
	# 		{"CHOICE": [
	#			[],
	#			[{"Cloud": "Buy one "}]
	#       ]},

	o = open(fileName)
	d = o.read()
	o.close()

	d = d.replace("Codename:","Codename-")
	d = d.replace("<em>is</em>","is")
	d = d.replace("as follows:","as follows ...")
	d = d.replace('Troopers:','Troopers-')
	d = d.replace('Infants:','Infants-')
	d = d.replace('Characteristics:',"Characteristics-")
	#d = d.replace('he was right:','he was right-')
	d = d.replace("Date of Publication:","Date of Publication-")

	script = BeautifulSoup(d, 'html.parser')
	script = script.find("div",{"class":"article-content"})
	
	out = []
	startedParse = False
	
	for bit in list(script.children):
		im = bit.find("img")
		if im!=-1:
			startedParse = True
		if startedParse:
			# if charName is None, and it's a bit of text, this is narrative
			if bit.name=="p":
				out += paraParser(bit)
			elif bit.name == "center" or bit.name=="aside":
				# End of the script
				break
			else:
				if bit.name=="div":
					if 'sp-wrap' in bit.get("class") and 'sp-wrap-default' in bit.get("class"):
						# optional dialogue
						inner = bit.find("div",{"class": "sp-body folded"})
						# Cut the inner part into sections. (the "p" is not always reliable)
						for br in inner.find_all("br"):
						    br.replace_with("\n")
						innerText = inner.get_text(separator="\n")
						innerText = [x.strip() for x in innerText.split("\n—") if len(x.strip())>0]
						#print(innerText)
						#optionalBits = [paraParser(x) for x in inner.children if x.name=="p"]
						optionalBits = [paraParser(x) for x in innerText]
						
						for optionalBit in optionalBits:
							if len(optionalBit)>1:
								out.append({"CHOICE":
										[[], optionalBit]
									})
							elif len(optionalBit)==1:
								charName = [x for x in optionalBit[0].keys() if not x.startswith("_")][0]
								if charName == "NARRATIVE" and optionalBit[0]["NARRATIVE"].startswith("Note:"):
									if "CHOICE" in out[-1]:
										out[-1]["CHOICE"][1] += optionalBit
								else:
									out.append({"CHOICE":[[],optionalBit]})
			


	
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)

# Post-processing:
# Deal with coded choices
# [A prompt appears to select either “Accept” or “Decline”]
# However, this isn't always followed by all the options, e.g.:
# [A prompt appears to select either “Proceed” or “Turn back”]
# (upon selecting “Proceed”)
#[Noctis turns to the other Chocobros]
#Noct: I’ll see you guys later.
#Gladio: You go give ’em hell. We’ll do the same on our end.
#  ---- end of <p> ----
#[Noct squeezes through a narrow crevasse to join up with Cor]
#Cor: Once we’re in, we launch our ambush, pushing out while support pushes in, crushing the enemy from both sides.

def postProcessing(out):
	#
	def getCharText(line):
		charName = [x for x in line if not x.startswith("_")][0]
		if charName=="CHOICE":
			return((charName, ""))
		else:
			return((charName,line[charName]))
	
	finalOut = []
	choices = []
	subchoice = []
	numPromptOptions = 0
	inChoice = False
	for line in out:
		charName,charText = getCharText(line)
		if inChoice:
			if charText.startswith("---"):
				numPromptOptions -=1
				if numPromptOptions==0:
					# End of options
					choices.append(subchoice)
					finalOut.append({"CHOICE":choices})
					inChoice = False
					choices = []
					subchoice = []
				else:
					choices.append(subchoice)
					subchoice = []
			else:
				if charText!="---":
					subchoice.append(line)
		else:
			# Not in choice		
			if charText.count("prompt appears") > 0 or charText.count("A prompt asking") > 0:
				inChoice = True
				# some prompt lines can include a question as well as options
				# [A prompt appears asking “Head out?”; the player can select either “Yes” or “No”]
				opt = []
				if charText == 'A prompt appears to select either Ignis, Gladiolus or Prompto':
					opt = ["Ignis","Gladiolus","Prompto"]
				else:
					charText = charText[charText.replace("can choose","can select").index("select"):]
					opt = re.findall('".+?"',charText)
				
				if opt == ['"Proceed"', '"Turn back"']:
					# Not really a choice
					numPromptOptions = 0
					inChoice = False
					finalOut.append(line)
					finalOut.append({"NARRATIVE":"On selecting \"Proceed\""})
				else:
					numPromptOptions = len(opt)+1
					finalOut.append(line)
			else:
				finalOut.append(line)
				
	for line in finalOut:
		charName,charText = getCharText(line)
		if charName=="CHOICE" and len(line["CHOICE"])==2:
			ks = []
			for x in line["CHOICE"][1]:
				ks += [y for y in x]
			if "Dave" in ks and "NARRATIVE" in ks and "SYSTEM" in ks:
				# TODO: Put in correct
				line["CHOICE"] = [[],
						[{"NARRATIVE": "Note: Starting with this quest and not changing until Dave's final quest, \"The Witch of the Woods,\" all of his lines when beginning a quest will be randomly selected from either the line above or one of the following"},
						{"Dave": "We meet again. You stickin' around these parts for a spell? Could use your help diggin' up some dog tags."}],
					[{"Dave": "Howdy. Just heard word of another lost tag. Don't know where you boys are headed, but would y'all mind pickin' it up if it's on your way?"}],
					[{"Dave": "Howdy, boys. If y'all happen to stumble across another tag out there in the field, do me a favor and bring it my way."}],
					[{"Dave": "Howdy, boys. Say, if you could take a little time out, would you mind helpin' me track down some more tags?"}]]
				
	## Fix newscaster:
	def editNewscaster(line,prevLine):
		if "SYSTEM" in prevLine:
			if prevLine["SYSTEM"] =='Newscaster':
				return({"Newscaster":line["SYSTEM"]})
		return(line)
	
	def iterateEditNewscaster(lines):
		if len(lines)>0:
			for i in range(len(lines)-1):
				lines[i+1] = editNewscaster(lines[i+1],lines[i])
		return(lines)
	
	for i in range(len(finalOut)):
		if "CHOICE" in finalOut[i]:
			finalOut[i] = {"CHOICE":[iterateEditNewscaster(lx) for lx in finalOut[i]["CHOICE"]]}
		elif i>0:
			finalOut[i] = editNewscaster(finalOut[i],finalOut[i-1])
			
	# Swap lines so that the dialogue reflects the audio
	audioDiffs = {
		"Yeah. I betcha she'd really enjoy that.": "Hmm, Yeah. I betcha she'd really enjoy that.",
		"And then they jump out!": "And then they jump out! (shivers)",
		"Perhaps you ought to rest a while.": "Hmm, perhaps you ought to rest a while.",
		"Got out while you could, huh? Bad stuff's goin' on down there. You need cash? ‘Cause I need people. What d'ya say? The job's yours, if you're willin' and able.": "Got out while you could, huh? Bad stuff's goin' on down there. You need cash? ‘Cause I need people. What d'ya say? The job's yours, if you're willin' and able. The job's yours, if you're willing and able.",
		"Something about her \"baby.\"":"Iunno, something about her \"baby.\"",
		"Whereare your friends? You don't think they ran off without you?": "Where are your friends? You don't think (gasp) they ran off without you?",
		"Rejection hurts, doesn't it?": "Aw, rejection hurts, doesn't it?",
		"You just keep on telling yourself that": "You just keep on telling yourself that. This was such a great idea. Come on. Let's go show the others"
	}
	def walkAudioDiffs(outx):
		for line in outx:
			if "CHOICE" in line:
				for choice in line["CHOICE"]:
					walkAudioDiffs(choice)
			else:
				k = [x for x in line if not x.startswith("_")][0]
				origDlg = line[k]
				if origDlg in audioDiffs:
					# Swap lines
					line[k] = audioDiffs[origDlg]
					if not "_Subtitle" in line:
						line["_Subtitle"] = origDlg
	walkAudioDiffs(finalOut)
	
	return(finalOut)
	
	
	
	
	
	
	
	
	
	
	
	
	
	