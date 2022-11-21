from bs4 import BeautifulSoup
import json


def parseFile(fileName,parameters={"characterClassIdentifier":"DAI"},asJSON=False):
		
	html_= open(fileName,'r', encoding = 'utf8')
	soup = BeautifulSoup( html_, "html.parser")
	posts = soup.find('div', class_='posts')

	




	def lineOfDialogueParser(element):
		# parse one line of dialogue
		scriptLine = element.getText()
		if scriptLine.count(":")>0:
			# split by colon
			characterName = scriptLine[:scriptLine.index(":")].strip()
			dialogue = scriptLine[scriptLine.index(":")+1:].strip()
			return({characterName:dialogue})
		return(None)

	# variable for the output
	out = []
	outx = []
	optionalDialogueSection = False
	# Loop through children of the post
	for child in posts.children:
		# Recognise what kind of thing this is:
		if child.name == "p":
			parsedLine = lineOfDialogueParser(child)
			if parsedLine is not None:
				out.append(parsedLine)

		if child.name == "ul":
			choices = []
			liLines = []
			lines = child.find_all('li')
			for l in lines:
				playerDialogue = []
				optionalDialogue = []
				for i in l.find_all('b'):
					for o in optionalDialogue:
						optionalDialogue.append(o.getText())
				for i in l.find_all('b'):
					i.decompose()
				playerDialogue.append(i.getText())
			liLines.append({'CHOICE':playerDialogue,  '_Option':optionalDialogue})
			choices.append(liLines)
			out.append(choices)

			

			# ... code to parse a list (dialogue options)
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)
	


	


	

	

	
	



