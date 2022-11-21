# Find parallel dialogue from two characters
# e.g. Kaiden and Ashley's alternative lines

import json,csv
from textatistic import word_array

with open("../../data/MassEffect/MassEffect1B/data.json") as json_file:
	ME1lines = json.load(json_file)["text"]
with open("../../data/MassEffect/MassEffect2/data.json") as json_file:
	ME2lines = json.load(json_file)["text"]
with open("../../data/MassEffect/MassEffect3C/data.json") as json_file:
	ME3lines = json.load(json_file)["text"]
	

def findSpeakerAltDialogue(lines,speakers, prevLine={}):

	for line in lines:
		if isinstance(line,dict):
			mainKey = [x for x in line if not x.startswith("_")][0]
			if mainKey == "CHOICE":
				# Look ahead
				choices = line["CHOICE"]
				nextLevelChars = []
				nextLevelLines = {}
				for choice in choices:
					for choiceLine in choice:
						k = [x for x in choiceLine if not x.startswith("_")][0]
						if k in speakers:
							nextLevelChars.append(k)
							if not k in nextLevelLines:
								nextLevelLines[k] = []
							nextLevelLines[k].append(choiceLine)
				if all([spk in nextLevelChars for spk in speakers]):
					yield (prevLine,[nextLevelLines[spk] for spk in speakers])
				# Now follow the choices
				for choice in choices:
					for result in findSpeakerAltDialogue(choice,speakers,prevLine):
						yield result
			else:
				if not mainKey in ["CHOICE","GOTO",'ACTION',"LOCATION"]:
					prevLine = line
		elif isinstance(lines,list):
			for line in lines:
				for result in findSpeakerAltDialogue(line,cues,speakers):
					yield result

def writeToCSV(speakers,spkSets,fileName):
	with open(fileName, 'w') as csvfile:
		csvwriter = csv.writer(csvfile)
		header = ["previousSpeaker","previousLine"]
		for spk in speakers:
			header += [spk+"_ID",spk]
		csvwriter.writerow(header)
		for prevLine,spkSet in spkSets:
			prevSpk = [x for x in prevLine if not x.startswith("_")][0]
			row = [prevSpk,prevLine[prevSpk]]
			for i in range(len(speakers)):
				spk = speakers[i]
				spkLines =spkSet[i]
				spkDialogue = " / ".join([spkLine[spk] for spkLine in spkLines])
				spkIds = ";".join([spkLine["_ID"] for spkLine in spkLines])
				row += [spkIds,spkDialogue]
			csvwriter.writerow(row)

speakers = ["Kaidan Alenko","Ashley Williams"]

writeToCSV(speakers,findSpeakerAltDialogue(ME1lines, speakers), "../../results/doNotShare/ME/AshleyKaidan/ME1_Ashley_Kaidan.csv")

writeToCSV(speakers,findSpeakerAltDialogue(ME2lines, speakers), "../../results/doNotShare/ME/AshleyKaidan/ME2_Ashley_Kaidan.csv")

writeToCSV(speakers,findSpeakerAltDialogue(ME3lines, speakers), "../../results/doNotShare/ME/AshleyKaidan/ME3_Ashley_Kaidan.csv")

# Get all dialogue and dump into text file

def getTextByCharacters(var,characterKeys):
	if isinstance(var,dict) or isinstance(var,list):
		for k in var:
			if isinstance(var, dict):
				v = var[k]
				if k in characterKeys:
					yield v
				for result in getTextByCharacters(v,characterKeys):
					yield result
			elif isinstance(var, list):
				for result in getTextByCharacters(k,characterKeys):
					yield result

for spk in speakers:
	ME1SD= "\n".join([x for x in getTextByCharacters(ME1lines,[spk]) if len(x)>0])
	with open("../../results/doNotShare/ME/AshleyKaidan/AllDialogue_ME1_"+spk+".txt",'w') as outf:
		outf.write(ME1SD)
	ME2SD= "\n".join([x for x in getTextByCharacters(ME2lines,[spk]) if len(x)>0])
	with open("../../results/doNotShare/ME/AshleyKaidan/AllDialogue_ME2_"+spk+".txt",'w') as outf:
		outf.write(ME2SD)
	ME3SD= "\n".join([x for x in getTextByCharacters(ME3lines,[spk]) if len(x)>0])
	with open("../../results/doNotShare/ME/AshleyKaidan/AllDialogue_ME3_"+spk+".txt",'w') as outf:
		outf.write(ME3SD)
