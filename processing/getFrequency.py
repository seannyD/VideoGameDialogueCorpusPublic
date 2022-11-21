# TODO: 


print("Loading libraries ...")
import os, json, re, csv, sys, math
#from corpusHelpers import *
# For log likelihood calculator
from corpus_toolkit import corpus_tools as ct

#from nltk.stem import WordNetLemmatizer
#from nltk import pos_tag
#from nltk.corpus import wordnet

from corpusHelpers import *

from textatistic import punct_clean, word_array

#from scipy import stats

#spacyTokeniserModel = "en_core_web_md"


keywordsMustAppearInBothMaleAndFemaleDialogue = True
minimumFrequencyThreshold = 100
numberOfWordsInKeywords = 100

def latex_float(f):
	float_str = "{0:.2g}".format(f)
	if "e" in float_str:
		base, exponent = float_str.split("e")
		return r"{0} \times 10^{{{1}}}".format(base, int(exponent))
	else:
		return float_str

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

male_texts = []
female_texts = []

charDialogue = {}

numGames =0
		
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
			
			numGames += 1
			
			name2Group = getNameToGroup(meta)
			series = meta["series"]
			game = meta["game"]
			
			for charName, dialogue in getAllCharacterTexts(d, getNames=True):
				# remove text in parentheses
				dialogue = re.sub("\(.+?\)"," ",dialogue)
				# from corpusHelpers
				dialogue = cleanText(dialogue)
				group = ""
				try:
					group = name2Group[charName]
				except:
					pass
				if group in ["male","female"]:
					key = (folder,series,game,group,charName)
					if key in charDialogue:
						charDialogue[key].append(dialogue)
					else:
						charDialogue[key] = [dialogue]


print("Tokenising ...")

for k in charDialogue.keys():
	# Tokenise: From Textatistic, also applies "punct_clean"
	# (not just simple splitting by spaces)
	# Also convert to lowercase
	charDialogue[k] = [[wd.lower() for wd in word_array(line)] for line in charDialogue[k]]
	
print("Counting words ...")
# Make frequency dictionary
malefreq = {}
femalefreq = {}
for (folder,series,game,group,charName),lines in charDialogue.items():
	for line in lines:
		for word in line:
			if group=="male":
				try:
					malefreq[word] += 1
				except:
					malefreq[word] = 1
			elif group=="female":
				try:
					femalefreq[word] += 1
				except:
					femalefreq[word] = 1

male_texts = [charDialogue[k] for k in charDialogue if k[3]=="male"]
female_texts = [charDialogue[k] for k in charDialogue if k[3]=="female"]


def getTotalWordCount(texts):
	# Unpack tokenisation and check for empty strings
	return(sum([sum([len([word for word in words if len(word)>0]) for words in lines]) for lines in texts]))
	
totalMaleWords = getTotalWordCount(male_texts)
totalFemaleWords = getTotalWordCount(female_texts)
totalMaleAndFemaleWords = totalMaleWords+totalFemaleWords

def freq(targetWord="I"):
	f = femalefreq[targetWord]
	m = malefreq[targetWord]
	print("Females: " + str(f))
	print("Males: " + str(m))
	print(str(f / float(f+m)) + "% female")
	print("--")
	print("Females: " + str(1000000 * (f/totalFemaleWords)))
	print("Males: " + str(1000000 * (m/totalMaleWords)))
	
	a = f
	b = m
	c = totalFemaleWords
	d = totalMaleWords
	E1 = c*(a+b) / float(c+d)
	E2 = d*(a+b) / float(c+d)
	G2 = 2*((a*math.log(a/E1)) + (b*math.log(b/E2)))
	print(G2)
