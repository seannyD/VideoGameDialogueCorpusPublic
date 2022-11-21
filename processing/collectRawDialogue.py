# Dump raw dialogue text for each game into a file

print("Loading libraries ...")
import os, json, re, csv, sys
from corpusHelpers import *


print("Collecting texts ...")
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

try:
	os.mkdir("../data/ALL")
except:
	pass

		
for folder in foldersToProcess:
	print(folder)
	if os.path.isfile(folder+"meta.json") and os.path.isfile(folder+"data.json"):
		with open(folder+"meta.json") as json_file:
			meta = json.load(json_file)
		with open(folder+"data.json") as json_file:
			d = json.load(json_file)["text"]
		
		includeGame = True
		# alternativeMeasure is true if this parsing should not count 
		# as part of the main list of results (e.g. alternative versions)
		if "alternativeMeasure" in meta:
			if meta["alternativeMeasure"]:
				includeGame = False
		
		if includeGame:
			gameDialouge = ""
			for charName, dialogue in getAllCharacterTexts(d, getNames=True):
				# remove text in parentheses
				dialogue = re.sub("\(.+?\)"," ",dialogue)
				# from corpusHelpers
				dialogue = cleanText(dialogue).strip()
				if len(dialogue)>0:
					gameDialouge += dialogue + "\n"
			# Write out
			gameFolder = [x for x in folder.split("/") if len(x)>0][-1]
			with open("../data/ALL/"+ gameFolder +".txt",'w') as o:
				o.write(gameDialouge)

