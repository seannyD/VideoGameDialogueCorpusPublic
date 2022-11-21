# TODO
# {"Archadian Gentry/Good Brother": "Archadian Gentry/Waiting Woman (x2): I wo
# (if you haven't already spoken to him)
# "Horne (and all other Moogling attendants, after you've used the Moogling the first time, will say this same thing, unless one of them is involved in an active quest)",
# "Moogling Attendant (during this period in the game, there is a Moogling Attendant to explain the Moogling to you at every Moogling post)",
# (again, both say same thing)


from bs4 import BeautifulSoup, NavigableString, Tag
import json, re
import bs4
import cssutils

#ffxii_PhrasesThatLookLikeNamesButAreActions=[]

def parseFile(fileName,parameters={},asJSON=False):
	print(fileName)
	#global ffxii_PhrasesThatLookLikeNamesButAreActions
	#ffxii_PhrasesThatLookLikeNamesButAreActions = parameters["PhrasesThatLookLikeNamesButAreActions"]
	
	html = open(fileName, 'r').read()
	html = html.replace("Nutsy: Nutsy:","Nutsy: ")
#	html = html.replace('The only factor that actually changes based on where you talk to her is the price </span><span class="c9">[n]</span><span class="c1">',
#						'The only factor that actually changes based on where you talk to her is the price "n"')
	html = html.replace('</span><span class="c0">[#]</span><span class="c4 c6">&nbsp;', " N ")
	html = html.replace("[n]",'"n"')
	soup = BeautifulSoup(html, 'html5lib')
	#html.close()
	css = soup.find('head').find('style')
	css = cssutils.parseString(css.string)

	
	marginRules = {}
	italicClasses = []
	for rule in css.cssRules:
		
		if hasattr(rule, 'style'):
			if "margin-left" in rule.style.keys():
				ml =rule.style["margin-left"].replace('pt',"")
				if len(ml)>0:
					marginRules[rule.selectorText] = int(ml)
			elif "margin" in rule.style.keys():
				ml =rule.style["margin"].replace('pt',"")
				if len(ml)>0:
					marginRules[rule.selectorText] = int(ml)
			if "font-style" in rule.style.keys():
				if rule.style["font-style"] == "italic":
					italicClasses.append(rule.selectorText)
	marginRules = dict(marginRules)
	
	def getMaxMarginLeft(obj):
		x = [marginRules["."+cl] for cl in obj.get("class") if "."+cl in marginRules.keys()]
		if len(x)>0:
			return(max(x))
		else:
			return(0)

	def isItalic(obj):
		if any([("."+cl) in italicClasses for cl in obj.get("class")]):
			return(True)
		if obj.find("span"):
			spanClass = obj.find("span").get("class")
			if not spanClass is None:
				if any([("."+cl) in italicClasses for cl in spanClass]):
					return(True)
		return(False)
	
	#print(marginRules)
	
	posts = soup.find('body')
	
	def cleanDialogue(txt):
		txt = txt.replace("\n"," ")
		txt = txt.replace("¬"," ")
		txt = txt.replace("¬"," ")
		txt = txt.replace('“','"')
		txt = txt.replace('”','"')
		txt = txt.replace('’',"'")
		txt = txt.replace('‘',"'")
		txt = txt.replace(">","")
		txt = txt.replace("…"," ... ")
		txt = txt.replace("\\xa0", " ")
		txt = txt.replace("\xa0", " ")
		txt = re.sub(" +"," ",txt)
		if txt.startswith("-"):
			txt = txt[1:]
		txt = txt.strip()
		return(txt)
		
	def cleanName(txt):
		txt = txt.replace("¬","")
		txt = txt.replace('’',"'")
		txt = txt.replace('‘',"'")
		txt = txt.replace('“','"')
		txt = txt.replace('”','"')
		txt = txt.replace("\\xa0", " ")
		txt = txt.replace("\xa0", " ")
		txt = txt.strip()
		return(txt)
		
