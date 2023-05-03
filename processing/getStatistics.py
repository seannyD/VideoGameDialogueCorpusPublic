# Calculate and compile all statistics
#  Stats files are written to the data folder for each game
#  You can also re-compile stats for just one game e.g.
#  > python3 getStatistics.py ../data/FinalFantasy/FFVII


print("LOADING LIBRARIES ...")
import os, json, re, csv, sys
import parsers
from textatistic import Textatistic,word_count,sent_count

# TODO: Load more accurate parser
# spacy.load('en_core_web_trf')
from pprint import pformat
from corpusHelpers import *

# binom_test is deprecated, and having trouble with scipy install,
#  so mute for now
#from scipy.stats import binom_test

import string
#from nltk.tokenize import word_tokenize
#from nltk.corpus import stopwords
#from nltk import sent_tokenize
#from textatistic import Textatistic


# def countWords(text):
# 	# Tokenise
# 	tokens = word_tokenize(text)
# 	# convert to lower case
# 	tokens = [w.lower() for w in tokens]
# 	# remove punctuation from each word
# 	table = str.maketrans('', '', string.punctuation)
# 	stripped = [w.translate(table) for w in tokens]
# 	# remove remaining tokens that are not alphabetic
# 	words = [word for word in stripped if word.isalpha()]
# 	# filter out stop words
# 	#stop_words = set(stopwords.words('english'))
# 	#words = [w for w in words if not w in stop_words]
# 	return(len(words))


def getStats(texts):
	# texts is a list of strings
	# Get rid of text within parentheses
	texts = [re.sub("\(.*?\)"," ",x) for x in texts]
	# Filter
	texts = [x for x in texts if len(x.strip()) > 0]
	
	nLines = len(texts)
	out = [nLines,"NA","NA","NA","NA","NA","NA"]
	
	# Join texts for faster processing
	joinedTexts = cleanText(". ".join(texts)).strip()
	if len(joinedTexts)>0:
		# Check joined texts have alphabetic characters
		#  (e.g. sometimes characters just have exclamation points)
		if re.search('[a-zA-Z]', joinedTexts):
			# Make sure there's at least one sentence delimiter.
			if not re.search('[\\.!?]', joinedTexts):
				joinedTexts += "."
			tStats = Textatistic(joinedTexts)
			numOfWords = tStats.word_count
			out = [nLines,numOfWords,tStats.sent_count,tStats.sybl_count,tStats.fleschkincaid_score,tStats.flesch_score,tStats.dalechall_score]
	return(out)

#columnHeaders = ["game","series","group",'lines',"words","sentences"]
columnHeaders = ["folder","alternativeMeasure","game","series","group",'lines',"words","sentences",'syllables','FleschKincaidReadability',"FleschReadability","DaleChallReadability","numCharacters"]


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

