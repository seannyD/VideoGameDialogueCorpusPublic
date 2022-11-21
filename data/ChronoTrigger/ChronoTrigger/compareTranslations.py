print("LOADING LIBRARIES ...")
import os, json, re, csv, sys
from textatistic import *
from pprint import pformat
import string

includeLinesInOutput = True


# Japanese tokeniser based on https://github.com/ikegami-yukino/rakutenma-python
# Initialize a RakutenMA instance with a pre-trained model
# rma = RakutenMA(phi=1024, c=0.007812)  # Specify hyperparameter for SCW (for demonstration purpose)
# rma.load("model_ja.json")
# rma.hash_func = rma.create_hash_func(15)
# 
# def countJapaneseWords(txt):
# 	tok = rma.tokenize("うらにわにはにわにわとりがいる")
# 	return(len(tok))
# 	

# Japanese rōmaji converter based on
#  https://pypi.org/project/pykakasi/
import pykakasi
kks = pykakasi.kakasi()

def countJapaneseLength(txt):
	txt = txt.replace("　"," ")
	romaji = kks.convert(txt)
	romajiWords = []
	for w in romaji:
		romajiWords += cleanRomaji(w['kunrei'])
	nChar_romaji = sum([len(x) for x in romajiWords])
	nChar_kana = sum([len(cleanKana(x['kana'])) for x in romaji])
	nWords = len(romajiWords)
	return((nChar_romaji,nChar_kana,nWords))

def cleanRomaji(t):
	#The output of pykakasi can return multiple words
	t = re.sub("[^a-z]+"," ",t)
	t = [x for x in t.split(" ") if len(x)>0]
	return(t)

def cleanKana(t):
	t = cleanText(t)
	t = t.replace("(","").replace(")","")
	return(t)

def cleanText(t):
	# remove stuff between brackets
	t = re.sub("\(.+?\)","",t)
	#
	# Clean for identifying sentence length
	t = re.sub("(\. *)+",". ",t)
	t = re.sub("!\.","!",t)
	t = re.sub("\?\.","?",t)
	t = re.sub(",\.",",",t)
	t = re.sub("([!\?])[!\?]+","\\1",t) # multiple exclamations
	t = t.replace("\.+",".")
	# Japanese encoded space:
	t = t.replace("　"," ")
	#
	for x in ["…","？","！","。","、","『","』","!"]:
		t = t.replace(x,"")
	t = t.strip()
	#
	return(t)

def findGender(charName,m):
	for g in m["characterGroups"]:
		if charName in m["characterGroups"][g]:
			return(g)
	return("none")

with open("data.json") as json_file:
	d = json.load(json_file)["text"]
	
with open("meta.json") as json_file:
	m = json.load(json_file)
	
def getStats(line, charName):
	gender = findGender(charName,m)
	
	engPrep = textatistic.punct_clean(cleanText(line[charName]))
	engWordList = textatistic.word_array(engPrep, prepped=True)
	eng_char = textatistic.char_count(engPrep, prepped=True)
	eng_syll = textatistic.sybl_counts(engWordList, prepped=True)['sybl_count']
	eng_word = textatistic.word_count(engWordList, prepped=True)
	
	rePrep = textatistic.punct_clean(cleanText(line["_Retranslate"]))
	reWordList = textatistic.word_array(rePrep, prepped=True)
	re_char = textatistic.char_count(rePrep, prepped=True)
	re_syll = textatistic.sybl_counts(reWordList, prepped=True)['sybl_count']
	re_word = textatistic.word_count(reWordList, prepped=True)

	jap_romaji,jap_kana,jap_words = countJapaneseLength(line["_Japanese"])
	jap =cleanText(line["_Japanese"])
	jap = re.sub("\s","",jap).strip()
	jap_char = len(jap)

	comm = ""
	comm_word = 0
	if "_TranslateComment" in line:
		comm = line["_TranslateComment"]
		commPrep = textatistic.punct_clean(cleanText(comm))
		commWordList = textatistic.word_array(commPrep, prepped=True)
		comm_word = textatistic.word_count(commWordList, prepped=True)
		comm = comm.replace("\n"," ")

	outBits = [charName,gender,
			eng_word,eng_syll,eng_char,
			jap_char,jap_romaji,jap_kana,jap_words,
			re_word,re_syll,re_char,
			comm_word]
	if includeLinesInOutput:
		outBits += [line[charName],line["_Japanese"],line["_Retranslate"]]
	outBits.append(comm)
	return(outBits)

def walkStructure(d):
	for line in d:
		charName = [x for x in line.keys() if not x.startswith("_")][0]
		if charName == "CHOICE":
			for choice in line["CHOICE"]:
				yield from walkStructure(choice)
		else:
			if all([x in line for x in ["_Japanese", "_Retranslate"]]):
				outBits = getStats(line, charName)
				yield [str(x) for x in outBits]

header = ["charName","gender",
			"eng_word","eng_syll","eng_char",
			"jap_char","jap_romaji","jap_kana","jap_word",
			"re_word","re_syll","re_char",
			"re_comment"]
if includeLinesInOutput:
	header += ["eng","jap","re","RetranslatorComment"]	

out = [x for x in walkStructure(d)]

	
with open('compareTranslations.csv', 'wt') as f:
	csv_writer = csv.writer(f, quoting=csv.QUOTE_ALL)
	csv_writer.writerow(header) # write header
	for row in out:
		csv_writer.writerow(row)