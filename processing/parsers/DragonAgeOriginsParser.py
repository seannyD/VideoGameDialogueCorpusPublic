import json, csv, re

# Creatures have a "gender" property: http://www.datoolset.net/wiki/Creature
# Characters have "male", "female" or "neutral"  http://www.datoolset.net/wiki/Character

# Creature tags: https://dragonage.fandom.com/wiki/Creature_tags_(Origins)

# Voice cast: https://dragonage.fandom.com/wiki/Voice_cast_(Origins)

# Another list: https://pdfcoffee.com/resrefnames-pdf-free.html


# The resource names are the conversation owner, I think
#  The speaker names are the actual thing we want.
# However, different characters sometimes have the same name?
#  e.g. arl110cr_child_f_1  and  arl110cr_child_m_1  -> "CHILD"
# And the main cast has multiple models: "Sten Main#sten_main", "Sten Faryn#sten_faryn", "Sten#party_camp"

# Note that arl110cr_child_f_1 - the "_f_" indicates a female model
#  "Amb Noblef#bdn120_amb_noblef_3",
#  "Amb Noblem#bdn100_amb_noblem_1",

def parseFile(fileName,parameters={"characterClassIdentifier":"DAI"},asJSON=False):
	
	def cleanLine(txt):
		txt = txt.replace("<emp>"," ")
		txt = txt.replace("</emp>"," ")
		txt = txt.replace("<desc>","(")
		txt = txt.replace("</desc>",")")
		txt = re.sub(" +"," ", txt).strip()
		#<FirstName/>
		return(txt)
		
	def parseLine(line,header):
		spkName = row[header.index("Speaker")]
		rName = row[header.index("ResourceName")]
		charName = spkName
		#if spkName in dictOfNames:
		#	if len(dictOfNames[spkName])==1:
			# This is a unique speaker name
			#  (only one model resource name), so just use that
		#		charName = spkName
		
		# If there's no speaker name, use the resource name
		if spkName == "":
			charName = rName
		# If it's the player, just use player
		if spkName == "Player":
			charName = "Player"
		# Modifiers for character names
		for x in [" Main"," Faryn"," Scavenger","Epi "]:
			charName = charName.replace(x,"").strip()

		dialogue = row[header.index("Text")]
		isDebug = False
		if charName.lower().count("debug")>0 or dialogue.lower().count("debug")>0:
			charName = "SYSTEM"
			dialogue = "("+ dialogue+ ")"
			isDebug = True

		if dialogue.startswith("<desc>") and dialogue.strip().endswith("</desc>"):
			charName = "SYSTEM"
		
		actions = ""
		if dialogue.count("<act>")>0:
			# <act>Lie</act> He's guilty. Here's the lyrium. <act>Give 1 nugget.</act>
			partIsAction = True
			parts = re.split("</?act>",dialogue)
			dialogue = " ".join(parts[::2])
			dialogue = re.sub(" +"," ", dialogue)
			actions = "; ".join(parts[1::2])				
		
		outx = {charName: cleanLine(dialogue), "_ID": row[header.index("StringID")]}
		
		if len(actions)>0:
			outx["_Action"] = actions
		
		cx = row[header.index("VoiceOverComment")]
		for comment in [x.strip() for x in cx.split("\n") if len(x.strip())>0]:
			if comment.startswith("IF PC IS"):
				pass
			elif comment.count(" = "):
				# comment is context
				if "context" in outx:
					outx["_Context"] += " ; " + comment
				else:
					outx["_Context"] = comment
			else:
				# comment is voice direction
				if "direction" in outx:
					outx["_Direction"] += " ; " + comment
				else:
					outx["_Direction"] = comment	
		
		if isDebug:
			outx["_Debug"] = "True"			
		
		return(outx)	
	
	# Work out which names are unique
	# By building a dictionary of script name to resource names
# 	dictOfNames = {}
# 	header = []
# 	with open(fileName) as csvfile:
# 		csvreader = csv.reader(csvfile)
# 		for row in csvreader:
# 			if len(header)==0:
# 				header = row
# 			else:
# 				spkName = row[header.index("Speaker")]
# 				rName = row[header.index("ResourceName")]
# 				if not spkName in dictOfNames:
# 					dictOfNames[spkName] = []
# 				if not rName in dictOfNames[spkName]:
# 					dictOfNames[spkName].append(rName)
# 	print(dictOfNames["Wynne"])
	
	resourceNameByGender = {"female":[],"male":[]}
	
	# Build directory of lines by speaker and who they are speaking to
	# ResourceName,ModuleResRefVersionID,StringID,VoiceOverComment,Text,Speaker
	lineDirectory = {}
	header = []
	with open(fileName) as csvfile:
		csvreader = csv.reader(csvfile)
		for row in csvreader:
			if len(header)==0:
				header = row
			else:
				line = parseLine(row,header)
				rn = row[header.index("Speaker")]
				ltype = "universal"
				if row.count("IF PC IS FEMALE")>0 or row.count("IF PC IS A FEMALE")>0:
					ltype = "toFemale"
				elif row.count("IF PC IS MALE")>0 or row.count("IF PC IS A MALE")>0:
					ltype = "toMale"
					
				if rn in lineDirectory:
					if ltype in lineDirectory[rn]:
						lineDirectory[rn][ltype].append(line)
					else:
						lineDirectory[rn][ltype] = [line]
				else:
					lineDirectory[rn] = {}
					lineDirectory[rn][ltype] = [line]

				# Attempt to identify gender from resource name
				tspk = row[header.index("Speaker")]+"#" + row[header.index("ResourceName")]
				rn = row[header.index("ResourceName")]
				if rn.count("_f_"):
					resourceNameByGender["female"].append((rn,tspk))
				if rn.count("_m_"):
					resourceNameByGender["male"].append((rn,tspk))
				
	# Now build out for each char
	out = []	
	for rn in lineDirectory:
		rDir = lineDirectory[rn]
		# Universal lines (to all PCs)
		if "universal" in rDir:
			out += rDir["universal"]
			
		# text dependent on player gender
		choices = []
		if "toFemale" in rDir:
			choices.append([{"STATUS": "PC is female"}] + rDir["toFemale"])
		else:
			choices.append([])
		#######
		if "toMale" in rDir:
			choices.append([{"STATUS": "PC is male"}] + rDir["toMale"])
		else:
			choices.append([])
		if len(choices[0])>0 or len(choices[1])>0:
			out.append({"CHOICE":choices})
	
	if asJSON:
		print(json.dumps({"text":out}, indent = 4))
		return(json.dumps({"text":out}, indent = 4))
	return(out)
	


	


	

	

	
	