for folder in foldersToProcess:
	print("PROCESSING "+folder+ " ...")
	
	if not (os.path.isfile(folder+"meta.json") and os.path.isfile(folder+"data.json")):
		print("##########")
		print("JSON files not found")
		continue

	with open(folder+"meta.json") as json_file:
		meta = json.load(json_file)
	with open(folder+"data.json") as json_file:
		d = json.load(json_file)["text"]

	# Print list of all characters
	# with frequency
	allKeys = {}
	for k in get_keys_recursively(d):
		try:
			allKeys[k] += 1
		except:
			allKeys[k] = 1
	listOfCharactersForWriting = ",\n".join(reversed(['"'+k + '" '+ ":" + str(allKeys[k]) for k in sorted(allKeys, key=allKeys.get)]))
	with open(folder+"characters.txt",'w') as f:
		f.write(listOfCharactersForWriting)
	# Check all characters have been coded
	codedCharacters = sum([v for k,v in meta["characterGroups"].items()],[]) # Sum flattens list
	nonCodedCharacters = sorted([x for x in allKeys.keys() if not x in codedCharacters and not x in ["ACTION","CHOICE","LOCATION","COMMENT","STATUS","SYSTEM","GOTO","NARRATIVE"]])
	chkf = "\n".join(['"' + x + '",' for x in nonCodedCharacters])[:-1]
	if len(nonCodedCharacters)>0:
		print("No coding for: \n"+ chkf)
	with open(folder+"nonCodedCharacters.txt",'w') as f:
		f.write(chkf)
	
	# Check if "CHOICE" is coded as a character (can cause problems)
	if "CHOICE" in codedCharacters:
		print("\n\n-------\nWARNING:\n-------\n'CHOICE' should not be coded as a character.")
	
	alternativeMeasure = False
	if "alternativeMeasure" in meta:
		alternativeMeasure = meta["alternativeMeasure"]			
	
	seriesName = "NA"
	if meta["series"]:
		seriesName = meta["series"]

	
	############	
	#  Stats per character
	#  (do this first so we know how many characters we have)
	outChar = [["folder","alternativeMeasure","game","series","group","charName",'lines',"words","sentences","syllables"]]

	# Get list of characters first (in case characters appear two times within a group)
	groupsAndChars = []
	for groupName,characters in meta["characterGroups"].items():
		for character in characters:
			if not [groupName,character] in groupsAndChars:
				groupsAndChars.append([groupName,character])
			else:
				print("  WARNING: char twice within a group: "+ character + "/ "+groupName)
	
	charCountByGroup = {}
	for groupName,character in groupsAndChars:
		texts = [x for x in getTextByCharacters(d,[character]) if len(x.strip())>0]
		if len(texts)>0:
			sx = getStats(texts)
			lines = sx[0]
			words = sx[1]
			sentences = sx[2]
			syllables = sx[3]
			outChar.append([folder,alternativeMeasure, meta["game"], seriesName, groupName,character,lines,words,sentences,syllables])			
			if not groupName in charCountByGroup:
				charCountByGroup[groupName] = 1
			else:
				charCountByGroup[groupName] += 1
	
	out = []
	out.append(columnHeaders)
	######################
	# Total Dialogue
	charNamesAndDialogue = [x for x in getAllCharacterTexts(d,getNames=True)]
	totalNumChars = len(set([charName for charName,dialogue in charNamesAndDialogue if len(dialogue)>0]))
	texts = [dialogue for charName,dialogue in charNamesAndDialogue if len(dialogue)>0]
	stats = getStats(texts)


	out.append([folder, alternativeMeasure, meta["game"],seriesName, "TOTAL"] + stats + [totalNumChars])

	########################
	# Dialogue by Groups
	for groupName,characters in meta["characterGroups"].items():
		texts = [x for x in getTextByCharacters(d,characters) if len(x)>0]
		stats = getStats(texts)
		# csv handles escaping quotes etc.
		cc = 0
		if groupName in charCountByGroup:
			cc = charCountByGroup[groupName]
		out.append([folder,alternativeMeasure,meta["game"],seriesName, groupName] + stats + [cc])

	with open(folder+"stats.csv", "w") as f:
		writer = csv.writer(f)
		writer.writerows(out)
	
				
	with open(folder+"stats_by_character.csv", "w") as f:
		writer = csv.writer(f)
		writer.writerows(outChar)
		
	
	
# Collect all data and write to single file
#  Also, get some overall stats and output to latex for the paper
# (for all folders)

def getInfoFromRow(row,prop,default=0):
	ix = columnHeaders.index(prop)
	if ix>=0 and ix<len(row):
		x = row[columnHeaders.index(prop)]
		if x == "NA":
			return(default)
		if x in ["True","False"]:
			return(x=="True")
		return(int(x))
	return(default)

groupWordTotals = {}
groupLinesTotals = {}
groupNumCharTotals = {}		

allData = [columnHeaders]
for folder in allFolders:
	csvFileLoc = folder + 'stats.csv'
	if os.path.exists(csvFileLoc):
		dat = {}
		with open(csvFileLoc,'r') as csvfile:
			csvreader = csv.reader(csvfile)
			for row in csvreader:
				if not row[0]==columnHeaders[0]:
					allData.append(row)
					# Read data for latex stats
					groupName = row[columnHeaders.index("group")]
					groupWords = getInfoFromRow(row,"words")
					groupLines = getInfoFromRow(row,"lines")
					groupChars = getInfoFromRow(row,"numCharacters")
					dat[groupName] = {"words":groupWords,"lines":groupLines,"numCharacters":groupChars}
					alternativeMeasure = getInfoFromRow(row,"alternativeMeasure")
		# Add stats to totals
		if not alternativeMeasure:
			for groupName in dat:
				if not groupName in groupWordTotals:
					groupWordTotals[groupName] = 0
					groupLinesTotals[groupName] = 0
					groupNumCharTotals[groupName] = 0
				groupWordTotals[groupName] += dat[groupName]["words"]
				groupLinesTotals[groupName] += dat[groupName]["lines"]
				groupNumCharTotals[groupName] += dat[groupName]["numCharacters"]

