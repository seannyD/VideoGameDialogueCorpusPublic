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

def countWords(line):
	charKey = [k for k in line if not k.startswith("_")][0]
	if charKey in ["ACTION","CHOICE","LOCATION","COMMENT","STATUS","SYSTEM"]:
		return(0)
	dialogueText = line[charKey]
	# this function defined in corpusHelpers
	dialogueText = cleanText(dialogueText)
	if len(dialogueText)>0:
		#tStats = Textatistic(line[charKey])
		prepped_text = punct_clean(dialogueText)
		word_list = word_array(prepped_text, prepped=True)
		wordCount = word_count(word_list, prepped=True)
		return(wordCount)
	return(0)
	
def getCategory(line, nameToGroup):
	charKey = getCharKey(line)
	if charKey in nameToGroup:
		return(nameToGroup[charKey])
	return(None)

def getCharKey(line):
	return([k for k in line if not k.startswith("_")][0])

def getSumDiff(sum):
	maleDialogue = 0
	if "male" in sum:
		maleDialogue = sum["male"]
	femaleDialogue = 0
	if "female" in sum:
		femaleDialogue = sum["female"]
	# absolute difference
	return(maleDialogue - femaleDialogue)
	# proportional difference
#	tot =  femaleDialogue + maleDialogue
#	if tot==0:
#		return(0)
#	return(maleDialogue / tot)

def countDialogueOnly(lines,nameToGroup):
	sum = {}
	dialogues = [line for line in lines if not getCharKey(line) in ["ACTION","CHOICE","LOCATION","COMMENT","STATUS","SYSTEM"]]
	for dialogue in dialogues:
		cat = getCategory(dialogue,nameToGroup)
		if not cat is None:
			numWords = countWords(dialogue)
			if cat in sum:	
				sum[copy.deepcopy(cat)] += numWords
			else:
				sum[copy.deepcopy(cat)] = numWords
	return(sum)

def walkLinesRandom(lines,nameToGroup,sums=[{}]):
	# Count all normal dialogues (order doesn't matter)
	# and add to all parallel sums
#	print("-----")
#	print(lines)
	dialogues = [line for line in lines if not getCharKey(line) in ["ACTION","CHOICE","LOCATION","COMMENT","STATUS","SYSTEM"]]
	for dialogue in dialogues:
		cat = getCategory(dialogue,nameToGroup)
		if not cat is None:
			numWords = countWords(dialogue)
			if cat in sums[0]:	
				sums[0][copy.deepcopy(cat)] += numWords
			else:
				sums[0][copy.deepcopy(cat)] = numWords
	choices = [line for line in lines if getCharKey(line)=="CHOICE"]
	if len(choices)==0:
		return(copy.deepcopy(sums))
	# Deal with choices
	# For each dialogue tree
	for choiceObject in choices:	
		# Choose a random branch
		nChoices = len(choiceObject["CHOICE"])
#		print("=====")
#		print(choiceObject["CHOICE"])
		if nChoices > 0:
			if nChoices == 1:
				choice = choiceObject["CHOICE"][0]
			else:
				choice = choiceObject["CHOICE"][random.randint(0,(nChoices-1))]
			sums = walkLinesRandom(choice,nameToGroup,copy.deepcopy(sums))
	# If we return everything, the number of options grows too quickly
	return(copy.deepcopy(sums))
	
def walkLines(lines,nameToGroup,sums=[{}]):
	# Count all normal dialogues (order doesn't matter)
	# and add to all parallel sums
	dialogues = [line for line in lines if not getCharKey(line) in ["ACTION","CHOICE","LOCATION","COMMENT","STATUS","SYSTEM"]]
	for dialogue in dialogues:
		cat = getCategory(dialogue,nameToGroup)
		if not cat is None:
			numWords = countWords(dialogue)
			for sum in sums:
				if cat in sum:	
					sum[copy.deepcopy(cat)] += numWords
				else:
					sum[copy.deepcopy(cat)] = numWords
	choices = [line for line in lines if getCharKey(line)=="CHOICE"]
	if len(choices)==0:
		return(copy.deepcopy(sums))
	# Deal with choices
	
	# For each branch in sums:
		# Add results of walkLines to the branch
	for choiceObject in choices:	
		newSums = []	
		for choice in choiceObject["CHOICE"]:
			if len(choice)>0:
				newSums += walkLines(choice,nameToGroup,copy.deepcopy(sums))
			# If there are no dialogues in the choice,
			#  (e.g. because the other alt is optional)
			# then we still need to record this branch
			#  in case it minimises dialogue for one gender.
			else:
				newSums.append({"male":0,"female":0})
		sums = copy.deepcopy(newSums)
	
	# If we return everything, the number of options grows too quickly
	sums = sorted(sums,key=getSumDiff)
	s0 = {}
	s1 = {}
	if len(sums)>0:
		s0 = sums[0]
		s1 = sums[-1]
	return(copy.deepcopy([s0,s1]))



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

