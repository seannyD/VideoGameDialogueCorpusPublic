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

	return(out2)
			
			
			