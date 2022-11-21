from bs4 import BeautifulSoup, NavigableString
import json,re,copy



# Some characters have the same name:
#[The three soldiers run into the next screen, a bunch of burning grass lighting the battle-ready mood.]
#SeeD: (Where am I?)
#SeeD: (Dream?)
#SeeD: (?)


# TODO:
# "The [Central Square] is up ahead. 

def parseFile(fileName,pp,asJSON=False):

	def cleanLine(txt):
		txt = txt.replace("#","")
		txt = re.sub("\.\.\.([A-Z])","... \\1",txt)
		txt = re.sub("^:","",txt)
		txt = txt.replace("_"," ")
		txt = txt.replace('"',"")
		txt = txt.replace('\n'," ")
		txt = re.sub(" +"," ",txt)
		# replace square brackets with round brackets
		txt = txt.replace("[","(").replace("]",")")
		txt = txt.strip()
		
		for x in re.findall("\(.+?\)",txt):
			if not x in pp["parentheticalsThatShouldStayInParentheses"]:
				txt = txt.replace(x,x[1:-1])
		
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
		
		# Divide parts
		#print("###")
		#print(txt)
		initialLine = txt[:txt.index("R1 -->")]
		p2SplitText = "R1:"
		p2 = ""
		p3 = ""
		if txt.count(p2SplitText)==0:
			p2SplitText = "R1 ("
		if txt.count(p2SplitText)==0:
			# Raw choices without responses
			p2 = txt[txt.index("R1 -->"):]
		else:
			p2 = txt[txt.index("R1 -->"):txt.index(p2SplitText)]
			p3 = txt[txt.index(p2SplitText):]
		
		outx = []
		# Initial line
		initiatingCharName, dialogue = initialLine.split(":",1)
		outx.append({initiatingCharName: cleanLine(dialogue)})
		
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
			#global seenIDs
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
									{"Squall": opText},
									{"GOTO": decisionID + ":" +idx}])
						else:
							# Embed
							if idx in options:
								embed = options[idx]
								seenIDs.append(idx)
								cx = parseResp(embed)
								# "Squall" here is the player option
								nextChoices.append([{"ACTION": "Player chooses '"+opText+"'"}]+cx)
							else:
								print("Can't find "+idx)
								print(line)
					# If there's just one option, it's not really a choice
					if len(nextChoices)==1:
						choiceBits += nextChoices[0]
					else:
						# Otherwise, return a choice
						choiceBits.append({"CHOICE":nextChoices})
			return(choiceBits)


		# Main parsing bit
		choices = []
		#global seenIDs
		seenIDs = []
		for rID in opIDList:
			if not rID in seenIDs:
				seenIDs.append(rID)
				respBits = options[rID]
				choiceBits = parseResp(respBits)
				#print(choiceBits)
				choices.append(choiceBits)
		outx.append({"CHOICE": choices})
		return(outx)
		
		
		
