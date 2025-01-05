# For each choice, find the extremes for difference in the possible
#  number of words spoken by male and female characters.
# We're assuming that choice blocks in the main script level
#  are independent.
# This analysis only looks at dialogue within choices
#  (not main script dialogue)

from corpusHelpers import *
import os, sys, csv, json, copy
from textatistic import Textatistic,punct_clean,word_array,word_count
import random

	
def tokenizeLine(dialogueText):
	dialogueText = cleanText(dialogueText)
	dialogueText = dialogueText.lower()
	dialogueText = re.sub("[\\.,:;\"!?-]"," ",dialogueText)
	dialogueText = re.sub(" +"," ",dialogueText)
	if len(dialogueText)==0:
		return([])
	else:
		prepped_text = punct_clean(dialogueText)
		word_list = word_array(prepped_text, prepped=True)
		return(word_list)
		
def getCharKey(line):
	return([k for k in line if not k.startswith("_")][0])

	
def walkLines(lines,weight=1):
	# Count all normal dialogues (order doesn't matter)
	# and add to all parallel sums
	global wordFrequencies
	global wordFrequenciesWeighted
	
	dialogues = [line for line in lines if not getCharKey(line) in ["ACTION","CHOICE","LOCATION","COMMENT","STATUS","SYSTEM"]]
	for line in dialogues:
		if type(line) == dict:
			dialouge = line[getCharKey(line)]
			word_list = tokenizeLine(dialouge)
			for word in word_list:
				if not word in wordFrequencies:
					wordFrequencies[word] = 1
					wordFrequenciesWeighted[word] = weight
				else:
					wordFrequencies[word] += 1
					wordFrequenciesWeighted[word] += weight

	choices = [line for line in lines if getCharKey(line)=="CHOICE"]
	for choiceObject in choices:	
		for choice in choiceObject["CHOICE"]:
			if len(choice)>0:
				# Pass on weight divided equally between choices
				walkLines(choice,weight/len(choices))



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

#foldersToProcess = ["../data/MassEffect/MassEffect3C/", "../data/MassEffect/MassEffect1B/", "../data/MassEffect/MassEffect2/"]


#global wordFrequencies
#global wordFrequenciesWeighted

wordFrequencies = {}
wordFrequenciesWeighted = {}

numGames = 0
for folder in foldersToProcess:
	
	
	if not (os.path.isfile(folder+"meta.json") and os.path.isfile(folder+"data.json")):
		#print("##########")
		#print("JSON files not found")
		continue
	with open(folder+"meta.json") as json_file:
		meta = json.load(json_file)
	with open(folder+"data.json") as json_file:
		d = json.load(json_file)["text"]
		
	altMeasure = False
	if "alternativeMeasure" in meta:
		altMeasure = meta["alternativeMeasure"]
	
	allChoices = [x for x in d if "CHOICE" in x]

	# Script has no choices
	if len(allChoices)>0 and (not altMeasure):
		print("PROCESSING "+folder+ " ...")
		numGames += 1
		walkLines(d,weight=1)

		# Choice dialogue - limits

print("Number of games: "+str(numGames))

allWords = list(set([x for x in wordFrequencies.keys()]+ [x for x in wordFrequenciesWeighted.keys()]))
print(len(wordFrequencies))
out = "word,freq,freqWeighted\n"
for word in allWords:
	freq = 0
	freqW = 0
	if word in wordFrequencies:
		freq = wordFrequencies[word]
	if word in wordFrequenciesWeighted:
		freqW = wordFrequenciesWeighted[word]
	out += word + "," + str(freq) + "," + str(freqW) + "\n"
	
with open("../results/doNotShare/WeightedFreq.csv",'w') as csv_file:
	csv_file.write(out)