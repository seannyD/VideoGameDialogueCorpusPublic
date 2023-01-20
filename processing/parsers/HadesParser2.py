import json, re,hjson

# TODO
# Extract comment/Cue pairs
#  Remove commented cue lines ("-- {Cue ")
#
# Put boundaries between alternative lines?
#   Or try to put them in CHOICE structures?
#
#  Error: "DisappearFadeLOCATION"
#  Error: "/VO/ZagreusField_4003"
#
# Maybe we need to parse by indent level?


# Split by "[A-Za-z0-9_]+ =\n\t+{"
#  Then we can extract the line ID to build up structure.
#  Then split by "{ Cue ="

# Some end cues just have commented transcript
# 				-- It's all right. Father can't make you sing if you don't want to.
#				EndCue = "/VO/ZagreusHome_1035",



def parseFile(fileName,parameters={},asJSON=False):

	def cleanLine(txt):
		if txt.count("\n")>0:
			txt = txt[:txt.index("\n")]
		# TODO: Handle emphasis markup
		txt = txt.replace("{#DialogueItalicFormat}","")
		txt = txt.replace("{#PreviousFormat}","")
		if txt.count("},")>0:
			txt = txt[:txt.index("},")]
		txt = txt.replace('"',"").strip()
		return(txt)

	def bitParser(bit):
		#print(bit)
		#print('-----')
		txt = bit[bit.index("Text")+4:].strip().replace("=","")		
		
		bit = bit[bit.index("Cue ="):]
		charName = "Unknown"
		if bit.count("/VO/")>0:
			vo = bit.index("/VO/")+4
			vx = bit[vo:bit.index(",",vo)].replace('"','').strip()
			#print("VX:"+vx)
			vx = vx[:vx.index("_")]
			#print("CN:"+charName)
			vx = re.findall('[A-Z][^A-Z]*',vx)
			charName = vx[0]
		elif bit.count("Speaker =")>0:
			sx = bit.index('Speaker = "')+11
			charName = bit[sx:bit.index('"',sx+1)]
			charName = charName.split("_")[1]
		elif bit.count("Bouldy")>0:
			charName = "Bouldy"
			
		#print("CN2:",charName)
		line = {charName:cleanLine(txt)}
		return(line)

	o = open(fileName)
	d = o.read()
	o.close()
	
	# Swap order of comment and cue lines
	d = re.sub("\n(\s*)(--.+?)\n(\s*{ Cue.+?)\n", "\n\\3\n\\1Text = \"\\2\"\n",d)
	# Apply again to catch lists
	d = re.sub("\n(\s*)(--.+?)\n(\s*{ Cue.+?)\n", "\n\\3\n\\1Text = \"\\2\"\n",d)
	d = d.replace("Text = \"\n","Text = \"")
	# These seem to be entities that violate the spit regex
	#  So replace first:	
	d = re.sub("EndVoiceLines =\n\t+{","EndVoiceLines = {",d)
	d = re.sub("VoiceLines =\n\t+{","VoiceLines = {",d)
	d = re.sub("Cooldowns =\n\t+{","Cooldowns = {",d)
	d = re.sub("DistanceTrigger =\n\t+{","DistanceTrigger = {",d)
	d = re.sub("ActivateRequirements =\n\t+{","ActivateRequirements = {",d)
	d = re.sub("Binks =\n\t+{","Binks = {",d)
	d = re.sub("InteractTextLineSets =\n\t+{","InteractTextLineSets = {",d)
	
	open("../data/Hades/Hades/raw/tmp.json",'w').write(d)

	# split into chunks
	chunks = re.split("([A-Za-z0-9_]+) =\n\t+{",d)
	chunks = list(zip(chunks[1::2],chunks[2::2]))
	out = []
	for chunkID, chunkContents in chunks:
		
		# Replace "\tEndCue =" with "\t{ Cue ="
		#  So that end cues are processed
		chunkContents = chunkContents.replace("\tEndCue =","\t{ Cue =")
		requiredLines = []
		if chunkContents.count("RequiredTextLines")>0:
			rlPos = chunkContents.index("RequiredTextLines")+17
			rl = chunkContents[rlPos:chunkContents.index("\n",rlPos)]
			rl = rl.replace("=","").replace("{","").replace("}","").replace('"',"")
			rl = rl.split(",")
			requiredLines = [x for x in rl if len(x)>2]
		
		bits = re.split("\n\s*{",chunkContents)
		conv = []
		inConv = False
		chunkOut = []
		for bit in bits:
			if bit.count('Cue = "')>0 and bit.count('Text = ')>0:
				print("HERE!")
				inConv = True
				line = bitParser(bit)
				conv.append(line)			
			else:
				if inConv:
					inConv = False
					if len(conv)>0:
						# move endcue to end
						if conv[0][list(conv[0].keys())[0]].count("--")>0:
							conv.append(conv.pop(0))
						chunkOut += conv
						conv = []
					chunkOut.append({"ACTION": "---"})
		# Final flush
		if len(conv)>0:
			# move endcue to end
			if conv[0][list(conv[0].keys())[0]].count("--")>0:
				conv.append(conv.pop(0))
			chunkOut += conv
		# Add to out
		if len(chunkOut)>0:
			if chunkContents.count("RandomRemaining = true") and len(chunkOut)>1:
				# alternative lines in CHOICE format
				out.append({"CHOICE":[[x] for x in chunkOut if not x=={"ACTION": "---"}]})
			else:
				out += chunkOut
		# Add divider if necessary
		if len(out)==0 or not out[-1]=={"ACTION": "---"}:
			out.append({"ACTION": "---"})
	
				
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)