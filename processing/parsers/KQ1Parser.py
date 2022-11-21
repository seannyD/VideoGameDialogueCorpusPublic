from bs4 import BeautifulSoup
import json
import re

def parseFile(fileName,parameters={},asJSON=False):
	
	o = open(fileName)
	d = o.read()
	o.close()
	
	d = d[d.index(parameters["startText"]):]
	d = d[:d.index(parameters["endText"])]
	
	d = d.replace("But I fear that my wife grows weaker still for lack of food.", 'But I fear that my wife grows weaker still for lack of food."')
	d = d.replace("I can smell you there!", 'I can smell you there!"')
	d = d.replace("Whaddaya tryin' to do, cheat me with that measly offering? What an insult.", "RAT: \"Whaddaya tryin' to do, cheat me with that measly offering? What an insult.\"")
	
	html = BeautifulSoup(d, 'html.parser')
	
	t = html.getText()

	t = t.replace("\n"," ")
	t = re.sub(" +"," ",t)

	out = []
		
	dialogue = re.findall('[A-Z][A-Z ]+: +".+?"',t)
	for d in dialogue:
		character = d[:d.index(":")].strip()
		dialogue = d[d.index(":")+1:].replace('"',"").strip()
		out.append({character:dialogue})
		
	witchSection = t[t.index('As soon as you entered the gingerbread house'):t.index("There is a spider web above the door.")]
	
	witchDialogue = re.findall('"(.+?)" [0-9]',witchSection)
	for wd in witchDialogue:
		out.append({"WITCH":wd})
	out.append({"WITCH":"Nibble, nibble, little mouse. Who is nibbling at my house?"})
	out.append({"WITCH":"Who is there? I love visitors, especially young, tender ones! Come in, come in!"})
	
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)
