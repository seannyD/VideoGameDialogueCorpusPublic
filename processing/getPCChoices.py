from corpusHelpers import *
import os, sys, csv, json, copy
import random


def getCharName(line):
	return([k for k in line if not k.startswith("_")][0])
	
def isPCDialogueChoice(firstChoices):
	return(all([getCharName(x) in PC or x[getCharName(x)].count("Player chooses")>0 for x in firstChoices]))

def walkDialogue(lines, PC):
	
	prevLine = {}
	for line in lines:
		charName = getCharName(line)
		if charName == "CHOICE":
			firstChoices = [x[0] for x in line["CHOICE"] if len(x)>0]
			if(len(firstChoices)>1 and isPCDialogueChoice(firstChoices)):
				yield((prevLine,firstChoices))
			for choice in line["CHOICE"]:
				for res in walkDialogue(choice,PC):
					yield res
		else:
			prevLine = line



allFolders = [root+os.sep for root,dirs,files in os.walk("../data/") if "meta.json" in files]

foldersToProcess  = []

# Allow parsing of just one game
if len(sys.argv)>1:
	fx = sys.argv[-1]
	if not fx.endswith(os.sep):
		fx += os.sep
	foldersToProcess = [fx]
else:
	for f in allFolders:
		foldersToProcess.append(f)
		
#foldersToProcess = [x for x in foldersToProcess if x.count("Skyrim")==0]
foldersToProcess = [x for x in foldersToProcess if x.count("Test")==0]


data = []
gamesPresent = {}
for folder in foldersToProcess:
	#print("PROCESSING "+folder+ " ...")

	with open(folder+"meta.json") as json_file:
		meta = json.load(json_file)
		
	altGame = False
	if "alternativeMeasure" in meta:
		altGame = True
	
	if not altGame:
		game = meta["game"]
		with open(folder+"data.json") as json_file:
			d = json.load(json_file)["text"]
		mainChars = meta["mainPlayerCharacters"]
		if len(mainChars)>0:
			gameData = []
			PC = ["ACTION", mainChars[0]]
			for prevLine, choices in walkDialogue(d,PC):
				gameData.append([folder,game,prevLine,choices])
				try:
					gamesPresent[game] += 1
				except:
					gamesPresent[game] = 1
			
			print((folder,len(gameData)))
			if len(gameData)>0:
				data += random.choices(gameData,k=20)
			
		else:
			print("No main char for "+folder)

#print(askjdn)

for g in gamesPresent:
	print(g + " " + str(gamesPresent[g]))
print(len(gamesPresent))

if True:
	with open('../data/ALL/ChoiceSample2.csv', 'w') as csvfile:
		csvwriter = csv.writer(csvfile)
		csvwriter.writerow(["folder","game","prevLine","choices"])
		for folder,game,prevLine,choices in data:
			print(choices)
			charName = getCharName(choices[0])
			choiceDialogue = [x[getCharName(x)] for x in choices]
			csvwriter.writerow([folder,game,prevLine,charName]+choiceDialogue)



###############################
# Custom for Mass Effect
		
def walkDialogueME(lines, PC):
	
	prevLine = {}
	for line in lines:
		charName = getCharName(line)
		if charName == "CHOICE":
			# {"ACTION": "DISAGREE", "_PROMPT": "\"It was necessary.\""},
			firstChoices = [x[0] for x in line["CHOICE"] if len(x)>0 and "_PROMPT" in x[0]]
			if(len(firstChoices)>1 and isPCDialogueChoice(firstChoices)):
				firstActualLines = []
				for x in [x for x in line["CHOICE"] if len(x)>0 and "_PROMPT" in x[0]]:
					if "GOTO" in x[1]:
						idx = x[1]["GOTO"]
						if not idx in lineDict:
							firstActualLines.append({"Shepard":idx})
						else:
							firstActualLines.append(lineDict[x[1]["GOTO"]])
					elif "Shepard" in x[1]:
						firstActualLines.append(x[1])
					else:
						firstActualLines.append({"Shepard": "XX"})
				yield((prevLine,firstChoices,firstActualLines))
			for choice in line["CHOICE"]:
				for res in walkDialogueME(choice,PC):
					yield res
		else:
			prevLine = line

def walkDictionary(lines, PC):
	for line in lines:
		charName = getCharName(line)
		if charName == "CHOICE":
			for choice in line["CHOICE"]:
				for res in walkDictionary(choice,PC):
					yield res
		elif charName == PC:
			yield (line["_ID"],line)
	
lineDict = {}
gameData = []
data = []		
foldersToProcess = ["../data/MassEffect/MassEffect1B/", "../data/MassEffect/MassEffect2/", "../data/MassEffect/MassEffect3C/"]
for folder in foldersToProcess:
	#print(folder)
	with open(folder+"meta.json") as json_file:
		meta = json.load(json_file)
	game = meta["game"]
	with open(folder+"data.json") as json_file:
		d = json.load(json_file)["text"]
	mainChars = meta["mainPlayerCharacters"]
	
	lineDict = {}
	for idx,txt in walkDictionary(d,"Shepard"):
		lineDict[idx] = txt
		
	gameData = []
	for prevLine, choices, firstActualLine in walkDialogueME(d,"ACTION"):
		gameData.append([folder,game,prevLine,choices,firstActualLine])
		try:
			gamesPresent[game] += 1
		except:
			gamesPresent[game] = 1
	
	print((folder,len(gameData)))
	if len(gameData)>0:
		data += random.choices(gameData,k=20)

with open('../data/ALL/ChoiceSampleME.csv', 'w') as csvfile:
	csvwriter = csv.writer(csvfile)
	csvwriter.writerow(["folder","game","prevLine","choices"])
	for folder,game,prevLine,choices,firstActualLine in data:
		print("====")
		print(choices)
		charName = getCharName(choices[0])
		choicePrompts = [x[getCharName(x)] + ":" + x["_PROMPT"] for x in choices]
		print(firstActualLine)
		choiceSpeech = [x["Shepard"] for x in firstActualLine]
		choiceDialogue = [x[0]+" -> "+x[1] for x in zip(choicePrompts, choiceSpeech)]
		csvwriter.writerow([folder,game,prevLine,charName]+choiceDialogue)