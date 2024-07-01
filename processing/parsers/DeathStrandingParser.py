import json, re
from bs4 import BeautifulSoup

def parseFile(fileName,parameters={},asJSON=False):

	o = open(fileName)
	d = o.read()
	o.close()
	
	# TODO: sort lullaby
	#d = d.replace('<br/>\n<i>[]</i><br/>',"\n")
	
	d = d.replace("See the sunset<br/>\n","See the sunset // ")
	d = d.replace("The day is ending<br/>\n","The day is ending // ")
	d = d.replace("Let that yawn out<br/>\n","Let that yawn out // ")
	d = d.replace("There’s no pretending<br/>\n","There’s no pretending // ")
	d = d.replace("I will hold you<br/>\n","I will hold you // ")
	d = d.replace("And protect you<br/>\n","And protect you // ")
	d = d.replace("So let love warm you<br/>\n","So let love warm you // ")
	d = d.replace("Till the morning<br/>\n","Till the morning // ")

	d = d.replace("<b>Starring:</b>","<b>Starring - </b>")
	d = d.replace("<b>Special appearance:</b>","<b>Special appearance - </b>")
	d = d.replace("<b>Also starring:</b>","<b>Also starring - </b>")

	d = d[d.index("[]"):]
	d = d.replace("…"," … ")
	d = d.replace("Mama Holorgam","Mama Hologram")
	
	d = d.replace("’","'")
	
	#script = BeautifulSoup(d, 'html.parser')
	
	out = []
	for line in d.split("\n"):
		txt = re.sub("<.+?>"," ",line).strip()
		if len(txt.strip())>1:
			if ":" in txt:
				charName,dialogue = txt.split(":",1)
				if charName.count("Hologram")>0:
					dialogue = "(Hologram) "+dialogue
					charName = charName.replace("'s","").strip()
					charName = charName[:charName.index("Hologram")].strip()
				out.append({charName: dialogue.strip()})
			elif txt.strip() == "[]":
				out.append({"ACTION":"---"})
			elif txt.startswith("=="):
				out.append({"LOCATION":txt.replace("="," ").strip()})
			else:
				out.append({"ACTION":txt.strip()})
			
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)