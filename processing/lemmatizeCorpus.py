# Running in python3.10
import os,json,csv
from tqdm import tqdm
from corpusHelpers import *
print("Loading spacy")
import spacy
nlp = spacy.load('en_core_web_sm')
print('Loaded')
from collections import Counter
import sqlite3

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


out = [["game","group","word","freq"]]
for folder in foldersToProcess:

	with open(folder+"meta.json") as json_file:
		meta = json.load(json_file)
	if meta["status"]=="ready":

		gameID = folder
		if gameID.endswith("/"):
			gameID= gameID[:-1]
		gameID = gameID[gameID.rindex("/")+1:].strip()
		gameName = meta["game"]
		print(gameName)

		# Make gender dict
		# TODO: what if in multiple groups?
		genderDict = {}
		charGroups = meta["characterGroups"]
		for group in charGroups:
			for char in meta["characterGroups"][group]:
				genderDict[char] = group


		# Get dialogue
		with open(folder+"data.json") as json_file:
			d = json.load(json_file)["text"]
	
		# Lemmatise dialogue
		print("  Lemmatising ...")
		charTexts = getAllCharacterTexts(d,getNames=True)
		genderTextsLemmaTokens = {}
		for group in charGroups:
			genderTextsLemmaTokens[group] = []
		ctx = [x for x in charTexts]
		for char,text in tqdm(ctx):
			if char in genderDict:
				genderTextsLemmaTokens[genderDict[char]] += lemmatiseText(text)
	
		for group in genderTextsLemmaTokens:
			#fullText = "\t"+"\t".join(genderTextsLemmaTokens[group])+"\t"
			freq = Counter(genderTextsLemmaTokens[group])
			for wd in freq:
				out.append([gameID,group,wd,freq[wd]])
		
		outfile = "../data/ALL/byCharGroup/Freq_"+gameID + ".csv"

		with open(outfile, "w") as csv_file:
			writer = csv.writer(csv_file)
			for row in out:
				writer.writerow([str(x) for x in row])