# 	def embedChoices(choices):
# 		indentation = []
# 		indentation.append(0)
# 		depth = 0
# 		data = []
# 		for choice,indent in choices:
# 			if indent > indentation[-1]:
# 				depth += 1
# 				indentation.append(indent)
# 				data.append([])
# 
# 			elif indent < indentation[-1]:
# 				while indent < indentation[-1]:
# 					depth -= 1
# 					indentation.pop()
# 					top = data.pop()
# 					data[-1].append(top)
# 
# 				if indent != indentation[-1]:
# 					raise RuntimeError("Bad formatting")
# 
# 			data[-1].append(content)
# 
# 		while len(data) > 1:
# 			top = data.pop()
# 			data[-1].append(top)
# 		return(data)

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
		
	def getCharNameForChoice(charName,dialogue,parameters):
		dialogue = cleanDialogue(dialogue)
		if any([dialogue.startswith(x) for x in parameters["PlayerChoiceWhichIsDialogue"]]):
			charName = "Vaan"
		else:
			charName = "ACTION"
		return(charName)
	
	def makeDialogue(charName,dialogue,parameters,setPrevCharName=False):
		global previousCharName
		extra = ""
		if charName.count("(x"):
			extra = re.findall('\(x.+?\)', charName)[0]
			charName = charName[:charName.index("(x")].strip()
		
		if charName.count("(sign)")>0 or charName.lower().endswith(" sign") or charName.lower().endswith(" signs"):
			dialogue = "(" + charName + ") -" + dialogue
			charName = "ACTION"
		cond = ""
		if charName.count("(if ")>0:
			ix = charName.index("(if ")
			cond = charName[ix+1:charName.index(")",ix)]
			charName = charName[:ix].strip()
		
		charCat = ""
		outsideParentheses = re.sub("\(.+?\)","",charName)
		if outsideParentheses.count("/")>0:
			#print(charName)
			charCat = charName[:charName.index("/")].strip()
			charName = charName[charName.index("/")+1:].strip()
			#print(charName)
		isChoice = False
		if charName == "VaanCHOICE":
			isChoice = True
			charName = getCharNameForChoice(charName,dialogue,parameters)
		
		ret = {cleanName(charName):cleanDialogue(dialogue)}
		if len(extra)>0:
			ret["_InteractionNum"] = extra
		if len(cond)>0:
			ret["_Condition"] = cond
		if len(charCat)>0:
			ret["_OriginalCharName"] = charCat
		if isChoice:
			ret["_IsChoice"] = "Y"
		if setPrevCharName:
			previousCharName = charName
		return(ret)
	
	def parseP(child,parameters,charName = ""):
		global previousCharName
		
		avoidNames = parameters["PhrasesWithColonsThatAreNotNames"]
		actionNames = parameters["PhrasesThatLookLikeNamesButAreActions"]
	
		texts = re.split("(\[.+?\])",child.get_text())
	
		#texts = [x.get_text().strip() for x in child.find_all("span")]
		texts = [x for x in texts if len(x.strip())>0]
		
		# TODO: options for purchases can be recognised by italics
		# Mt. Bur-Omisace   15
		# TODO: Add image links

		outx = []
		for txt in texts:
			noParentheses = re.sub("\(.+?\)","",txt)
			if txt.strip().startswith("[") or isItalic(child):
				actionText = txt.replace("[","").replace("]","")
				outx.append({"ACTION":cleanDialogue(actionText)})
			elif txt.count(":")>0 and cleanDialogue(txt[:txt.index(":")]) in actionNames:
				outx.append({"ACTION":cleanDialogue(txt)})
				previousCharName = "ACTION"
			elif noParentheses.count(":")>0 and noParentheses.index(":")<40 and not cleanDialogue(txt[:txt.index(":")]) in avoidNames and not txt.startswith("-"):
				charName = txt[:txt.index(":")].strip()
				previousCharName = charName
				dialogue = txt[txt.index(":")+1:].strip()
				if len(dialogue)>0:
					outx.append(makeDialogue(charName,dialogue,parameters,setPrevCharName=True))
			else:
				# overhanging dialogue
				if charName == "":
					outx.append(makeDialogue(previousCharName,txt,parameters))
				else:
					# TODO: Set previousCharName?
					outx.append(makeDialogue(charName,txt,parameters))
		return(outx)
	
	headerTypes = ["h2","h3","h4"]

	inChoice = False
	currentChoiceStyle = ""
	classOnStartingChoices = ""
	choices = []
	choice = []
	
	global previousCharName
	previousCharName = ""
	currentMarginDepth = 0
	prevChild = None
	out = []
	
	startedDialogue = False
	for child in posts.children:

	# ul is a new choice for a choices list
	#  following p will have a class that should be consistent within the choices
	#   (within the same level)
	#  Nested choices can be recognised by looking at the class of the li within the ul
		if child.name in headerTypes:
			startedDialogue = True
			
		if startedDialogue:
			# UL structures only encompass the player choice, not the answers,
			#  so we have to keep track of the class level which indicates
			#  the amount of indentation
			if child.name == "ul" or child.get_text().startswith(">"):
				inChoice = True
				if len(choices)==0 and len(choice)==0:
					# New set of choices, we'll keep track of previous class
					#print(prevChild.get_text())
					classOnStartingChoices = prevChild.get("class")
					classOnStartingChoices.sort()
					#print(classOnStartingChoices)
				if len(choice)>0:
						# add previous choice to choices
						choices.append((choice,currentMarginDepth))
						choice = []
				if child.name=="ul":
					lis = child.find_all('li')
					li = lis[-1]
					currentMarginDepth = getMaxMarginLeft(li)
					# Some choices have no further actions, so
					#  are bare li's within the ul
					if len(lis)>1:
						# For all but the last one
						for i in range(len(lis)-1):
							cx = parseP(lis[i],parameters,"VaanCHOICE")
							choices.append((cx,currentMarginDepth))
					# New choice, spoken by player
					# TODO: Line below used to be += ???
					choice = parseP(lis[-1],parameters, "VaanCHOICE")
					currentChoiceStyle = ""
				elif child.get_text().startswith(">"):
					currentMarginDepth = getMaxMarginLeft(child)
					choice = parseP(child, parameters, "VaanCHOICE")
					currentChoiceStyle = ""					
			elif child.name == "p" or child.name in headerTypes:
				prevChild = child
				if inChoice:
					if currentChoiceStyle == "":
						currentChoiceStyle = child.get("class")
						currentChoiceStyle.sort()
				
					# Are we in a different level of the choices,
					#   or have we finished a choice?
					#  Current tactic is to keep track of the class of the PREVIOUS p
					#   when we experience the first ul in a choices set.
					#  Then count on this being the same as the rejoining p (or h2 or h3)
					currClass = child.get("class")
					currClass.sort()
					if (currClass == classOnStartingChoices) or child.name in headerTypes or getMaxMarginLeft(child)==0:
						# Out of choices
						inChoice = False
						# Add any current choice to choices
						if len(choice)>0:
							#choice += parseP(child)
							choices.append((choice,currentMarginDepth))
						# Add choices to out
						if len(choices)>0:
							#print(choices)
							choices = embedChoices(choices,level=choices[0][1])
							out.append({"CHOICE":choices})
						choices = []
						choice = []
						currentMarginDepth = 0
						# Add current
						if child.name == "p":
							out += parseP(child,parameters)
						if child.name in headerTypes:
							locx = cleanDialogue(child.get_text())
							if child.name=="h4":
								pass
								#out.append({"LOCATION": locx})
							else:
								out.append({"ACTION": locx})
					else:
						if child.name == "p":
							choice += parseP(child,parameters)
				else:
					subChild = list(child.children)[0]
					if subChild.name == "span" and subChild.has_attr('class') and "c31" in subChild["class"]:
						locx = cleanDialogue(child.get_text())
						if len(locx)>0:
							out.append({"LOCATION": cleanDialogue(child.get_text())})
						previousCharName = "ACTION"
					elif child.name == "p":
						out += parseP(child,parameters)
					elif child.name in headerTypes:
						locx = cleanDialogue(child.get_text())
						if len(locx)>0:
							out.append({"LOCATION": cleanDialogue(child.get_text())})
						# First line after location is often a description
						previousCharName = "ACTION"

	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)


