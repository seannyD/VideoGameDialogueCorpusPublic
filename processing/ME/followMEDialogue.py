import json,csv


def followConv(lines,loc):

	# Make dictionary of ids to content,
	# and links between IDs
	links = {}
	idToLine = {"START":"START"}
	def getConvLinks(lines, prevLink = "START"):
		for line in lines:
			mainKey = [x for x in line if not x.startswith("_")][0]
			if mainKey == "CHOICE":
				choices = line["CHOICE"]
				for choice in choices:
					getConvLinks(choice,prevLink)
			elif mainKey == "GOTO":
				try:
					links[prevLink].append(line["GOTO"])
				except:
					links[prevLink] = [line["GOTO"]]
			else:
				# Add to idToLine
				if "_ID" in line:
					sid = line["_ID"]
				else:
					# (STATUS parts don't have IDs, so make one up)
					sid = "STATUS"+	str(len(idToLine))					
					line["_ID"] = sid
				idToLine[sid] = mainKey + ": " + line[mainKey]
				# Add links
				if line != {"ACTION": "---"}:
					try:
						links[prevLink].append(sid)
					except:
						links[prevLink] = [sid]
					prevLink = sid
				
	getConvLinks(lines)
				
	# Now walk through the links, keeping track of gender
	# assignments to each ID
	
	id2Gender = {"START":"START"}
	
	seenIDs = {}
	seenLinks = {}
	def walkLinks(startID, status=""):
		if startID in links:
			switchStatus = False
			for desitnationID in links[startID]:
				# (destline is string)
				destLine = idToLine[desitnationID]
				# Detect change in status
				if destLine.count("Shepard is female")>0:
					status = "F"
					switchStatus = True
				elif destLine.count("Shepard is male")>0:
					status = "M"
					switchStatus = True
				# Add to id2Gender
				if not desitnationID in id2Gender:
					id2Gender[desitnationID] = []
				if status != "":
					if not status in id2Gender[desitnationID]:
						id2Gender[desitnationID].append(status)
				
				# Should we continue?
				# Keep track of links we've done already, assume we won't go through the 
				# same link more than 10 times
				if not (startID,desitnationID) in seenLinks:
					seenLinks[(startID,desitnationID)] = 0
				seenLinks[(startID,desitnationID)] += 1
				if seenLinks[(startID,desitnationID)]<50:
					walkLinks(desitnationID,status)
				# If the gender status has been set, then we need to 
				# make all the subsequent alternative destinations be the opposite
				if switchStatus:
					if status == "F":
						status = "M"
					elif status == "M":
						status = "F"
	walkLinks("START")
	#print(id2Gender)
	
	femaleOnlyLines = []
	maleOnlyLines = []
	for lineID in id2Gender:
		if idToLine[lineID].count("ACTION")==0 and idToLine[lineID].count("STATUS")==0:
			if id2Gender[lineID] == ["F"]:
				femaleOnlyLines.append(idToLine[lineID])
			if id2Gender[lineID] == ["M"]:
				maleOnlyLines.append(idToLine[lineID])

	out = []
	longestListLength = max([len(femaleOnlyLines),len(maleOnlyLines)])
	for i in range(longestListLength):
		fLine = ""
		mLine = ""
		if i < len(femaleOnlyLines):
			fLine = femaleOnlyLines[i]
		if i < len(maleOnlyLines):
			mLine = maleOnlyLines[i]
		out.append([loc,fLine,mLine])
	if longestListLength>0:
		out.append(["","",""])
	return(out)
	
# 	def makeVis(links, idToLine):
# 		allLinks = list(links.keys())
# 		for k in links:
# 			allLinks += links[k]
# 		allLinks = list(set(allLinks))
# 		gv = "digraph {\nrankdir=LR;\n"
# 		for link in allLinks:
# 			thisLine = idToLine[link]
# 			style = ""
# 			if thisLine.startswith("ACTION"):
# 				style = ', style=filled, fillcolor="lightgray"'
# 			elif thisLine.startswith("AGREE"):
# 				style = ', style=filled, fillcolor="lightgreen"'
# 			elif thisLine.startswith("DISAGREE"):
# 				style = ', style=filled, fillcolor="lightred"'
# 			# TODO: This should be based on the gender coding, not the contents
# 			elif id2Gender[link]==["F"]:
# 				style = ', style=filled, fillcolor="lightpink"'
# 			elif id2Gender[link]==["M"]:
# 				style = ', style=filled, fillcolor="lightblue"'
# 			gv += "  N"+link + "[ label=\"" + thisLine + "\"" +style + "];\n"
# 		for source in links:
# 			for dest in links[source]:
# 				gv += "  N"+source + " -> " + "N"+dest + "\n"
# 		gv += "\n}"
# 		return(gv)
# 		
# 	idToLine["START"] = "START"
	#gv = makeVis(links,idToLine)
	#with open("../../results/doNotShare/ME/ShepGender/tmp.dot",'w') as outfile:
	#	outfile.write(gv)
		

def getGenderDifferentLines(inFileName,outFileName):
	with open(inFileName) as json_file:
		lines = json.load(json_file)["text"]		

	out = [["Location","FemaleOnly","MaleOnly"]]
	skipLocs = []
	seq = []
	for line in lines:
		if "LOCATION" in line:
			loc = line["LOCATION"]
			if len(seq)>0 and not loc in skipLocs:
				# TODO: add to out
				try:
					out += followConv(seq,loc)
				except:
					pass
				seq = []
		else:
			seq.append(line)
	# Process leftover dialogue		
	try:
		followConv(seq)
	except:
		pass

	with open(outFileName, 'w') as csvfile:
		csvwriter = csv.writer(csvfile)
		for x in out:
			csvwriter.writerow(x)
		
getGenderDifferentLines("../../data/MassEffect/MassEffect3C/data.json","../../results/doNotShare/ME/ShepGender/ME3_GenderDifferences.csv")

getGenderDifferentLines("../../data/MassEffect/MassEffect2/data.json","../../results/doNotShare/ME/ShepGender/ME2_GenderDifferences.csv")

getGenderDifferentLines("../../data/MassEffect/MassEffect1B/data.json","../../results/doNotShare/ME/ShepGender/ME1_GenderDifferences.csv")
