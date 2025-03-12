import json, re, time, os


def cleanLine(txt):
	# don't include player input options
	txt = txt.strip()
	txt = txt.replace("..."," ... ")
	txt = txt.replace("…", " ... ")
	txt = txt.replace("“",'"')
	txt = txt.replace("”",'"')
	# e.g. ["chuckle","sigh","gasp","snrk","yip"]:
	#txt = re.sub("\*([A-Za-z]+) ?\*","(\\1)",txt)
	txt = txt.replace('*cough cough*',"(cough cough)")
	txt = txt.replace('*munch munch*',"(munch munch)")
	txt = txt.replace("{","")
	txt = txt.replace("}","")
	txt = re.sub("==+","",txt)
	txt = re.sub("--+","",txt)
	txt = txt.strip()
	txt = re.sub("^/","",txt)
	txt = re.sub("/$","",txt)
	txt = re.sub("\\\\","",txt)
	txt = txt.strip()
	txt = txt.replace("\n", " ")
	txt = re.sub(" +"," ",txt)
	if txt.startswith("+"):
		txt = txt.replace("+","*")
	return(txt)
	
	
def cleanName(name):
	name = name.replace("_"," ")
	name = name.title()
	name = name.replace("'S","'s")
	name = re.sub("\\(.+?\\)","",name).strip()
	return(name)


def parseFile(fileName,parameters={},asJSON=False):

	def parseLine(line):
		if line.strip()[0] in ["(","<",">"]:
			return({"ACTION": cleanLine(line)})
		elif line.strip()[0] in ["-","="]:
			return({"LOCATION": cleanLine(line)})
		elif line.strip()[0] == "{":
			return({"Makoto": cleanLine(line)})
		elif re.search("^ *[A-Z].+?: .+",line):
			speaker = cleanName(line[:line.index(":")].strip())
			dialogue = cleanLine(line[line.index(":")+1:])
			if speaker.count("Q.")>0:
				dialouge = speaker + " " + dialogue
				speaker = "ACTION"
			return({speaker:dialogue})
		return(None)



	o = open(fileName)
	d = o.read()
	o.close()
	
	d = d.replace("Episode 17: The Priestess' Revival","Episode 17- The Priestess' Revival")
	
	d = d[d.index("========\n*4/6/09*"):d.index("*Tanaka's Amazing Commodities*")]
	
	d = re.sub("\n +\n","\n\n",d)
	
	lines = re.split("\n\n+",d)
	
	# join choices
	chunks = []
	currentChunk = []
	inChoice = False
	for line in lines:
		if line.startswith("Main: {"):
			inChoice = True
			currentChunk = [line]
		else:
			if not inChoice:
				chunks.append(line)
			else:
				if not line.startswith("  "):
					inChoice = False
					chunks.append(currentChunk)
					currentChunk = []
					chunks.append(line)
				else:
					currentChunk.append(line)


	if len(currentChunk)>0:
		chunks.append(currentChunk)
	
	print("Parsed Chunks")
	
	out = []
	for line in chunks:
	
		if len("".join(line).strip())==0:
			pass
		elif line[0].strip().startswith("Main: {"):
			line[0] = line[0].replace("Main:","Makoto:") 
			choices = []
			currentChoice = []
			for lx in line:
				if lx.strip().startswith("{"):
					if len(currentChoice)>0:
						choices.append(currentChoice)
					currentChoice = []
					pLine= parseLine(lx)
					if not pLine is None:
						currentChoice = [pLine]
				else:
					pLine= parseLine(lx)
					if not pLine is None:
						currentChoice.append(pLine)
			if len(currentChoice)>0:
				choices.append(currentChoice)
			if len(choices)>0:
				out.append({"CHOICE": choices})
		else:
			pLine = parseLine("".join(line))
			if not pLine is None:
				out.append(pLine)

	return(out)
	