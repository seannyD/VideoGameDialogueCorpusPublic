# TODO:
# Get list of dialogue to check who is speaking.

# TODO:
# Transitions

# TODO:
# Some parts have no text, they are just structures for other parts
# We probably have to reconstruct this using graphs

# +-[entry #48]
#   speaker: variable_1
#   listener: variable_2
#   +-[reply #24]
#     listener: variable_3
#     +-[entry #49]
#     | speaker: variable_1
#     | listener: variable_2
#     | +-[reply #25]
#     |   listener: variable_3
#     |   +-[entry #50]
#     |   | speaker: variable_1
#     |   | listener: variable_2
#     |   | +-[reply #26]
#     |   |   listener: variable_3
#     |   |   +-*** see entry #51 ***
#     |   |   +-*** see entry #52 ***
#     |   |   +-*** see entry #53 ***
#     |   |   +-*** see entry #54 ***
#     |   |   +-*** see entry #55 ***
#     |   |   +-*** see entry #56 ***
#     |   |   +-*** see entry #57 ***
#     |   +-[entry #58]
#     |     speaker: variable_1
#     |     listener: variable_2
#     |     +-[reply #27]
#     |       listener: variable_3
#     |       +-*** see entry #59 ***
#     |       +-*** see entry #60 ***
#     |       +-*** see entry #61 ***
#     |       +-*** see entry #62 ***
#     |       +-*** see entry #63 ***
#     |       +-*** see entry #64 ***
#     |       +-*** see entry #65 ***
#     |       +-*** see entry #66 ***
#     +-[entry #67]
#       speaker: variable_1
#       listener: variable_2
#       +-[reply #28]
#         listener: variable_3
#         +-[entry #68]
#           speaker: variable_1
#           listener: variable_2
#           +-[reply #29]
#             listener: variable_3
#             +-*** see entry #69 ***
#             +-*** see entry #70 ***
#             +-*** see entry #71 ***
#             +-*** see entry #72 ***
#             +-*** see entry #73 ***

from bs4 import BeautifulSoup
import json,re,csv


def cleanText(t):
	t = t.replace("’","'").replace("“",'"').replace("”",'"').replace("…", " ... ")
	return(t)


def parseFile(fileName,parameters={},asJSON=False):

# 	def loadConditionals():
# 		o = open("raw/conditionals.txt")
# 		txt = o.read()
# 		o.close()
# 		bits = txt.split("\n[")
# 		
# 		conditionals = {}
# 		for bit in bits:
# 			bitName,cond = bit.split("]\n",1)
# 			conditions[bitName.strip()] = cond.strip()
			
	def loadPlotDatabase(folder):
		o = open(folder + "/plotDatabase.txt")
		txt = o.read()
		o.close()
		txt = txt.replace("/","/")
	
		condBits = txt.split("<conditional ")[1:-1]
		condDatabase = {}
		for condBit in condBits:
			condID = condBit[condBit.index("=")+2:condBit.index(">")-1].strip()
			condDesc = condBit[condBit.index("<description>")+13:condBit.index("</description")]
			condDatabase[condID] = condDesc
		
		transBits = txt.split("<state_transition ")[1:-1]
		transDatabase = {}
		for transBit in transBits:
			transID = transBit[transBit.index("=")+2:transBit.index(">")-1].strip()
			transDesc = transBit[transBit.index("<description>")+13:transBit.index("</description")]
			transDatabase[transID] = transDesc
		
		boolBits = txt.split("<value ")[1:-1]
		boolDatabase = {}
		for boolBit in boolBits:
			boolID = boolBit[boolBit.index("=")+2:boolBit.index(">")-1].strip()
			boolDesc = boolBit[boolBit.index("<description>")+13:boolBit.index("</description")]
			boolDatabase[boolID] = boolDesc

		# Character lists
		charBits = txt.split("<character ")[1:]
		charIDToFriendlyName = {}
		for charBit in charBits:
			friendlyName = charBit[charBit.index("=")+2:charBit.index(">")-1].strip()
			friendlyName = friendlyName.replace("&quot;",'"')
			tags = re.findall('<actor_tag>(.+?)</actor_tag>', charBit)
			for tag in tags:
				charIDToFriendlyName[tag] = friendlyName
				
		#allCharNames = list(set([x for x in charIDToFriendlyName.values()]))
		#for ax in allCharNames:
		#	print(ax)
