from bs4 import BeautifulSoup
import json, re

# TODO
# Check whether filtering datapoint logs is working.


def parseFile(fileName,parameters={},asJSON=False):
	# The data files are composed of one main file and several
	#  audio and hologram "datapoints"

	def cleanLine(txt):
		txt = txt.replace("\n"," ")
		txt = txt.strip()
		rep = [('’',"'"),("‘","'"),("…","... "),("—","-"),("“",'"'),("”",'"'),("é","é")]
		for r1,r2 in rep:
			txt = txt.replace(r1,r2)
	
		# Remove lines that start with parentheses and have nothing else
		txt = txt.replace("...","... ")
		txt = re.sub(" +"," ",txt)
		txt = txt.replace("[","(").replace("]",")")
		return(txt)
	
	def cleanName(txt):
		txt = txt.replace("’","'")
		return(txt)
		
	def parseP(line):  #(takes text)
		if line.strip().startswith("["):
			if line.strip().endswith("]"):
				lx = line.strip()[1:-1].strip()
				if len(lx)>0:
					return([{"ACTION": cleanLine(lx)}])
			elif line.lower().count("datapoint")>0:
				datapoint = line[line.index("[")+1:line.index("]")]
				endOfDatapoint =line.index("]")
				colonPos = line.index(":",endOfDatapoint)
				charName = line[endOfDatapoint+1:colonPos].strip()
				dialogue = "(" + datapoint + ") " + line[colonPos+1:].strip()
				return([{cleanName(charName): cleanLine(dialogue)}])
			elif line.count("scans an interview")>0:
				outx = []
				for bit in [x for x in line.split("\n") if len(x.strip())>0]:
					outx += parseP(bit)
				return(outx)
			else:
				# textDatapoint
				return([{"ACTION":cleanLine(line.strip())}])
		elif line.count(":"):
			charName = line[:line.index(":")].strip()
			dialogue = line[line.index(":")+1:].strip()
			dialogue = cleanLine(dialogue)
			if dialogue == "On the Old Trail? Is she crazy?":
				return( [{"Female Contestant": "On the Old Trail?"},
						{"Male Contestant": "Is she crazy?"}])
			elif len(dialogue)>0:
				return([{cleanName(charName):cleanLine(dialogue)}])		
		else:
			if len(line.strip())>0:
				return([{"ACTION": cleanLine(line.strip())}])

	def getChildParts(child):
		parts = []
		currentPart = ""
		for x in child:
			if x.name == "br":
				parts.append(currentPart)
				currentPart = ""
			else:
				currentPart += x.get_text()
		if len(currentPart)>0:
			parts.append(currentPart)
		return(parts)


	o = open(fileName)
	d = o.read()
	o.close()
	
	isDatapoint = False
	datapointName = ""
	if d.startswith("DATAPOINT"):
		isDatapoint = True
		datapointName = d[:d.index("\n")]
		datapointName = datapointName.replace("\t",": ")
		d = d[d.index("\n"):]
		d = d.replace("Operation:","Operation")
		d = d.replace("Project:","Project")
		d = d.replace("Dawn:","Dawn")
	else:
		# Main script file fixes	
		d = d[d.index(parameters["scriptStartCue"]):d.index(parameters["scriptEndCue"])]
		d = d.replace("<b>FROM:</b>","<b>[FROM:</b>")
		d = d.replace("Rest in Peace","Rest in Peace]")
		d = d.replace("Looks strong, thought", "Looked strong, I thought")
		d = d.replace("Bu All-Mother, you survived","But All-Mother, you survived")
		d = d.replace('datapont',"datapoint")
		d = d.replace("into Meridian without submitting to.","into Meridian without submitting to search.")
		d = d.replace("&#160;","")
	
	d = d.replace("Mad King Jiran's summer palate","Mad King Jiran's summer palace")
	d = d.replace("Kill the all!","Kill them all!")
		
	script = BeautifulSoup(d, 'html.parser')
	
	script = script.find_all(["p","h2"],recursive=True)
	
	out = []
	
	if isDatapoint:
		# File is Extract from datapoint
		out.append({"ACTION":datapointName})
		lastChar = "ACTION"
		for child in script:
			if child.name=="p":
				lines = getChildParts(child)
				for line in lines:
					if line.strip().startswith("("):
						out.append({"ACTION":cleanLine(line.replace("(","").replace(")","").strip())})
					else:
						if line.count(":") and line.index(":")<35:
							lastChar = cleanName(line[:line.index(":")].strip()).title().replace("'S","'s")
							if lastChar in ["From","To","Subject","Status"]:
								lastChar = "ACTION"
							else:
								line = line[line.index(":")+1:]
						out.append({lastChar: cleanLine(line)})

		out.append({"ACTION":"---"})
	else:
		# Main script
		for child in script:
			if child.name=="h2":
				lx = child.getText().replace("[","").replace("]","").strip().replace("’","'")
				if len(lx)>0:
					out.append({"LOCATION": lx})
			if child.name=="p":
				line = child.get_text()
				px = parseP(line)
				if px is not None:
					out += px
		out.append({"ACTION":"END OF MAIN FILE. Extra datapoint extracts are included below."})
		out.append({"ACTION":"---"})
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)
	
