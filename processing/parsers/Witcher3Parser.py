from bs4 import BeautifulSoup,Tag, NavigableString
import json
import re
import xlrd
import copy
import os
import pprint


def parseFile(fileName,parameters={},asJSON=False):
	print(fileName)
	
	def cleanLine(line):
		line = line.replace("…"," ...")
		line = line.strip()
		return(line)
		
	def groupSubsections(sections,level=2):
		# Nest the choice structures
		out = []
		i = 0
		while i < len(sections):
			sec = sections[i]
			mx = re.split("0x[0-9a-z]+( +)",sec)
			print(sec)
			print('=====')
			if len(mx)>1:
				thisLevel = len(mx[1])
				if sec.count("Geralt choice:")>0 or sec.count("Cirilla choice:")>0:
					thisLevel += 2
				print(")))")
				print(thisLevel)
				if thisLevel > level:
					secP = parseLines(sec)
					sx,ix = groupSubsections(sections[i:],thisLevel)
					i += ix-1
					#out.append({"CHOICE":[secP]+sx})
					#out[-1] += secP+sx
					#out.append(sx)
					out.append({"CHOICE": sx})
				elif thisLevel < level:
					break
				elif sec.count("Geralt choice:")>0 or sec.count("Cirilla choice:")>0:
					out.append(parseLines(sec))
				else:
					if len(out)>0:
						if isinstance(out[-1],dict):
							out += parseLines(sec)
						else:
							out[-1] += parseLines(sec)
					else:
						out += parseLines(sec)
			i += 1
			
		out = [x for x in out if x!=[]]

		return((out,i))
	
	def parseLines(lines):
		out = []
		lines = lines.split('\n')
		lines = [x for x in lines if len(x)>0]
		for line in lines:
			x = parseLine(line)
			if not x is None:
				out.append(x)
		return(out)

	
	def parseLine(line):
		if line.strip().startswith("("):
			return(None)
		elif line.strip().startswith("==>"):
			return(None)
		else:
			print(line)
			print(re.split("([0-9]+)  (0x[0-9a-z]+)  (.+?):(.+)",line))
			d1,localID,globalID,charName,dialogue,d2 = re.split("([0-9]+)  (0x[0-9a-z]+)  (.+?):(.+)",line)
			dialogue = cleanLine(dialogue)
			charName = charName.strip()
			if charName in ["Geralt choice","Cirilla choice"]:
				dialogue = "PC CHOOSES: "+dialogue
				charName = "ACTION"
			return({charName: dialogue,"_ID":globalID.strip(),"_LID":localID.strip()})
	
	d = open(fileName).read()
	
	d = d.replace("(If player has\n","(")
	
	scenes = re.split("(.+w2scene:)",d)
	scenes = scenes[1:]
	scenes = zip(scenes[::2],scenes[1::2])
	
	out = []
	for sceneName,sceneText in scenes:
		out.append({"LOCATION":sceneName})
		sections = re.split("\n\n+",sceneText)
		subsections = sections
		
		if sceneText.count("Geralt choice:")>0:
			subsections,ix = groupSubsections(sections)
			print("!!!!!!!")
			pprint.pprint(subsections)
			print("!!!!!!!!!!!!!")
			#print(snfkjdnfksjn)

		for section in subsections:
			lines = []
			if isinstance(section,str):
				out += parseLines(section)
			else:
				out.append(section)
		
		# TODO: also add "---" at end of subsection?
		if len(out)>1 and not out[-1] == {"ACTION":"---"}:
			out.append({"ACTION":"---"})
			
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)
	
	
