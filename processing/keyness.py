# TODO: 


print("Loading libraries ...")
import os, json, re, csv, sys
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
spacy.load('en_core_web_trf')


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

with open("../results/latexStats/numberOfGames.tex",'w') as o:
	o.write(str(numGames))

print("Writing ALL files ..")
male_texts = [charDialogue[k] for k in charDialogue if k[3]=="male"]
female_texts = [charDialogue[k] for k in charDialogue if k[3]=="female"]

try:
	os.mkdir("../data/ALL")
except:
	pass
o = open("../data/ALL/male.txt",'w')
o.write("\n".join(sum(male_texts,[])))
o.close()

o = open("../data/ALL/female.txt",'w')
o.write("\n".join(sum(female_texts,[])))
o.close()

## (stats to latex is now moved to getStatistics.py)

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
				

print("Filtering ...")

if keywordsMustAppearInBothMaleAndFemaleDialogue:
	# remove words that only appear in either male or female text
	mk =[x for x in malefreq.keys()]
	fk = [x for x in femalefreq.keys()]
	commonWords = list(set(mk).intersection(set(fk)))
	for k in mk:
		if not k in commonWords:
			del malefreq[k]		
	for k in fk:
		if not k in commonWords:
			del femalefreq[k]


# Remove infrequent words
if minimumFrequencyThreshold>1:
	# all words
	words = [x for x in malefreq.keys()] + [x for x in femalefreq.keys()]
	words = list(set(words))
	for word in words:
		tot = 0
		if word in malefreq:
			tot += malefreq[word]
		if word in femalefreq:
			tot += femalefreq[word]
		if tot < minimumFrequencyThreshold:
			del malefreq[word]
			del femalefreq[word]


print("Getting keyness ...")
# Keyness
def getKeyness(target,reference):
	# ct.keyness returns a dictionary
	keyness = ct.keyness(target,reference, effect = "log-ratio")
	# sort by keyness sore
	corp_key = [(keyness[word],word, malefreq[word],femalefreq[word]) for word in keyness]
	corp_key.sort(reverse=True)
	# cut to just 1 to numberOfWordsInKeywords
	corp_key = corp_key[:numberOfWordsInKeywords]
	return(corp_key)
	
maleKeywords = getKeyness(malefreq,femalefreq)
femaleKeywords = getKeyness(femalefreq,malefreq)

out = "group,word,keyness,maleFreq,femaleFreq\n"
for keyness,word,mfreq,ffreq in maleKeywords:
	out += "male,"+word + "," + str(keyness) + "," + str(mfreq) + "," + str(ffreq)+ "\n"
for keyness,word,mfreq,ffreq in femaleKeywords:
	out += "female,"+word + "," + str(keyness) + "," + str(mfreq) + "," + str(ffreq)+ "\n"
	
o = open("../results/keyness/keyness.csv",'w')
o.write(out)
o.close()

print("Profiling ...")
def getWordFreqByCharacterMatrix(keywords):
	# for each character, get freq of each keyword
	out = [[".folder",".series",".game",".group",".charName",".totalWords"]+keywords ]
	for (folder,series,game,group,charName),lines in charDialogue.items():
		words = sum(lines,[])
		keywordFreq = [words.count(keyword) for keyword in keywords]
		out.append([folder,series,game,group,charName, str(len(words))]+[str(x) for x in keywordFreq])
	return(out)
	
# Get matrix of characters x freq
keywords = [word for keyness,word,mfreq,ffreq in maleKeywords]
keywords += [word for keyness,word,mfreq,ffreq in femaleKeywords]
keywords = list(set(keywords))

out = getWordFreqByCharacterMatrix(keywords)
with open("../results/keyness/keywordsByCharacter.csv", "w") as f:
	writer = csv.writer(f)
	writer.writerows(out)

print("TARGET WORDS ... ")
out = getWordFreqByCharacterMatrix(["i","me","my","you","he","she","they","them","his","hers","theirs"])
with open("../results/keyness/pronounsByCharacter.csv", "w") as f:
	writer = csv.writer(f)
	writer.writerows(out)
	
out = getWordFreqByCharacterMatrix(["who","what","why","where","when","how"])
with open("../results/keyness/questionWordsByCharacter.csv", "w") as f:
	writer = csv.writer(f)
	writer.writerows(out)
	



#########################
#########################
#########################

# print("Lemmatising ...")
# # LEMMATISE
# lemmatizer = WordNetLemmatizer()
# # convert tags to lemmatizer tagset
# # see https://www.machinelearningplus.com/nlp/lemmatization-examples-python/
# tagToWN = {"J": wordnet.ADJ,
# 		"N": wordnet.NOUN,
# 		"V": wordnet.VERB,
# 		"R": wordnet.ADV}
# 
# def lemm(txt):
# 	# part of speech tagging
# 	pos = pos_tag(txt)
# 	lemm = []
# 	for word,tag in pos:
# 		if len(word)>0:
# 			if tag[0] in tagToWN:
# 				lemm.append(lemmatizer.lemmatize(word,tagToWN[tag[0]]))
# 			else:
# 				lemm.append(lemmatizer.lemmatize(word))
# 	return(lemm)