with open("../results/generalStats.csv", "w") as f:
	writer = csv.writer(f)
	writer.writerows(allData)
	
##############
# Write various stats to latex for the main paper

# Overall stats
totalNumCharacters = groupNumCharTotals["TOTAL"]
totalDialogueWords = groupWordTotals["TOTAL"]

numMaleCharacters = groupNumCharTotals["male"]
numFemaleCharacters = groupNumCharTotals["female"]
numMaleAndFemaleCharacters = numMaleCharacters + numFemaleCharacters
propFemaleCharacters = numFemaleCharacters / numMaleAndFemaleCharacters
propFemaleCharacters = round(100* propFemaleCharacters,2)

propMaleCharacters = numMaleCharacters / numMaleAndFemaleCharacters
propMaleCharacters = round(100* propMaleCharacters,2)

numNeutralCharacters = groupNumCharTotals["neutral"]
propNeutralCharacters = numNeutralCharacters / (numNeutralCharacters + numMaleAndFemaleCharacters)
propNeutralCharacters = round(100* propNeutralCharacters,2)


## This used to run the binomial test on the number of characters
##  but the scipy library was causing trouble, so muted for now
#bt_p = binom_test(numFemaleCharacters,numMaleAndFemaleCharacters,alternative='two-sided')
#if bt_p < 0.0001:
#	bt_p = "< 0.0001"
#else:
#	bt_p = "= " + str(round(bt_p,3))
#propFemaleCharBinomTest = "p$" +  str(bt_p) + "$"
#with open("../results/latexStats/propFemaleCharBinomTest.tex",'w') as o:
#	o.write(propFemaleCharBinomTest)

totalMaleWords = groupWordTotals["male"]
totalFemaleWords = groupWordTotals["female"]
print(groupWordTotals)
totalMaleAndFemaleWords = totalMaleWords+totalFemaleWords
propFemaleWords = totalFemaleWords / totalMaleAndFemaleWords
propFemaleWords = round(100* propFemaleWords,2)

totalMaleLines = groupLinesTotals["male"]
totalFemaleLines = groupLinesTotals["female"]
totalMaleAndFemaleLines = totalMaleLines+totalFemaleLines
propFemaleLines = totalFemaleLines / totalMaleAndFemaleLines
propFemaleLines = round(100* propFemaleLines,2)


with open("../results/latexStats/totalNumCharacters.tex",'w') as o:
	o.write(f'{totalNumCharacters:,}')
with open("../results/latexStats/numMaleCharacters.tex",'w') as o:
	o.write(f'{numMaleCharacters:,}')
with open("../results/latexStats/numFemaleCharacters.tex",'w') as o:
	o.write(f'{numFemaleCharacters:,}')
with open("../results/latexStats/numMaleAndFemaleCharacters.tex",'w') as o:
	o.write(f'{numMaleAndFemaleCharacters:,}')
with open("../results/latexStats/propFemaleCharacters.tex",'w') as o:
	o.write(str(propFemaleCharacters))	
with open("../results/latexStats/propMaleCharacters.tex",'w') as o:
	o.write(str(propMaleCharacters))
	
with open("../results/latexStats/numNeutralCharacters.tex",'w') as o:
	o.write(str(numNeutralCharacters))
with open("../results/latexStats/propNeutralCharacters.tex",'w') as o:
	o.write(str(propNeutralCharacters))
	

with open("../results/latexStats/totalDialogueWords.tex",'w') as o:
	o.write(f'{totalDialogueWords:,}')
with open("../results/latexStats/totalMaleWords.tex",'w') as o:
	o.write(f'{totalMaleWords:,}')
with open("../results/latexStats/totalFemaleWords.tex",'w') as o:
	o.write(f'{totalFemaleWords:,}')
with open("../results/latexStats/totalMaleAndFemaleWords.tex",'w') as o:
	o.write(f'{totalMaleAndFemaleWords:,}')
with open("../results/latexStats/propFemaleWords.tex",'w') as o:
	o.write(str(propFemaleWords))
	
with open("../results/latexStats/totalMaleLines.tex",'w') as o:
	o.write(f'{totalMaleLines:,}')
with open("../results/latexStats/totalFemaleLines.tex",'w') as o:
	o.write(f'{totalFemaleLines:,}')
with open("../results/latexStats/totalMaleAndFemaleLines.tex",'w') as o:
	o.write(f'{totalMaleAndFemaleLines:,}')
with open("../results/latexStats/propFemaleLines.tex",'w') as o:
	o.write(str(propFemaleLines))


