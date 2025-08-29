# TODO: Check if first section

from corpusHelpers import *
import os, sys, csv, json, copy
import random
from tqdm import tqdm
from scipy.stats import chisquare


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
# Skip mass effect for now, and use the custom method below
foldersToProcess = [x for x in foldersToProcess if x.count("MassEffect")==0]


data = []
gamesPresent = {}
for folder in foldersToProcess:

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
			print("PROCESSING "+folder+ " ...")
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
				#data += random.choices(gameData,k=20)
				data += gameData
			
		else:
			print("No main char for "+folder)



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
		# (omit prompts, i.e. 'choices')
		gameData.append([folder,game,prevLine,firstActualLine])
		try:
			gamesPresent[game] += 1
		except:
			gamesPresent[game] = 1
	
	print((folder,len(gameData)))
	if len(gameData)>0:
		#data += random.choices(gameData,k=20)
		data += gameData


##################

def tokenise(text):
	text = re.sub("\\[.+?\\]"," ",text)
	text = re.sub("\\(.+?\\)"," ",text)
	text = text.lower()
	text = text.replace("player chooses"," ")
	text = re.sub("[0-9]"," ",text)
	text = re.sub("[\\?\\.,:;\\-'\"!’]"," ",text)
	words = text.split(" ")
	words = [x for x in words if len(x.strip())>0]
	return(words)

# list of (folder,game,prevLine,firstActualLine)

print(data[1])

data = [x for x in data if len(x[1])>1]

freq = {}

# Between freq
for folder,game,prevLine,lines in tqdm(data):
	dialogues = [line[getCharName(line)] for line in lines]
	for i1 in range(0,len(dialogues)-1):
		d1 = dialogues[i1]
		words1 = tokenise(d1)
		for i2 in range(i1+1,len(dialogues)):
			d2 = dialogues[i2]
			if d1 != d2:
				words2 = tokenise(d2)
				for w1 in words1:
					for w2 in words2:
						if w1!=w2:
							w1,w2 = sorted([w1,w2])
							if not w1 in freq:
								freq[w1] = {}
							if not w2 in freq[w1]:
								freq[w1][w2] = 0
							freq[w1][w2] += 1

# Collocation within lines		
withinFreq = {}
for folder,game,prevLine,lines in tqdm(data):
	dialogues = [line[getCharName(line)] for line in lines]
	for dialogue in dialogues:
		words1 = tokenise(dialogue)
		for i1 in range(0,len(words1)-1):
			w1 = words1[i1]
			for i2 in range(i1+1,len(words1)):
				w2 = words1[i2]
				if w1!=w2:
					w1,w2 = sorted([w1,w2])
					if not w1 in withinFreq:
						withinFreq[w1] = {}
					if not w2 in withinFreq[w1]:
						withinFreq[w1][w2] = 0
					withinFreq[w1][w2] += 1
						
if False:
	allWords = [x for x in freq.keys()]
	out = "w1," + ",".join(allWords) + "\n"
	for w1 in allWords:
		out += w1+","
		for w2 in allWords:
			f = 0
			if w1 in freq:
				if w2 in freq[w1]:
					f = freq[w1][w2]
			out += str(f)+"," 
		out += "\n"

	o = open("../results/doNotShare/choiceDifferences.csv",'w')
	o.write(out)
	o.close()
	
#########

# minTotalFreq = 10
# minPairFreq = 5
# minPairProb = 0
# 
# out = "w1,w2,str\n"
# for w1 in tqdm(freq):
# 	w1sum = sum([freq[w1][w2] for w2 in freq[w1]])
# 	if w1sum > minTotalFreq:
# 		#freq[w1] = dict(zip(freq[w1].keys(),[freq[w1][w2]/w1sum for w2 in freq[w1]]))
# 		fx = [(w1, w2, freq[w1][w2]/w1sum) for w2 in freq[w1] if freq[w1][w2]>minPairFreq]
# 		fx = [x for x in fx if x[2]>minPairProb]
# 		for w1o,w2o,fo in fx:
# 			out += w1o+","+w2o+","+str(fo)+"\n"
# o = open("../results/doNotShare/choiceDifferences.csv",'w')
# o.write(out)
# o.close()


smoothFreq = 1
minFreqBetween = 5

out = "w1,w2,between,within,str\n"
for w1 in tqdm(freq):
		for w2 in freq[w1]:
			freqBetween = freq[w1][w2]
			if freqBetween > minFreqBetween:
				freqWithin = 0
				if w1 in withinFreq:
					if w2 in withinFreq[w1]:
						freqWithin = withinFreq[w1][w2]
				elif w2 in withinFreq:
					if w1 in withinFreq[w2]:
						freqWithin = withinFreq[w2][w1]
				
				freqBetween += smoothFreq
				freqWithin += smoothFreq
		
				bRatio = freqBetween / freqWithin
				out += w1+","+w2+","+str(freqBetween)+","+str(freqWithin)+","+str(bRatio)+"\n"

o = open("../results/doNotShare/choiceDifferences.csv",'w')
o.write(out)
o.close()