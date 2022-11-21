from bs4 import BeautifulSoup
import json, re





def postProcessing(out):

	def cName(o):
		return([n for n in o if not n.startswith("_")][0])
	def getDialogue(o):
		return(o[cName(o)])

	def parseAlternativeLines(out):
		choiceIndices = []
		ix = 0
		for i in range(len(out)):
			if out[i]=={"ACTION":"Or:"}:
				#print("OR!")
				startLine = i
				# Search backwards until we find a line by Guybrush (include it)
				#  or an action (don't include it)
				while startLine>0:
					if cName(out[startLine-1])=="ACTION":
						break
					elif cName(out[startLine-1])=="Guybrush":
						startLine -= 1
						break
					else:
						startLine -= 1
				# Search forwards until we find an action (ignoring actions with text in 'skipLines')
				skipLines = ["Wally pauses"]
				breakLines = [
					"No. The value of the ring",  # This is the voodoo priestess rejoining the optional dialogue
												 # see https://youtu.be/cbhmWFSTl0k?t=70 and https://youtu.be/y3UuLQmovz4?t=679
					"What was that?", # Van Helgen's rejoiner
					"We sailed for two years", # Bill's rejoiner https://youtu.be/JcqyjuTaudA?t=2503
					"All right. In you go."
					]
				endLine = i+1
				#print("Look ahead")
				while endLine < (len(out)-1):
					#print(out[endLine+1])
					notInSkipLines = not (any([getDialogue(out[endLine + 1]).startswith(x) for x in skipLines]))
					notOr = (not getDialogue(out[endLine+1])=="Or:")
					lineInBreakLines = (any([getDialogue(out[endLine + 1]).startswith(x) for x in breakLines]))
					if (cName(out[endLine + 1])== "ACTION" and notInSkipLines and notOr) or lineInBreakLines:
						#print("BREAK!")
						break
					endLine += 1
				choiceIndices.append((startLine,endLine))
		
		# Now we have the indices of choices, add everything:
		endLineIndices = [endLine for startLine,endLine in choiceIndices]
		out2 = []
		choices= [[]]
		for i in range(len(out)):
			if any([i >= startLine and i<=endLine for startLine,endLine in choiceIndices]):
				if out[i]=={"ACTION":"Or:"}:
					choices.append([])
				else:
					choices[-1].append(out[i])
				if i in endLineIndices:
					out2.append({"CHOICE":choices})
					choices= [[]]
			else:
				out2.append(out[i])					
		return(out2)
					
	# Main post processing loop
	out2 = []
	for o in out:
		if isinstance(list(o.values())[0],str):
			if not list(o.values())[0].startswith("THE CURSE OF MONKEY ISLAND STARRING"):
				out2.append(o)
		else:
			out2.append(o)
	out2 = parseAlternativeLines(out2)
	return(out2)

def parseFile(fileName,parameters={},asJSON=False):

	def cleanLine(txt, isDialogue=False):
		txt = txt.replace("\n"," ").replace("_"," ").replace("|"," ").replace("/","").replace("[","").replace("]","").replace("*","")
		txt = txt.strip()
		if(isDialogue):
			if txt.count("NOTE:")>0:
				txt = txt[:txt.index("NOTE:")]
	
		# Remove lines that start with parentheses and have nothing else
		txt = re.sub(" +"," ",txt)
		txt = re.sub("\\-+","-",txt)
		txt = txt.replace("<","(").replace(">",")")
		return(txt)
	


	def getOut(charName,dialogueText):
		dx = re.sub("\\(.+?\\)","",cleanLine(dialogueText)).strip()
		if len(dx)==0:
			return({"ACTION":cleanLine(dialogueText)})
		else:		
			dialogueText = cleanLine(dialogueText,True)
			fullText = ""
			if dialogueText.count("("):
				fullText = dialogueText
				dialogueText = re.sub(r"\(.*?\)", "", dialogueText)
				dialogueText = re.sub(" +"," ",dialogueText)
				return({charName:cleanLine(dialogueText,True), "_withCue":fullText})
			else:
				return({charName:cleanLine(dialogueText,True)})


	html_= open(fileName,'r', encoding = 'utf8')
	soup = BeautifulSoup( html_, "html.parser")
	text = soup.find("div", {"id": parameters["textDivId"]})
	text = "\n\n".join([x.get_text() for x in text.children])
	text = text[text.index(parameters["startText"]):text.index(parameters["endText"])]

	# Manual fixes so that parser doesn't get confused
	text = text.replace("-- Age: Twenty.","    Age- Twenty.")
	text = text.replace("my/me","me")
	text = text.replace("the/me","me")
	text = text.replace("[sic]"," ")
	for rep in ["for","available","do him any good","but not limited to",'things',"Island 2","appears","time to ask yourself","Goodsoup Presents","PATIENTS"]:
		text = text.replace("\n"+rep+":","\n"+rep+".")

	linesIn = text.split("\n\n")
	
	# split into actual bits first
	lines = []
	for line in linesIn:
		bits = re.split("\n *([A-Za-z0-9 \\-\\.™ñ#]+:)",line)
		if len(bits)>1:
			bits = [bits[0]]+["".join(x) for x in zip(bits[1::2],bits[2::2])]
		lines += bits
	
#	for l in lines:
#		print(l)
#		print("---")
	
	out =[]
	charName = ""
	dialogueText = ""
	actionText = ""
	for line in lines:
		if len(line.strip())<2:
			pass
		nameLen = 0
		dialogLen = 0
		if line.count(":")>0:
			nameLen = len(line[:line.index(":")].strip())
			dialogLen = len(line[line.index(":"):].strip())
		if re.match("[A-Za-z0-9 \\-\\.™ñ#]+:",line) and (dialogLen>3) and (nameLen>2) and (nameLen < 21):
			
			if len(cleanLine(actionText))>1:
				out.append({"ACTION":cleanLine(actionText)})
				actionText = ""
			if len(dialogueText)>0:
				out.append(getOut(charName,dialogueText))
				dialogueText = ""
		
			if line.strip().startswith("Part") or line.strip().startswith("Last Part"):
				out.append({"ACTION":cleanLine(line)})
			else:
				charName = line[:line.index(":")].strip()
				dialogueText = line[line.index(":")+1:].strip()
		elif line.startswith("  ") and not line.count("___")>0 and not line.count("|")>0:
			dialogueText += " " + line.strip()
		else:
			# Line of action description
			if len(dialogueText)>0:
				out.append(getOut(charName,dialogueText))
				dialogueText = ""
			actionText += " " + line.strip()
				
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)