for folder in foldersToProcess:
	print("PROCESSING "+folder+ " ...")
	
	if not (os.path.isfile(folder+"meta.json") and os.path.isfile(folder+"data.json")):
		print("##########")
		print("JSON files not found")
		# For safety, remove the file
		if(os.path.isfile(folder+"choiceVariation.csv")):
			os.remove(folder+"choiceVariation.csv")
		continue
	with open(folder+"meta.json") as json_file:
		meta = json.load(json_file)
	with open(folder+"data.json") as json_file:
		d = json.load(json_file)["text"]
	
	
# 	d = [
# 		{"1": "one"},
# 		{"CHOICE":[
# 			[
# 				{"2a":"one"},
# 				{"CHOICE": [
# 					[{"2aa": "one two"}],
# 					[{"2ab": "one"}]
# 				]}
# 			],
# 			[	
# 				{"2b": "one two"}
# 			]
# 		]},
# 		{"CHOICE":[
# 			[{"3a": "extra extra extra"}],
# 			[{"3b": "extra"}]
# 		]}
# 	]
# 	meta["characterGroups"] = {"1":["1"],"2a":["2a"],"2b":["2b"],"2aa":["2aa"],"2ab":["2ab"],"3a":["3a"],"3b":["3b"]}
# 	
	
	if True:	
#	try:
		nameToGroup = getNameToGroup(meta)

		allChoices = [x for x in d if "CHOICE" in x]
	
		# Script has no choices
		if len(allChoices)==0:
			if(os.path.isfile(folder+"choiceVariation.csv")):
				os.remove(folder+"choiceVariation.csv")
		else:
			# Non-choice dialogue
			nd = [copy.deepcopy(x) for x in d if not "CHOICE" in x]
			nonChoiceDialogue = countDialogueOnly(nd,nameToGroup)
			if not "male" in nonChoiceDialogue:
				nonChoiceDialogue["male"] = 0
			if not "female" in nonChoiceDialogue:
				nonChoiceDialogue["female"] = 0
		
			# Choice dialogue - random
			randomChoiceSums = []
			for i in range(100):
				rdist = walkLinesRandom(allChoices,nameToGroup)[0]
				if not "male" in rdist:
					rdist["male"] = 0
				if not "female" in rdist:
					rdist["female"] = 0
				randomChoiceSums.append(rdist)

			outRand = [["maleWords","femaleWords"]]
			for ranChoiceSum in randomChoiceSums:
				outRand.append([ranChoiceSum["male"], ranChoiceSum["female"]])
			with open(folder+"stats_randomChoices.csv", "w") as f:
				writer = csv.writer(f)
				writer.writerows(outRand)

			# Choice dialogue - limits
			results = []
			for choiceObject in allChoices:
				wl = walkLines([choiceObject],nameToGroup)
				results.append(wl)

			# Write results
			out = [["folder","maxF.maleWords","maxF.femaleWords","maxM.maleWords","maxM.femaleWords","totalNonChoice.maleWords","totalNonChoice.femaleWords"]]
			out.append([folder,"NA","NA","NA","NA",nonChoiceDialogue["male"],nonChoiceDialogue["female"]])
		
			for res in results:
				maxF = copy.deepcopy(res[0])
				maxM = copy.deepcopy(res[1])
	
				if not "male" in maxF:
					maxF["male"] = 0
				if not "female" in maxF:
					maxF["female"] = 0
		
				if not "male" in maxM:
					maxM["male"] = 0
				if not "female" in maxM:
					maxM["female"] = 0
		
				out.append([folder,maxF["male"],maxF["female"],maxM["male"],maxM["female"],"NA","NA"])
			#print(nonChoiceDialogue)
			with open(folder+"choiceVariation.csv", "w") as f:
				writer = csv.writer(f)
				writer.writerows(out)
				print("      DONE")
	else:
#	except:
		print("\n\nERROR\n\n")
		if(os.path.isfile(folder+"choiceVariation.csv")):
			os.remove(folder+"choiceVariation.csv")