#########
# Check status (e.g. non-coded characters)
# and make centralised table
noSymbol = " :x: "
yesSymbol = " :ok: "
readySymbol = ":white_check_mark:"
supersededSymbol = ":arrow_down:"
inProgressSymbol = ":parking:"

codingStatus = "# Data \n\n Each folder is for a video game series, with sub-folders for each game. \n\nNote that some games have multiple folders with alternative sources. Only some of these are included in the final data for the main analysis. \n\n # Coding Status\n\n"+readySymbol+" = Data has passed checks and is ready to use.\n\n"+inProgressSymbol+" = Parser is in progress.\n\n"+supersededSymbol+" = Abandoned, has been superseded by a newer source.\n\n| Folder | Status |  All Char Coded | Data older than parser | Data older than meta | Stats older than data | Main char | Source Feat. |\n| --- | --- | --- | --- | --- | --- | --- | --- |\n"
allFolders.sort()
for folder in allFolders:
	with open(folder+"meta.json") as json_file:
		meta = json.load(json_file)		
	altMeasure = False
	if "alternativeMeasure" in meta:
		altMeasure = meta["alternativeMeasure"]
	devStatus = inProgressSymbol
	if "status" in meta:
		if meta["status"] == "superseded":
			devStatus = supersededSymbol
		if meta["status"] == "ready":
			devStatus = readySymbol
	
	# List for all sources
	if not any([folder.startswith(x) for x in ["../data/Test","../data/Bar"]]):
		parserName = "XXX"
		if "parserParameters" in meta:
			if "parser" in meta["parserParameters"]:
				parserName = meta["parserParameters"]["parser"]
		codingStatus += "| " + folder[8:] + " | " + devStatus + " | "
		codingFileLoc = folder + 'nonCodedCharacters.txt'
		if os.path.exists(codingFileLoc):
			with open(codingFileLoc,'r') as codingFile:
				codingFileContents = codingFile.read().strip()
				codingFileContents = codingFileContents.replace('"',"")
				if len(codingFileContents) >0:
					codingStatus += noSymbol+ "|"
				else:
					codingStatus += yesSymbol + "|"
		else:
			codingStatus += noSymbol+ "|"

		# Check parsing is up to date
		dataFileLoc = folder + 'data.json'
		parserFileLoc = 'parsers/'+parserName + ".py"
		if os.path.exists(dataFileLoc) and os.path.exists(parserFileLoc):
			dataModDate = os.path.getmtime(dataFileLoc)
			parserModDate = os.path.getmtime(parserFileLoc)
			if dataModDate > parserModDate:
				codingStatus += yesSymbol + "|"
			else:
				print('   echo "Parser needs re-run"\n   python3 parseRawData.py '+folder)
				codingStatus += noSymbol + "|"
		else:
			codingStatus += noSymbol + "|"
			
		# Check data is older than meta
		metaFileLoc = folder+"meta.json"
		if os.path.exists(dataFileLoc) and os.path.exists(metaFileLoc):
			dataModDate = os.path.getmtime(dataFileLoc)
			metaModDate = os.path.getmtime(parserFileLoc)
			if dataModDate > metaModDate:
				codingStatus += yesSymbol + "|"
			else:
				print('   echo "Parser needs re-run"\n   python3 parseRawData.py '+folder)
				codingStatus += noSymbol + "|"
		else:
			codingStatus += noSymbol + "|"
		

		# Check stats are up to date
		statsFileLoc = folder + 'stats.csv'	
		if os.path.exists(dataFileLoc) and os.path.exists(statsFileLoc):
			dataModDate = os.path.getmtime(dataFileLoc)
			statsModDate = os.path.getmtime(statsFileLoc)
			if statsModDate > dataModDate:
				codingStatus += yesSymbol + "|"
			else:
				print('   echo "Stats needs re-run";\n   python3 getStatistics.py '+folder+";")
				codingStatus += noSymbol + "|"
		else:
			codingStatus += noSymbol + "|"
			
		if "mainPlayerCharacters" in meta:
			if len([x for x in meta["mainPlayerCharacters"] if len(x)>0])>0:
				codingStatus += yesSymbol + "|"
			else:
				codingStatus += noSymbol + "|"
		else:
			codingStatus += noSymbol + "|"

		if "sourceFeatures" in meta:
			codingStatus += yesSymbol + "|"
		else:
			codingStatus += noSymbol + "|"
			
		codingStatus += "\n"
	
with open("../data/README.md", "w") as f:
	f.write(codingStatus)
	