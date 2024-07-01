# Running in python3.10
import os,json,csv
from tqdm import tqdm
from corpusHelpers import *
print("Loading spacy")
import spacy
nlp = spacy.load('en_core_web_sm')
print('Loaded')

foldersToProcess = [root+os.sep for root,dirs,files in os.walk("../data/") if "meta.json" in files]


def lemmatiseText(text):
	# Lemmatise, replace proper names, take out punctuation
	doc = nlp(text)
	#lemmatized_tokens = [token.lemma_ for token in doc]
	lemmatized_tokens = []
	for token in doc:
		if token.pos_ == "PROPN":
			lemmatized_tokens.append("PROPN")
		elif token.pos_ == "PUNCT":
			pass
		else:
			lemmatized_tokens.append(token.lemma_)
	return(lemmatized_tokens)


# final frequency dictionary
# tropeWordFreq[tropeName][word] = wordFreq
tropeWordFreq = {}

for folder in foldersToProcess:
	tropeDataFile = folder+"tropeData.csv"
	if os.path.isfile(tropeDataFile):
		print(folder)
		with open(folder+"meta.json") as json_file:
			meta = json.load(json_file)
		game = meta["game"]

		# Make gender dict
		# TODO: what if in multiple groups?
		genderDict = {}
		for group in meta["characterGroups"]:
			for char in meta["characterGroups"][group]:
				genderDict[char] = group
				
		# Load trope data
		tropeHeader = []
		tropes = []
		with open(tropeDataFile, 'r') as file:
			reader = csv.reader(file)
			for row in reader:
				if len(tropeHeader)==0:
					tropeHeader = row
				else:
					tropes.append(dict(zip(tropeHeader,row)))
		# Make dictionary of trope to chars:
		trope2char = {}
		charsThatHaveTropes = []
		for tx in tropes:
			charName = tx["VGDCName"]
			if charName in genderDict:
				try:
					trope2char[tx["tropeName"]].append(charName)
				except:
					trope2char[tx["tropeName"]] = [charName]
				if not charName in charsThatHaveTropes:
					charsThatHaveTropes.append(charName)
				
		# Get dialogue
		with open(folder+"data.json") as json_file:
			d = json.load(json_file)["text"]
		
		# Lemmatise dialogue
		print("  Lemmatising ...")
		charTexts = getAllCharacterTexts(d,getNames=True)
		charTextsLemmaTokens = {}
		ctx = [x for x in charTexts]
		for char,text in tqdm(ctx):
			if char in charsThatHaveTropes:
				charTextsLemmaTokens[char] = lemmatiseText(text)
		
			
		# Add to frequency dictionaries
		# (might be more efficient to do one character at a time?)
		# ( and maybe only characters that actually appear in the trope data?)
		print("  Updating frequency dictionary ...")
		tropes = [x for x in trope2char]
		for trope in tqdm(tropes):
			if not trope in tropeWordFreq:
				tropeWordFreq[trope] = {}
			charsWithTrope = trope2char[trope]
			wordsWithTrope = []
			# get frequency for characters with the trope
			for char in charsWithTrope:
				if char in charTextsLemmaTokens:
					for lemma in charTextsLemmaTokens[char]:
						if not lemma in tropeWordFreq[trope]:
							tropeWordFreq[trope][lemma] = 0
						tropeWordFreq[trope][lemma] += 1
		
# Output
# Get all words for all tropes
# (this is a very inefficient format, because the matrix is very sparse)
allWords = {}
for trope in tropeWordFreq:
	for word in tropeWordFreq[trope]:
		allWords[word] = 0
allWords = [x for x in allWords.keys()]

# csv output, starting with row header
out = [[".TROPE"] + allWords]
for trope in tropeWordFreq:
	row = [trope]
	for word in allWords:
		if word in tropeWordFreq[trope]:
			row.append(tropeWordFreq[trope][word])
		else:
			row.append(0)
	out.append(row)

outfile = "../results/tropes/tropeWordFreq.csv"
	
with open(outfile, "w") as csv_file:
	writer = csv.writer(csv_file)
	for row in out:
		writer.writerow([str(x) for x in row])