def postProcessing(out):
	# Remove datapoints that are already in the main text
	# Do this by getting a "clip" of each line in the main text
	#  then checking whether it matches the first dialogue line of each datapoint
	
	def getClip(line):
		k = list(line.keys())[0]
		txt = line[k]
		txt = re.sub("\(.*?\)"," ",txt).strip()
		clip = k + ":" + txt[:30]
		return(clip.lower())
	
	mainFileClips = []

	startedDatapoints = False
	testNext = False
	prevDatapoint = None
	skip = False
	
	out2 = []
	for line in out:
		clip = getClip(line)
		# Recognise end of main file part
		if clip.startswith("action:end of main file"):
			startedDatapoints = True

		# decide whether to include the lines:
		if not startedDatapoints:
			mainFileClips.append(clip)
			out2.append(line)
		else:
			if clip.startswith("action:datapoint:"):
				testNext = True
				prevDatapoint = line
			elif testNext:
				testNext = False
				skip = clip in mainFileClips
				if not skip:
					out2.append(prevDatapoint)
					out2.append(line)
				#else:
				#	out2.append({"ACTION": "SKIP "+list(prevDatapoint.values())[0]})
			elif not skip:
				out2.append(line)
				
	JDialouge = [
		{"LOCATION": "SUNSTONE ROCK"},
		{"Sunstone Guard": "Warden Janeva. This is the one who defeated the Behemoths."},
		{"Janeva": "Outlander. I'm impressed. I don't impress easily. Tell me, how do you fare with hunting living prey?"},
		{"Aloy": "Haven't had any complaints. Why?"},
		{"Janeva": "Three dangerous prisoners have escaped. I need my men here, getting the others back in line. None of this would have happened if we dealt with criminals the old way ... But, I've clashed that gong before, and here I am, am here you are. "},
		{"Aloy": "What's the old way?"},
		{"Janeva": "TO be buried up to the neck and left for the Sun's judgement."},
		{"Aloy": "Seems to me like the jugement's already been made."},
		{"Janeva": "Not one of them committed another crime. "},
		{"Aloy": "Who are these dangerous prisoners?"},
		{"Janeva": "Three from the isolation cages. Don't feel sorry for them, they've lived well off the Sun-King's conscience. First is Rasgrund. Oseram trap-maker, hates the Carja, carzy as a loon in heat. Caught in one too many blasts -- or one too few. Then there's Ullia. A Tenakth warrior, if that means anything to you?"},
		{"Aloy": "Not really. Another tribe?"},
		{"Janeva": "Reavers, from the south. Bloodthirsty -- some say they're cannibals, but she slurped gruel well enough. And the last is Gavan. A traitor who smuggled weapons to the exiles."},
		{"Aloy": "Compared to the other two, this one doesn't seem so bad."},
		{"Janeva": "He helped drag out a civil war, all for the shards it got him. A machine has more warmth."},
		{"Aloy": "Do you know a ... hunter ... named Nil? He told me about this place."},
		{"Janeva": "Nil. That's what he calls humself now? Is he ... well?"},
		{"Aloy": "I maybe wouldn't say well."},
		{"Janeva": "He was born under a long and dark shadow. But he wasn't a knife without a thought behind it, like the butchers of the Sun-Ring. He had honor. Old-fashioned. His time here ... boiled it to the surface."},
		{"Aloy": "So the Carja keep their criminals in this place?"},
		{"Janeva": "Since the Liberation. We've had them all, from theives to the Mad King Jiran's former kestrels. The Sun-King believes in the power of change. And sure enought, some did change. Shed their skin, like lizards. I thought all criminals were the same, once. That's why the Sun-King gave me command of Sunstone Rock. As an education."},
		{"Aloy": "Sounds like an honor -- I mean, I haven't seen any other women in Carja armor -"},
		{"Janeva": "No. I'm not one of your sisters. No woman can wear Carja armor. When I was young, I chose to become a soldier. One good enough to join Avad's honor guard. There was talk about what I was. So I'd say, \"Test me, and I'll break your arm\". After enough arms had been broken, there was less talk."},
		{"Aloy": "I'm curious ... but, I'd rather we didn't have to start fighting."},
		{"Janeva": "Agreed."},
		{"Aloy": "So you want these prisoners brought back."},
		{"Janeva": "No. I want them put in the earth. I doubt they'll give you any choice. They had their chance with the Sun-King's generosity. So now they face mine. A bounty on all their heads. Ullia of the Tenakth, Rasgrund of the Oseram, and the traitor Gavan."},
		{"Aloy": "If I did this for you, I'd need a lead on them."},
		{"Janeva": "Well, when Ullia first swept through the Sundom, it was with the jungle bandits. I say she'll go back. Rasgrund, we pulled out of a crack in Dusk Mesa, where he'd been tinkering with his bombs. And Gavan will be trying to pay his way across the lake, I'd burn my palm on it. Look in Brightmarket."},
		{"ACTION": "After Aloy completes the bounty."},
		{"Janeva": "Your aid to the Carja Sundom in these times of strife is appreciated. That's the official response. I'd say: I can tell you've done the work by the look on your face."},
		{"Aloy": "Two of them got themselves killed. The other welcomed a fight to the end. J: They would have found death with or without you. Taken others with them."},
		{"Aloy": "That's what I told myself."},
		{"Janeva": "Smart girl. Doubt we'll meet again, so -- go in light."}
	]
	
	out3= []
	for line in out2:
		if line == 	{"LOCATION": "DEEP SECRETS OF THE EARTH"}:
			out3 += JDialouge
		out3.append(line)

	return(out3)
			
			
			