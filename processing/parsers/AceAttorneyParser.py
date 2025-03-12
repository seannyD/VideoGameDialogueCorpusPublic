from bs4 import BeautifulSoup,Tag, NavigableString
import json
import re
import xlrd
import copy
import os

def cleanLine(x):
	x = x.strip()
	x = x.replace("*"," * ")
	x = x.replace("(","( ")
	x = x.replace(")"," )")
	x = re.sub(" +"," ",x)
	return(x)


def parseFile(fileName,parameters={},asJSON=False):
	print(fileName)
	
	def getContentBlocks(content):
		contentBlocks = []
		tableBlock = []
		for element in content:
			if element.name is None:
				pass
			elif element.name == "table":
				tableBlock.append(element)
			else:
				if len(tableBlock)>0:
					contentBlocks.append(tableBlock)
					tableBlock = []
				contentBlocks.append(element)
		return(contentBlocks)
	
	
	def parseElement(element):
	
		if type(element) is list:
			choices = []
			for subtable in element:
				#print(subtable)
				choiceTitle = subtable.find("th")
				if not choiceTitle is None:
					choiceTitle = cleanLine(choiceTitle.get_text(separator=" "))
					choice = [{"ACTION": "USER SELECTS "+choiceTitle}]
					dat = subtable.find_all("td")
					for row in dat:
						contentBlocks = getContentBlocks(row)
						for el in contentBlocks:
							x = parseElement(el)
							if not x is None:
								choice += x
					choices.append(choice)
			if len(choices)==0:
				return(None)
			if len(choices) == 1:
				choices.append([])
			return([{"CHOICE": choices}])
	
		if element.name == "div":
			return([{"LOCATION": element.get_text(separator=" ")}])
		elif element.name == "p":
			hidden = element.find("span",{"style":"display: none;"})
			hiddenText = ""
			if not hidden is None:
				#print(hidden)
				hiddenText = hidden.get_text(separator=" ")
				hidden.extract()
			txt = element.get_text(separator=" ")
			if(txt.count(":")>0):
				charName,dialogue = txt.split(":",1)
				charName = cleanLine(charName)
				dialogue = cleanLine(dialogue)
				
				if charName.lower() in ["leads to", "leads back to"]:
					dialogue = charName + " " + dialogue
					charName = "ACTION"
				
				if len(charName)>20:
					dialogue = cleanLine(txt)
					charName = "ACTION"
				
				pic = element.find("a", {"class":"image"})
				if not pic is None:
					if pic["href"].count("Holdit"):
						dialogue += "HOLD IT!"
					elif pic["href"].count("Objection"):
						dialogue += "Objection!"				

				line = {charName : dialogue}
				if hiddenText!="":
					line["_info"] = hiddenText
				return([line])
		elif element.name == "hr":
			return([{"ACTION": "---"}])
		elif element.name == "center":
			return([{"ACTION": cleanLine(element.get_text(separator=" "))}])
			
	
	
	o = open(fileName)
	d = o.read()
	o.close()
	
	reps = parameters["replaces"]
	for targ,rep in reps:
		d = d.replace(targ,rep)
	
	soup = BeautifulSoup(d, 'html5lib')
	
	content = soup.find("div",{"class":"mw-content-ltr"})
	
	contentBlocks = getContentBlocks(content)
	
	out = []
	for element in contentBlocks:
		lines = parseElement(element)
		if not lines is None:
			out += lines

			
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)
	
	
def postProcessing(out):

	for line in out:
		if "CHOICE" in line:
			for choice in line["CHOICE"]:
				choiceType = ""
				for subline in choice:
					mainkey = [x for x in subline if not x.startswith("_")][0]
					if mainkey == "ACTION" and subline["ACTION"].startswith("USER SELECTS Press"):
						choiceType = "Press"
					elif mainkey in ["Phoenix"] and subline[mainkey].startswith("Objection!"):
						choiceType = "Objection"
						
					if choiceType !="":
						subline["_type"] = choiceType

	return(out)