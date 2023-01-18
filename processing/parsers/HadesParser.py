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
	open("../data/Hades/Hades/raw/tmp.json",'w').write(d)
	
	#dx = d[d.index("UnitSetData.NPCs"):]
	#dx = d[d.index("{"):d.index("\n}")+2]
	#
	#dx = dx.split("\n")
	#dx2 = []
	#for line in dx:
	#	if line.strip().startswith("--"):
	#		line = '    "COMMENTNUM": "'+line.replace('"','\\"').replace("\t","") + '",'
	#	dx2.append(line)
	#dx = "\n".join(dx2)
	#dx = re.sub("{\s*{","[{",dx)
	#dx = re.sub("}\s*}","}]",dx)
	#dx = dx.replace("=",":")
	#dx = hjson.loads(dx)
	#open("../data/Hades/Hades/raw/tmp.json",'w').write(json.dumps(dx))
	
	
	bits = re.split("\n\s*{",d)#d.split("{")
	
	out = []
	conv = []
	inConv = False
	for bit in bits:
		if bit.count('Cue = "')>0 and bit.count('Text = ')>0:
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
					out += conv
					conv = []
				out.append({"ACTION": "---"})
	
				
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)