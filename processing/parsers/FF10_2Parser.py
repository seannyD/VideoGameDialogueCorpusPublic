import json, re

def parseFile(fileName,parameters={},asJSON=False):

	def cleanLine(txt):
		txt = txt.replace("\\x91","'")
		txt = txt.replace("\\x92","'")
		txt = txt.replace("\\x97"," - ")
		txt = txt.replace("\\x85"," ... ")
		txt = txt.replace("...", " ... ")
		txt = txt.replace("\\x93",'"')
		txt = txt.replace("\\x94",'"')

		txt = re.sub(" +"," ",txt)
		txt = txt.strip()
		return(txt)
	
	def cleanName(charName):
		charName = charName.replace("\\x92","'")
		charName = charName.strip()
		return(charName)

	def parseLines(txt):
		lines = txt.split("\n\n")
		lines = [x.replace("\n"," ") for x in lines]
		lines = [re.sub(" +"," ",x) for x in lines]
		
		outx = []
		for line in lines:
			if line.count(":")>0 and line.index(":")<33:
				charName,dialogue = line.split(":",1)
				# Check for narration
				if dialogue.count("(narrating)")>0:
					before,narr = dialogue.split("(narrating)",1)
					after = ""
					if narr.count("(")>0:
						after = narr[narr.index("("):]
						narr = narr[:narr.index("(")]
					if len(cleanLine(before))>0:
						outx.append({cleanName(charName): cleanLine(before)})
					if len(cleanLine(narr))>0:
						# This is a line which is spoken, though not strictly dialogue,
						#  it is heard by the player
						outx.append({cleanName(charName): "(narrating) " + cleanLine(narr)})
					if len(cleanLine(after))>0:
						outx.append({cleanName(charName): cleanLine(after)})
				else:
					outx.append({cleanName(charName): cleanLine(dialogue)})
			else:
				dialogue = cleanLine(line)
				if len(dialogue)>0:
					outx.append({"ACTION": dialogue})
		return(outx)


	print(fileName)
	txt = open(fileName, 'r').read()
	
	txt = txt[txt.index("We begin this game"):]
	
	txt = txt.replace("THE END","CONTINUE WITH THE SCRIPT")
	
	# Split into optional sections first
	sections = txt.split("CONTINUE WITH THE SCRIPT")
	
	out = []
	for section in sections[:-3]:
		matchs = re.finditer("IF ", section)
		matchs_positions = [m.start() for m in matchs]
		# find new line just before break positions
		break_positions = [section[:m].rindex("\n") for m in matchs_positions]

		if len(break_positions)==0 or break_positions[0]!=0:
			break_positions = [0] + break_positions
		break_positions.append(len(section))
		bits = []
		for i in range(len(break_positions)-1):
			bit = section[break_positions[i]:break_positions[i+1]]
			bits.append(bit)
			
		out += parseLines(bits[0])
		
		opts = [parseLines(option) for option in bits[1:]]
		if len(opts)>0:
			out.append({"CHOICE":opts})
	
	endScene1 = parseLines(sections[-3])
	endScene2 = parseLines(sections[-2])
	
	extra = [{"CHOICE":[
			[], endScene1
		]},
		{"CHOICE":[
			[], endScene2
		]}]	
	out += extra

	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)