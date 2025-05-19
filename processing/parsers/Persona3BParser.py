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

	if fileName.count("SocialLinks")>0:
		out = parseSocialLinks(fileName)
		return(out)

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

def parseSocialLinks(fileName):
	# TODO: At the moment this is skipped
	#  The 

	return([])

	o = open(fileName)
	d = o.read()
	o.close()
	
	d = d[d.index("personatdh@gmail.com")+19:d.index("<>>=====[Credits][CR1]")]
	
	d = d.replace("i <--read downward!!\nluv\nu","Message: i <--read downward!! luv u")
	d = d.replace('\n Atlus decided to use both...]',' Atlus decided to use both...]')
	d = d.replace("\nb-but...","\n    b-but...")
	d = d.replace("\nMinato-sama...","\n    Minato-sama...")
	
	d = re.sub("\n  +"," ",d)
	
	#d = re.split("\n\n+",d)
	
	def parseSLBit(txt):
		lines = txt.split("\n")
		lines = [x.strip() for x in lines if len(x.strip())>0]
		out = []
		for line in lines:
			if len(line.strip())==0:
				pass
			elif line.startswith(">") or line.startswith("["):
				if not line.startswith("[Continue]=="):
					out.append({"ACTION": txt})
			elif line.startswith("====") or line.startswith("-"):
				pass
			elif line.startswith("["):
				line = line.replace("[","").replace("]","").strip()
				charName = "PC"
				if not line.startswith('"'):
					charName = "ACTION"
					line = "PC Chooses [" + line + "]"					
				else:
					if line.startswith('"'):
						line = line[1:]
					if line.endswith('"'):
						line = line[:-1]
				out.append({charName: line})
			else:
				print(line)
				speaker,dialogue = line.split(":",1)
				dialogue = cleanLine(dialogue)
				speaker = cleanName(speaker)
				out.append({speaker:dialogue})
		return(out)
	
	out = []
	#sections = d.split(">\n<>>===================")
	sections = d.split("\n<>>=====")
	sections = [x for x in sections if x.count('Summary:\n')==0]
	for section in sections[1:]:
		bits = section.split("<>>")
		bits = [x for x in bits if x.count("\n")>1]
		
		if len(bits)>0:
			start = bits[0]
			print(bits)
			if start.count("[Choices:]")>0:
				start = start[:start.index("[Choices:]")]
			out += parseSLBit(start)
			
			if len(bits)>1:
				cbits = bits[1:-1]
				choices = []
				# There are a very small number of choices with subchoices
				#  choices. Instead of a full recursive algorithm,
				#  just try to detect those cases and bodge.
				i = 0
				while i < len(cbits):
					choice = cbits[i]
					if choice.count("[Choices:]"):
						# This choice has sub-choices
						subChoices = [x for x in cbits if x.count("Choice 1-")>0]
						cx = parseSLBit(choice)
						cx.append({"CHOICE": [parseSLBit(x) for x in subChoices]})
						i += len(subChoices)-1
					else:
						choices.append(parseSLBit(choice))
					i += 1
				out.append({"CHOICE":choices})
				cont = bits[-1]
		
				cont = parseSLBit(cont)
				if len(cont)>0:
					out += cont
		
	return(out)