#		o = open(folder + "/../charIDs.txt",'w')
#		o.write("\n".join(['\t"' + x + '":"' + charIDToFriendlyName[x] + '"' for x in charIDToFriendlyName]))
#		o.close()

		# extra parts:
		# (Abandoned for now because the format is weird)
# 		b2 = open(folder + "/bools.txt").read()
# 		for x in ["name:","id:","categories:","Note:","ints:","bools:"]:
# 			b2 = b2.replace(x,'"'+x[:-1]+'":')
# 		b2 = b2.replace(",\n}","\n}")
# 		bools2 = json.loads(b2)
# 		print(bools2)
# 		print(naskj)
		

		return((charIDToFriendlyName,condDatabase,transDatabase,boolDatabase))

	def loadConversationOwnerData(folder):
		convOwners = {}
		with open(folder+"/../ME3_DialogueOwners.csv") as csvfile:
			creader = csv.reader(csvfile)
			for row in creader:
				conv = row[0]
				owner = row[1]
				convFile = row[2]
				
				convOwners[conv] = owner
		return(convOwners)

	def embedChoices(ttree,level=0):
		# from https://stackoverflow.com/questions/17858404/creating-a-tree-deeply-nested-dict-from-an-indented-text-file-in-python
		# ttree is a list of tupes (value, level)
		result = []
		for i in range(0,len(ttree)):
			cn = ttree[i] # current node
			try:
				nn  = ttree[i+1] # next node
			except:
				nn = (None,-10)
							
			# Edge cases
			if cn[1]>level:
				# The trailing level can sometimes be a bit weird
				if i==len(ttree)-1 and result[-1]!=cn[0]:
					result.append(cn[0])
				continue
			if cn[1]<level:
				return(result)
			# Recursion
			if nn[1]==level:
				result.append(cn[0])
			elif nn[1]>level:
				# Prase the rest of this branch
				rr = embedChoices(ttree[i+1:], level=nn[1])
				# add choice to current set of dialogue
				if len(rr)>1:
					cn[0].append({"CHOICE":rr})
					# add to result
					result.append(cn[0])
				elif len(rr)==1:
					# (not really a choice if there's just one subnode)
					result.append(cn[0])
					result.append(rr[0])
			else:
				result.append(cn[0])
				return(result)
		return(result)
		
	def parseCondition(partItems, speaker):
		thisCond = None
		if "conditional" in partItems["condition"]:
			condID = partItems["condition"]
			condID = condID[condID.index("_")+1:condID.index("(")]
			thisCond = partItems["condition"]
			if condID in condDatabase:
				thisCond = condDatabase[condID]
				if thisCond == "Speaker is in party" and not speaker.startswith("CHECK"):
					spk = speaker
					if spk in charIDToFriendlyName:
						spk = charIDToFriendlyName[spk]
					thisCond = spk + " is in party"
			thisCond = {"STATUS": thisCond}
		elif "plot.bools" in partItems["condition"]:
			# TODO: How to link plot bools?
			thisCond = {"STATUS": partItems["condition"]}
		return(thisCond)
		
		
	def parsePart(part, chunkName, var1Guess=None):

		if part.replace("|","").strip().startswith("***"):
			# TODO: record transition /  dialogue end
			if "*** see " in part:
				localRef = part[part.index("*** see ")+8:part.index(" ***")].replace(" ","")
				return([{"GOTO": chunkName+"@"+localRef}])
			else:
				return(None)
	
		lines = part.split("\n")
		partID = lines[0][lines[0].index("[")+1:lines[0].index("]")].replace(" ","")
		partID = chunkName + "@" + partID
		#partIsChoice = partID == "choice"
		
		lines = [x.replace("|","").strip() for x in lines]
		lines = [x for x in lines if len(x)>0][1:]
		lx = [x.split(": ",1) for x in lines]

		majorDecision = False
		if "major decision" in  lx:
			majorDecision = True
		lx = [x for x in lx if len(x)==2]
		lx = [(y[0].strip(),y[1].strip()) for y in lx]
		partItems = dict(lx)
		
		speaker = "Shepard"
		if "speaker" in partItems:
			speaker = partItems["speaker"]
			if speaker.startswith("variable_"):
				if not (var1Guess is None):
					speaker = var1Guess
				else:
					speaker = "CHECK."+chunkName+"."+speaker[-1]
			else:
				if speaker in charIDToFriendlyName:
					speaker = charIDToFriendlyName[speaker]
		
		
		ret = [{}]
		if "text" in partItems:
			if "category" in partItems:
				# part of a choice
				ret[-1][speaker] = "(" + partItems["text"] + ")"
				ret[-1]["_C"] = partItems["category"]
				if majorDecision:
					ret[-1]["_MajDec"] = "T"
			else:
				ret[-1][speaker] = partItems["text"]

			if not partID.endswith("choice"):
				ret[-1]["_ID"] = partID
			
			if "condition" in partItems:
				cond = parseCondition(partItems,speaker)
				if not cond is None:
					ret = [cond]+ret	
			return(ret)
		elif "condition" in partItems:
			cond = parseCondition(partItems,speaker)
			if not cond is None:
				return([cond])	
			else:
				return(None)
		
		return(None)
	
	def parseChunk(chunk,chunkName,var1Guess=None):
		subchunks = [x for x in chunk.split("\n\n") if len(x)>2]
		outx = [([{"LOCATION": chunkName}],0)]
		for subchunk in subchunks:
			prevLevel = 0
			
			parts = re.split("\n([ |]*\+-)",subchunk)
			# ZIP delimiter and part
			parts = [x for x in zip(parts[1::2],parts[2::2])]
			
			# Add chunk name as a header at level zero
			bit = []		
			for plus,part in parts:
				parsedPart = parsePart(part, chunkName, var1Guess)
				plusLevel = plus.index("+")
			
				isBareConditional = (part.count("condition: ")>0) and (part.count("text: ")==0)
	#			if isBareConditional:
	#				prevLevel = plusLevel
	#				bit.append({"DEC":0})
			
				if not parsedPart is None:
					if plusLevel > prevLevel:
						isChoice = part.count("[choice]")>0
						notJustOneSpaceAfterLastLine = (not (re.search("\n.*?\\| [A-Za-z]",part) is None))

						if notJustOneSpaceAfterLastLine or isChoice: #or isBareConditional:
							# dump current bit at prevLevel
							if len(bit)>0:
								outx.append((bit,prevLevel))
							# empty current bit and add part
							bit = parsedPart
							# Recalculate level
							prevLevel = plusLevel
						else:
							# same bit
							# Add to list, at prevLevel
							bit += parsedPart
					elif plusLevel < prevLevel:
						# Level has decreased, dump, recalc, add
						if len(bit)>0:
							outx.append((bit,prevLevel))
						bit = parsedPart
						prevLevel = plusLevel
					else:
						# Same level as previous
						#  (this happens for choices)
						# Dump current bit at prevLevel
						if len(bit)>0:
							outx.append((bit,prevLevel))
						# Add part to bit at prevLevel (equal to current level)
						bit = parsedPart
				else:
					if plusLevel < prevLevel:
						if len(bit)>0:
							outx.append((bit,prevLevel))
						outx.append(([{"STATUS":"See decision/condition above"}],plusLevel))

			# dump any hangover
			if len(bit)>0:
				outx.append((bit,prevLevel))
		return(outx)
	
	folder = fileName[:fileName.rindex("/")]
	charIDToFriendlyName,condDatabase,transDatabase,boolDatabase = loadPlotDatabase(folder)
	
	convOwners = loadConversationOwnerData(folder)
	
	o = open(fileName)
	d = o.read()
	o.close()
	
	locClues = {}
	
	needsCoding = {}
	
	charClues = {
		"adams": "Engineer Adams",
		"aethyta": "Matriarch Aethyta",
		"allers": "Diana Allers",
		"anderson": "David Anderson",
		"anderson1": "David Anderson",
		"anderson2": "David Anderson",
		"anderson3": "David Anderson",
		"andersonak01": "David Anderson",
		"andersonak02": "David Anderson",
		"aria2":"Aria T'Loak",
		"aria3":"Aria T'Loak",
		"ash": "Ashley Williams",
		"avina": "Avina",
		"barla": "Barla Von",
		"catalyst": "Catalyst",
		"chakwas": "Dr. Chakwas",
		"corinthus": "Corinthus",
		"donnelly": "Kenneth Donnelly",
		"ken": "Kenneth Donnelly",
		"edi": "EDI",
		"falere": "Falere",
		"gabby": "Gabriella Daniels",
		"garr":"Garrus Vakarian",
		"garrus":"Garrus Vakarian",
		"lightculm": "Garrus",
		"hackett": "Admiral Hackett",
		"hackett1": "Admiral Hackett",
		"hackett2": "Admiral Hackett",
		"hackett3": "Admiral Hackett", 
		"illusive": "Illusive Man",
		"jack": "Jack",
		"jacob": "Jacob",
		"james":"James Vega",
		"joker": "Joker",
		"kahlee": "Kahlee Sanders",
		"kaid": "Kaidan Alenko",
		"kaidan":"Kaidan Alenko",
		"kaileng": "Kai Leng",
		"kasumi": "Kasumi Goto",
		"kelly": "Kelly Chambers",
		"khalisah1":"Khalisah al-Jilani",
		"khalisah2":"Khalisah al-Jilani",
		"kirrahe": "Captain Kirrahe",
		"lia": "Liara",
		"liara": "Liara",
		"michel": "Dr. Michel",
		"miranda": "Miranda Lawson",
		"mordin": "Mordin Solus",
		"pilot": "Esteban Cortez",
		"raan": "Admiral Shala'Raan vas Tonbay",
		"rodriguez":"Rodriguez",
		"samara": "Samara",
		"tali": "Tali'Zorah",
		"talitalk": "Tali'Zorah",
		"udina": "Udina aka. The Traitor",
		"undina": "Udina aka. The Traitor",
		"victus": "Tarquin Victus",
		"wreav": "Urdnot Wreav",
		"wrex": "Urdnot Wrex",
		"zaeed": "Zaeed Massani"
		}
	
	out = []
	chunks = d.split("\n[")
	for chunk in chunks:
		out1 = []
		chunkName = chunk[:chunk.index("]")]
		
		convName = chunkName.split(".")[2].strip()
		var1Guess = None
		if convName in convOwners:
			# We know the owner
			var1Guess = convOwners[convName]
			if var1Guess == "Not found":
				var1Guess = None
		else:
			print("------->"+convName)
		
		if var1Guess is None:
			locClue,charClue = chunkName.split(".")[1].split("_")[:2]
			chunkName = ".".join(chunkName.split(".")[:2])
			var1Guess= None
			if charClue in charClues:
				var1Guess = charClues[charClue]
		
		parts = parseChunk(chunk, chunkName, var1Guess)

		chunkOut = embedChoices(parts)
		for cx in chunkOut:
			out += cx
		out.append({"ACTION":"---"})
	

			
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)











