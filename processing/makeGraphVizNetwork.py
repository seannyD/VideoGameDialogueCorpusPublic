import json,csv


def makeGraphViz(lines,outputFile):

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
				
	
	def makeVis(links, idToLine):
		allLinks = list(links.keys())
		for k in links:
			allLinks += links[k]
		allLinks = list(set(allLinks))
		gv = "digraph {\nrankdir=LR;\n"
		for link in allLinks:
			thisLine = idToLine[link]
			style = ""
			if thisLine.startswith("ACTION"):
				style = ' shape=diamond'
				if thisLine.count("AGREE")>0:
					style += " style=filled fillcolor=lightgreen"
				elif thisLine.count("DISAGREE")>0:
					style += " style=filled fillcolor=lightred"
				elif thisLine.count("INVESTIGATE")>0:
					style += " style=filled fillcolor=lightblue"
				elif thisLine.count("FRIENDLY")>0:
					style += " style=filled fillcolor=lightpink"						
			elif thisLine.startswith("STATUS"):
				style = " shape=rectangle"
			gv += "  N"+link + "[ label=\"" + thisLine + "\"" +style + "];\n"
		colours = ["dodgerblue2","goldenrod2","antiquewhite4","deeppink4","blueviolet","blue","aquamarine3","cyan2","darkgray","darkslategray2","chartreuse4","darkviolet","gold2","darkolivegreen","cadetblue4","coral4","brown4","darkorchid","darkred","darkgoldenrod","firebrick2","bisque2","darkseagreen3","fuchsia","cornsilk3","deepskyblue4"]
		i = 0
		for source in links:
			for dest in links[source]:
				i += 1
				if i >=len(colours):
					i =0
				
				gv += "  N"+source + " -> " + "N"+dest + " [color="+colours[i]+"]" +"\n"
		gv += "\n}"
		return(gv)
		
	idToLine["START"] = "START"
	gv = makeVis(links,idToLine)
	with open(outputFile,'w') as outfile:
		outfile.write(gv)


with open("../results/doNotShare/ME/Antagonists/AriaIntro.json") as json_file:
	lines = json.load(json_file)["text"]		
makeGraphViz(lines, "../results/doNotShare/ME/Antagonists/AriaIntro.dot")