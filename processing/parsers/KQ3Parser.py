from bs4 import BeautifulSoup, NavigableString, Tag
import json
import re

def parseFile(fileName,parameters={},asJSON=False):

	characterCues = parameters["characterCues"]
	skipLines = parameters["skipLines"]
	splitString = '(".+?")'
	quoteRecogniser = '"'
	
	if "splitString" in parameters:
		splitString = parameters["splitString"]
	if "quoteRecogniser" in parameters:
		quoteRecogniser = parameters["quoteRecogniser"]

	def parseLine(line):
		bits = re.split(splitString, line)
		txt = " ".join(bits[::2])
		txt = re.sub('[\.,:;\-\"]'," ",txt)
		txt = txt.split(" ")
		quotes = bits[1:][::2]
		charName = ""
		
		for cue in characterCues:
			if cue in txt:
				charName = characterCues[cue]
				return([{charName:cleanDialogue(q)} for q in quotes if not cleanDialogue(q) in skipLines])
		return([{"Unknown":cleanDialogue(q)} for q in quotes if not cleanDialogue(q) in skipLines])
		
	def cleanDialogue(dx):
		dx = dx.replace('"',"")
		dx = dx.replace('`',"'")
		dx = dx.replace("\\","").strip()
		return(dx)
	
	o = open(fileName)
	d = o.read()
	o.close()
	
	if "startText" in parameters:
		d = d[d.index(parameters["startText"]):]
	if "endText" in parameters:
		d = d[:d.index(parameters["endText"])]
		
	d = d.replace("""{C}Her last words on earth were: "Dear friends, I am going<br />
To where there's no cooking, or washing, or sewing,<br />
{C}For everything there is exact to my wishes,<br />
{C}For where they don't eat there's no washing of dishes,<br />
{C}I'll be where loud anthems will always be ringing,<br />
But having no voice I'll be quit of the singing,<br />
{C}Don't mourn for me now, don't mourn for me never,<br />
{C}I am going to do nothing for ever and ever."<br />""",
	"""{C}Her last words on earth were - 'Dear friends, I am going / To where there's no cooking, or washing, or sewing,/ For everything there is exact to my wishes, / For where they don't eat there's no washing of dishes, I'll be where loud anthems will always be ringing, / But having no voice I'll be quit of the singing, / Don't mourn for me now, don't mourn for me never, / I am going to do nothing for ever and ever.'<br />""")
	d = d.replace(""""Fe, fi, fo, fum!<br />
I smell the blood of a..."<br />""", 
		""""Fe, fi, fo, fum!"<br />
"I smell the blood of a..."<br />""")
	d = d.replace("You did it, your majesty!!", " You did it, your majesty!!\"")
	d = d.replace('\"mouse counsel\"',"'mouse counsel'")
	d = d.replace('"I\'m sorry Edgar, "You\'re very sweet...but, I must immediately return home."', '"I\'m sorry Edgar, You\'re very sweet...but, I must immediately return home."')
	d = d.replace("YECCHHH!! You cough and choke from the briny water of the ocean.", "\\\"YECCHHH!!\\\" You cough and choke from the briny water of the ocean.")
	d = d.replace("Glub, glub, glub, glub ....... !!!!!!", "\\\"Glub, glub, glub, glub ....... !!!!!!\\\"")
	d = d.replace("SSSsssssss! SSssstay away or I will ssssssstrike!", "\\\"SSSsssssss! SSssstay away or I will ssssssstrike!\\\"")
	d = d.replace("Can I be of service? the monk asks. What name do you go by?", "\\\"Can I be of service?\\\" the monk asks. \\\"What name do you go by?\\\"")
	d = d.replace("Please be quiet while praying.", "\\\"Please be quiet while praying.\\\"")
	d = d.replace("The kindly monk explains that he has heard of you and your quest. Here is my cross. It will protect you from evil, he says.", "The kindly monk explains that he has heard of you and your quest. \\\"Here is my cross. It will protect you from evil\\\", he says.")
	d = d.replace("Come, join me at the altar, my friend, says the monk.", "\\\"Come, join me at the altar, my friend\\\", says the monk.")
	d = d.replace("My name is Valanice, what is your name?", "\\\"My name is Valanice, what is your name?\\\"")
	d = d.replace("Come closer, kind sir.", "\\\"Come closer, kind sir.\\\"",)
	d = d.replace("Oh, Graham, I am forever grateful to you!", "\\\"Oh, Graham, I am forever grateful to you!\\\"")
	d = d.replace('message 128 "Hello."','message 128 "\\\"Hello.\\\""')
	d = d.replace("Yes, of course I will!", "\\\"Yes, of course I will!\\\"")
	d = d.replace("I love you, too!", "\\\"I love you, too!\\\"")
	d = d.replace("Thank you, Mister, she exclaims. Now I can take the goodies to my sick grandma.", "\\\"Thank you, Mister\\\", she exclaims. \\\"Now I can take the goodies to my sick grandma.\\\"")
	d = d.replace("In return for saving my life, I wish to offer you a ride across this ocean.", "\\\"In return for saving my life, I wish to offer you a ride across this ocean.\\\"")
	d = d.replace('If ya says so, sir','\\"If ya says so, sir')
	
	d = d.replace('\\"mouse counsel\\"',"'mouse counsel'")

		
	html = BeautifulSoup(d, 'html.parser')
	
	# divide into logic files
	logicFiles = []
	current = []
	for bit in list(html.children):
		if bit.name in ["p","ol", "dl"]:
			current.append(bit)
		elif bit.name in ["h2","h3"]:
			if len(current)>0:
				logicFiles.append(current)
				current = []
	
	finalMessages = []
	# Extract all message lines
	for logicFile in logicFiles:
		logicFileText = {}
		for bit in logicFile:
			for line in bit.children:
				if isinstance(line,Tag):
					line = line.get_text()
				line = line.strip()
				if isinstance(line,NavigableString) or isinstance(line,str) and len(line)>0:
					parts = line.split(' ',2)
					msgNum = parts[1]
					text = parts[2]
					logicFileText[msgNum] = text
		# glue parts together while keeping track of messages accessed
		#completeMessages = {}
		accessedMessages = []
		
		
		# TODO: iterate until no more messages are added?
		keepReplacing = True
		while keepReplacing:
			keepReplacing = False
			for msgNum in logicFileText:
				text = logicFileText[msgNum]
				if text.count("%")>0:
					parts = re.split("(%m[1-9][0-9]*)",text)
					completeMessage= ""
					for p in parts:
						if p.startswith("%m"):
							keepReplacing = True
							linkNum = p[2:].strip()
							accessedMessages.append(linkNum)
							completeMessage += logicFileText[linkNum]
						else:
							completeMessage += p
				else:
					completeMessage = text
				logicFileText[msgNum] = completeMessage
		fMessages = []
		for msgNum in logicFileText:
			if not msgNum in accessedMessages:
				fMessages.append(logicFileText[msgNum])
		finalMessages.append(fMessages)
			
	out = []
	
	characterName = ""
	for messages in finalMessages:
		characterName = ""
		for line in messages:
			if line.count(quoteRecogniser)>0:
				dialogue = parseLine(line)
				if len(dialogue)>0:
					currChar = [x for x in dialogue[0].keys()][0]
					if currChar!="Unknown":
						characterName = currChar
					else:
						if characterName!="":
							newDialogue = []
							for dx in dialogue:
								newDialogue.append({characterName: [x for x in dx.values()][0]})
							dialogue = newDialogue
				
					for dx in dialogue:
						dx["_OriginalLine"] = line
					out += dialogue
			else:
				# non-dialogue line
				line = cleanDialogue(line)
				line = line.replace("{C}","")
				line = re.sub("^[0-9]+","",line).strip()
				if len(line)>0:
					dial = {"SYSTEM": line}
					out.append(dial)						
	
	
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)
