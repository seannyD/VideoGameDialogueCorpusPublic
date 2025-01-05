from corpusHelpers import *
import os, sys, csv, json, copy
import random

numLinesPostDefeat = 4
defeatKeyWords = ["defeat","kills","killed"," kill ","wins","battle"]


def getCharName(line):
	return([k for k in line if not k.startswith("_")][0])

def lineIncludesDefeat(txt):
	txt = txt.lower()
	#return(any([txt.count(x)>0 for x in ["defeat","kills","wins","battle"]]))
	return(any([txt.count(x)>0 for x in defeatKeyWords]))

def walkDialogue(lines):
	for i in range(len(lines)):
		line = lines[i]
		charName = getCharName(line)
		if charName == "CHOICE":
			for choice in line["CHOICE"]:
				for res in walkDialogue(choice):
					yield res
		else:
			if "ACTION" in line and lineIncludesDefeat(line["ACTION"]):
				followingLines = []
				for j in [jx+1 for jx in range(numLinesPostDefeat)]:
					if (i+j)<len(lines):
						followingLines.append(lines[i+j])
				yield((line,followingLines))



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
gamesPresent = []
for folder in foldersToProcess:
	#print("PROCESSING "+folder+ " ...")

	with open(folder+"meta.json") as json_file:
		meta = json.load(json_file)
		
	altGame = False
	if "alternativeMeasure" in meta:
		altGame = True

	charName2Gender = {}
	for group in meta["characterGroups"]:
		for charName in meta["characterGroups"][group]:
			charName2Gender[charName] = group

	if not altGame:
		game = meta["game"]
		gamesPresent.append(folder)
		with open(folder+"data.json") as json_file:
			d = json.load(json_file)["text"]

		gameData = []
		
		def processFLines(line,followingLines):
			out = []
			for fline in followingLines:
				charName = [x for x in fline if not x.startswith("_")][0]
				charGender = ""
				if charName in charName2Gender:
					charGender = charName2Gender[charName]
					
				if charName in ["ACTION","LOCATION","GOTO"]:
					break
				elif charName in ["STATUS"]:
					continue
				elif charName == "CHOICE":
					for choice in fline["CHOICE"]:
						choice = choice[:min(3,len(choice))]
						out += processFLines(line,choice)
				else:
					out.append([folder,game,line,fline,charName,charGender])
			return(out)
			
		
		for line, followingLines in walkDialogue(d):
			#print(line)
			#for fLine in followingLines:
			#	print("\t\t\t"+str(fLine))
			#print("-----")
			out = processFLines(line,followingLines)
			if len(out)>0:
				gameData += out

		if len(gameData)>0:
			data += gameData

print(len(data))
xml = ""
for row in data:
	text = row[3][row[4]]
	text = text.replace("<","-").replace("\n", " ")
	context= row[2]["ACTION"].replace('"',"'")
	lx = f'<doc game="{row[1]}" charName="{row[4]}" gender="{row[5]}" context="{context}">{text}</doc>'
	xml += lx+"\n"
		
with open('../results/doNotShare/PostDefeat.xml', 'w') as xmlfile:
	xmlfile.write(xml)

import csv
prevContext = ""
with open('../results/doNotShare/PostDefeat.csv', 'w') as csvfile:
	writer = csv.writer(csvfile)
	writer.writerow(["folder","game","context","charName","charGender","line"])
	for row in data:
		if row[2] != prevContext:
			writer.writerow(["","","","","",""])
		prevContext = row[2]
		charName = row[4]
		line = row[3][charName]
		writer.writerow([row[0],row[1],row[2],charName,row[5],line])

for game in gamesPresent:
	print(game)