def postProcessing(out):

	def getChoiceStructure(currentConditions):
		cx = []
		for cc in currentConditions:
			charName = getCharName(cc)
			dial = cc[charName]
			cond = cc["_Condition"]
			cx.append([{"STATUS":cond},{charName:dial}])
		if len(currentConditions)==1:
			cx.append([])
		return({"CHOICE": cx})

	def getCharName(line):
		return([x for x in list(line.keys()) if not x.startswith("_")][0])

	out2 = []
	currentConditions = []
	currentCharName = ""
	for line in out:
		charName = getCharName(line)
		if "_Condition" in line:
			if len(currentConditions)==0:
				currentConditions.append(line)
				currentCharName = charName
			else:
				if charName == currentCharName:
					currentConditions.append(line)
				else:
					# Add choice structure
					choices = getChoiceStructure(currentConditions)
					out2.append(choices)
					# Then start new currentConditions
					currentConditions = [line]
					currentCharName = charName
		else:
			if len(currentConditions)>0:
				# Add choice structure
				choices = getChoiceStructure(currentConditions)
				out2.append(choices)
				currentConditions = []
				currentCharName = ""
			out2.append(line)
			

	return(out2)

# def postProcessing(out):
# 	global ffxii_PhrasesThatLookLikeNamesButAreActions
# 	actionDict = {}
# 	for x in ffxii_PhrasesThatLookLikeNamesButAreActions:
# 		x
# 	
# 	def changeAliasMulitlevel(out,ali):
# 		if len(ali)==0:
# 			return(out)
# 	
# 		def transform(multilevelDict,ali):
# 			newDict = changeAliasOneLevel(multilevelDict,ali)
# 
# 			if isinstance(newDict,dict):
# 				for k, val in newDict.items():
# 					if isinstance(val, dict):
# 						newDict[k] = transform(val,ali)
# 					if isinstance(val,list):
# 						newDict[k] = [transform(x,ali) for x in val]
# 			if isinstance(newDict,list):
# 				newDict = [transform(x,ali) for x in newDict]
# 			return newDict
# 		
# 		def splitCharacterDialogue(out,aliMulti):
# 			out2 = []
# 			for d in out:
# 				if "CHOICE" in d:
# 					d["CHOICE"] = [splitCharacterDialogue(x,aliMulti) for x in d["CHOICE"]]
# 					out2.append(d)
# 				else:
# 					try:
# 						charName = [x for x in d if not x.startswith("_")][0]
# 					except:
# 						print("ERROR:")
# 						print(d)
# 					if charName in aliMulti:
# 						replaceNames  = aliMulti[charName]
# 						for replaceName in replaceNames:
# 							out2.append(changeAliasOneLevel(deepcopy(d),{charName:replaceName}))
# 					else:
# 						out2.append(d)
# 			return(out2)
# 	
# 		# Apply the alias transformations
# 		out = transform(out,ali)
# 	
# 		# Split mutli-party lines of dialogue into individual lines
# 		aliMulti = {k: v for k, v in ali.items() if isinstance(v,list)}
# 		if len(aliMulti)>0:
# 			out = splitCharacterDialogue(out,aliMulti)
# 
# 	
# 	
# 	return(out)