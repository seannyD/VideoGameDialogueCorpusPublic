# For FFXIV, create a spreadsheet of quests, listing
#  the xp and gil, with the number of male and female words spoken

import json, csv, re
from textatistic import *

with open("data.json") as json_file:
	data = json.load(json_file)	

data = data["text"]

with open("meta.json") as json_file:
	meta = json.load(json_file)
	
g = meta["characterGroups"]


def getTextByCharacters(var,characterKeys):
	if isinstance(var,dict) or isinstance(var,list):
		for k in var:
			if isinstance(var, dict):
				v = var[k]
				if k in characterKeys:
					yield v
				for result in getTextByCharacters(v,characterKeys):
					yield result
			elif isinstance(var, list):
				for result in getTextByCharacters(k,characterKeys):
					yield result
					
def getStats(texts):
	# Get rid of text within parentheses
	texts = [re.sub("\(.*?\)"," ",x) for x in texts]
	texts = [x for x in texts if len(x.strip()) > 0]
	joinedTexts = ". ".join(texts)
	if len(joinedTexts.strip())>0:
		engPrep = textatistic.punct_clean(joinedTexts)
		engWordList = textatistic.word_array(engPrep, prepped=True)
		eng_word = textatistic.word_count(engWordList, prepped=True)
		return(eng_word)
	return(0)

def processQuestLines(lines,questDetails):
	femaleTexts = getTextByCharacters(lines,g["female"])
	femaleWords = getStats(femaleTexts)	
	maleTexts = getTextByCharacters(lines,g["male"])
	maleWords = getStats(maleTexts)
	
	def getProp(obj,key,default):
		if key in obj:
			return(str(obj[key]))
		return(default)
	
	lvl = getProp(questDetails,"_Level","")
	sce = getProp(questDetails,"_Scenario","")
	xp = getProp(questDetails,"_XP","NA")
	gil = getProp(questDetails,"_Gil","NA")
	
	return([questDetails["SYSTEM"],lvl,sce,xp,gil, femaleWords,maleWords])
 
# split into quests and process
out = [["QuestName","Level","Scenario","XP","Gil","femaleWords","maleWords"]]
questLines = []
questDetails = None
for line in data:
	if "_Level" in line:
		if not questDetails is None:
			out.append(processQuestLines(questLines,questDetails))
		questDetails = line
		questLines = []
	else:
		questLines.append(line)
# Leftover lines
if len(questLines)>0:
	out.append(processQuestLines(questLines,questDetails))
	
with open("XPByQuest.csv", 'w') as csvfile:
	csvwriter = csv.writer(csvfile)
	for row in out:
		csvwriter.writerow(row)



	