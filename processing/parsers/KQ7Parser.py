from bs4 import BeautifulSoup
import json
import re
from corpusHelpers import levenshtein_ratio_and_distance


def parseFile(fileName,parameters={},asJSON=False):

	def cleanText(dialogue):
		dialogue = dialogue.replace("::marker","")
		dialogue = dialogue.replace("\n"," ")
		dialogue = re.sub('^ *"',"",dialogue)
		dialogue = re.sub(',([A-Za-z])',", \1",dialogue)
		dialogue = re.sub('" *$',"",dialogue)
		dCue = ""
		if dialogue.startswith("("):
			dCue = dialogue[1:dialogue.index(")")]
		# remove text within brackets
		dialogue = re.sub("\(.+?\)","",dialogue).strip()
		dialogue = re.sub("<.+?>","",dialogue).strip()
		dialogue = dialogue.replace("..."," ... ")
		dialogue = re.sub(" +"," ",dialogue)
		return((dialogue,dCue))
		
	def lineShouldBeAdded(dialogue,dataKey):
		if dataKey in seenKeys:
			# Check other bits of dialogue to see if they're similar
			for prevDialogue in seenKeys[dataKey]:
				levenshteinSimilarity = levenshtein_ratio_and_distance(dialogue, prevDialogue, ratio_calc=True)
				# (measure is 1.0 if strings are identical)
				if levenshteinSimilarity > 0.8:
					# If very similar to previously seen, then don't add
					return(False)
		return(True)
	
	o = open(fileName)
	d = o.read()
	o.close()
	
	if "startText" in parameters:
		d = d[d.index(parameters["startText"]):]
	if "endText" in parameters:
		d = d[:d.index(parameters["endText"])]
	
	# Individual fixes for source
	d = d.replace('I should fin out',"I should find out")
	d = d.replace("(MALICIA - FURIOUS, SHRIEKING) NOOOOOOO!", "\"\n0 0 2 6 12 \"(MALICIA - FURIOUS, SHRIEKING) NOOOOOOO!\"")
	d = d.replace("EXTREMELY POLIT)","EXTREMELY POLITE)")
	d = d.replace('"THINKS TO HERSELF)','"(THINKS TO HERSELF)')
	d = d.replace('"CURIOUS)','"(CURIOUS)')
	d = d.replace('"OVERCOME WITH GRIEF)','"(OVERCOME WITH GRIEF)')

	html = BeautifulSoup(d, 'html.parser')
	
	# replace <br> with space
	for br in html.find_all("br"):
		br.replace_with(" ")
	
	out = []
	seenKeys = {}
	
	lastScene = ""
	chapter = "1"
	
	for bit in list(html.children):
	
		if bit.name in ["h2","h3"]:
			chapter = bit.get_text()
	
		if bit.name == "p":
			tx = bit.getText().strip()
			if len(tx)>0:
#				0 0 7 1 2 "Ooooh! I can't believe I ate BUGS! I'll never do THAT again!" 
				lines = re.findall('[0-9]{1,2} [0-9]{1,2} [0-9]{1,2} [0-9]{1,2} [0-9]{1,3} ".+?"', tx)
				for line in lines:
					data = line[:line.index('"')].strip()
					dataParts = data.split(' ')
					scene = str(dataParts[0]) + "_" + str(dataParts[1])+"_"+str(dataParts[2])
					dataKey = data

					if len(dataParts)==5:					
						characterNum = dataParts[4]
						dialogue = line[line.index('"'):]
						dialogue,cue = cleanText(dialogue)
						sortKey = chapter + " " + " ".join([str(dataParts[i]).zfill(3) for i in range(5)])
						if len(dialogue)>0 and lineShouldBeAdded(dialogue, dataKey):
							try:
								seenKeys[dataKey].append(dialogue)
							except:
								seenKeys[dataKey] = [dialogue]
							if scene != lastScene and lastScene!="":
								out.append((sortKey,{"ACTION":"---"}))
							lastScene = scene
							
							dout = {characterNum:dialogue}
							if len(cue)>0:
								if cue=="THINKS TO HERSELF":
									#dout = {"ACTION": 'Thinks to herself:"'+ dialogue + '"'}
									dout = {characterNum:dialogue, "_Cue":cue}
								else:
									dout["_Cue"] = cue
							out.append((sortKey,dout))
	# Sort by id number
	out.sort(key=lambda x: x[0])
	# Remove sort keys
	out= [x[1] for x in out]
						

	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)