################
### Main loop		
	o = open(fileName)
	d = o.read()
	o.close()
	

	#soup = BeautifulSoup(d, 'html.parser')
	# Parsing with html5lib so that p tags are closed
	soup = BeautifulSoup(d, "html5lib")
	script = soup.find('div', id='faqtxt')
	
	script = script.getText()
	
	startCue = "01. Post-fight, Infirmary, Classroom, Main Gate     "
	endCue = "THE END"
	script = script[script.index(startCue):script.index(endCue)]
	
	script = script.replace("A feather floats down","[A feather floats down")
	script = script.replace("At a festival, Irvine is dancing","[At a festival, Irvine is dancing")
	script = script.replace("After the credits, Rinoa is shown","[After the credits, Rinoa is shown")
	script = script.replace('Raijin: "Not bad, Squall!','\nRaijin: "Not bad, Squall!')
	script = script.replace("NOTE: For R3, it's one", "        NOTE: For R3, it's one")
	script = script.replace("NOTE: R3 is from", "        NOTE: R3 is from")
	script = script.replace('Are you ready?"\n\nSquall: R1 --> (Yes)','Are you ready?"\n      R1 --> (Yes)')
	script = script.replace('"The GF in the back of the cavern','Caraway\'s Guard: "The GF in the back of the cavern')
	script = script.replace('"I have no more hints."','Caraway\'s Guard: "I have no more hints."')
	script = script.replace('"You\'re ready, right?"','Squall: "You\'re ready, right?"')
	script = script.replace('"I\'m not going to','Squall: "I\'m not going to')
	script = script.replace('Laguna "Whoa!"','	Laguna: "Whoa!"')
	script = script.replace('            like the only option. \n','            like the only option. ')
	script = script.replace("R1 [-]","R1 (ACTION): \n\n [-]")
	
	for i in range(9):
		script = script.replace("\n            "+str(i+1), "\n            R"+str(i+4) + " --> ")
	script = script.replace("Victory is ours... That's it.\"",'Victory is ours... That\'s it."' + "".join(["\n\n     R"+str(i+4) + ':""' for i in range(9)]))
	
	script = script.replace("The Status Screen displays", "\n\n       SYSTEM:The Status Screen displays")
	script = script.replace("Alright, let's go!","\n\n      Quistis: Alright, let's go!")
	script = script.replace("\n____","\n\nX")
	script = script.replace("R4 --> 40 min",'R4 --> 40 min\n\n   R1:""\n\n   R2:""\n\n   R3:""\n\n   R4:""')
	
	# Split simultaneous lines
	script = re.sub('"\n( *[A-Za-z]+ ?[A-Za-z]+:)','"\n\n\\1',script)
#	script = script.replace('Officer: "Ughhhh!"\nSoldier:', 'Officer: "Ughhhh!"\n\nSoldier:')
#	script = script.replace('Security Guard: "This way!!!"','Security Guard: "This way!!!"\n')
	
	script = re.sub("####+","[Break]",script)
	
	# This inserts "GOTO" commands
	script = re.sub("\[(Same as R([1-9]).*?)\]", "\n   R\\2 --> (\\1)", script)
	#script = script.replace(": [Same as", " (GOTO): ")
	
	#open("tmp.txt",'w').write(script)
	
	parts = re.split("\n\n([A-Za-z\[])",script)
	parts = parts[1:]
	
	parts = [x+y for x,y in zip(parts[::2],parts[1::2])]

	out = []
	choices = []
	choiceIDCounter = 0

	for part in parts:
		#print(part)
		#print("***************")
		
		if part.startswith("__"):
			#ÊLocation
			part = part.replace("_","")
			part = re.sub("--+","",part)
			part = re.sub("\[.+?\]","",part).strip()
			out.append({"LOCATION": part})
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
			# TODO: Squall monologue in parentheses
			
			if len(re.findall("  +R[0-9][0-9]? *-->", part))>0:
				# decision
				choiceIDCounter += 1
				out += parseDecision(part,"D"+str(choiceIDCounter))
			else:
				charName, dialogue = part.split(":",1)
				charName = cleanCharName(charName)
				out.append({charName: cleanLine(dialogue)})
			

	return(out)

#---


def postProcessingXX(out):
	def getAllCharacterTexts(var, excludeKeys=["ACTION","CHOICE","LOCATION","COMMENT","SYSTEM","GOTO","NARRATIVE","STATUS"],getNames=False):
		if isinstance(var,dict) or isinstance(var,list):
			for k in var:
				if isinstance(var, dict):
					v = var[k]
					if not (k in excludeKeys or k.startswith("_")):
						if getNames:
							yield (k,v)
						else:
							yield(v)
					for result in getAllCharacterTexts(v,excludeKeys,getNames):
						yield result
				elif isinstance(var, list):
					for result in getAllCharacterTexts(k,excludeKeys,getNames):
						yield result
	txts = getAllCharacterTexts(out)
	seenX = []
	for t in txts:
		for x in re.findall("\(.+?\)",t):
			if not x in seenX:
				seenX.append(x)
				print(x)
	
	return(out)