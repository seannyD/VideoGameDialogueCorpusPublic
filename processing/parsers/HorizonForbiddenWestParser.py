from bs4 import BeautifulSoup
import json, re

# TODO
# Check whether filtering datapoint logs is working.


def parseFile(fileName,parameters={},asJSON=False):

	d = open(fileName).read()
	html = BeautifulSoup(d, 'html.parser')
	script = html.find("div",{"id":"post-toc"})
	script = script.get_text()
	
	script = script[script.index(parameters["scriptStartCue"]):script.index(parameters["scriptEndCue"])]
	
	script = script.replace("We will make use of a lesson learned from an early age", ":  We will make use of a lesson learned from an early age")
	script = script.replace("Kotalo","Kotallo")
	script = script.replace("Contract:", "Contract - ")
	script = script.replace("Errand:", "Errand - ")
	script = script.replace("Interlude:", "Interlude - ")
	script = script.replace("Vart", "Varl")
	
	lines = script.split("\n")
	lines = [line.strip() for line in lines if len(line.strip())>0]
	out = []
	for line in lines:
		#print(line)
		if line.startswith("["):
			out.append({"ACTION": line[1:-1]})
		elif line.count(":")==0:
			out.append({"LOCATION": line})
		else:
			charName,dialogue = line.split(":",1)
			out.append({charName:dialogue})


	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)
