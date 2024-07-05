import json,pathlib
from bs4 import BeautifulSoup
import collections

f = open("data.json")
d = json.load(f)


def getLinesWithNoSpeaker(lines):
	for line in lines:
		if "CHOICE" in line:
			for x in getLinesWithNoSpeaker(line["CHOICE"]):
				yield x
		else:
			charName = [x for x in line if not x.startswith("_")][0]
			if len(charName) == 36:
				yield (charName,line[charName])

# The idea is to use the mapping
#   (other source) charName -> dialogue <- charID (data.json)
# But some characters have identical lines of dialogue
# so we'll need to keep track of all characters who share a line.


# Build mapping from data.json between dialogue -> list of charNames
# dialogueToCharID = {}
# for charID,dialogue in getLinesWithNoSpeaker(d["text"]):
# 	if len(dialouge)>1:
# 		if dialogue in dialogueToCharID:
# 			dialogueToCharID[dialogue] += [charID]
# 		else:
# 			dialogueToCharID[dialogue] = [charID]

charIDToDialogue = {}
for charID,dialogue in getLinesWithNoSpeaker(d["text"]):
	if len(dialogue)>1:
		try:
			charIDToDialogue[charID].append(dialogue)
		except:
			charIDToDialogue[charID] = [dialogue]



px = pathlib.Path("/Users/seanroberts/Downloads/BG3 - parsed dialogue (1.6)/Dialogs/")
fileNamesToProcess = [str(x) for x in px.rglob("*.html")]

#fileNamesToProcess = [x for x in fileNamesToProcess if x.endswith("LOW_BlushingMermaid_Patron_01_Patron_09_Debate.html")]

# build mapping from dialogue to charName
dialogueToCharName = {}
for file in fileNamesToProcess:
	xml = open(file,'r', encoding = 'utf8')
	soup = BeautifulSoup(xml, "lxml")
	dialogues = soup.find_all("span",{"class":"dialog"})
	for dx in dialogues:
		dialogue = dx.get_text().strip()
		charName = dx.find_previous_sibling("div")
		if not charName is None:			
			charName = charName.get_text().strip()
			if dialogue in dialogueToCharName:
				dialogueToCharName[dialogue] += [charName]
			else:
				dialogueToCharName[dialogue] = [charName]				


# Now reconcile the two mappings, looking at frequency when it's ambiguous.
# TODO: We're counting charNames wrong, I think.
# e.g. 'd738c9a4-a031-4dd9-912f-93cda8d8d8b7' should be clearly resolvable?
# There's one line that's introducing some ambiguity: "For the Absolute!"
charIDToCharName = {}
for charID in charIDToDialogue:
	dialogues = charIDToDialogue[charID]
	
	allCharNames = [] # all speakers of all dialogues
	uniqueSpeakers = [] # all speakers who uniquely say a line
	for dx in dialogues:
		if dx in dialogueToCharName:
			speakersOfDx = list(set(dialogueToCharName[dx]))
			allCharNames += speakersOfDx
			if len(speakersOfDx)==1:
				uniqueSpeakers.append(speakersOfDx[0])
			
	onlyOneAssociatedCharName = len(list(set(allCharNames))) == 1
	uniqueLineIdentifiesCharName = len(list(set(uniqueSpeakers))) == 1
	
	if onlyOneAssociatedCharName:
		charIDToCharName[charID] = allCharNames[0]
	elif uniqueLineIdentifiesCharName:
		charIDToCharName[charID] = uniqueSpeakers[0]
	else:
	
		# List of all characters who said each line
		# for each line, a character receives the proportion of 
		# lines attributed to them. Find the character
		# with the best representation
		charNames = {}
		numDialogues = 0
		for dx in dialogues:
			if dx in dialogueToCharName:
				numDialogues += 1
				names = dialogueToCharName[dx]
				for name in list(set(names)):
					prop = names.count(name)/len(names)
					try:
						charNames[name] += prop
					except:
						charNames[name] = prop
	
		# normalise so max is 1.0
		for name in charNames:
			charNames[name] = charNames[name]/numDialogues
	
		if len(charNames)>0:
			mostFreq = max(charNames, key=charNames.get)
			mostFreqProp = charNames[mostFreq]
			if mostFreqProp > 0.9:
				# go with most frequent
				charIDToCharName[charID] = mostFreq
			else:
				# Not sure. We could whittle this further, but 
				#  probably easier to do manually.
				# Sort in frequency at least
				xx = sorted([(charNames[name],name) for name in charNames if charNames[name] > 0.05],reverse=True)
				xx2 = [x[1] for x in xx]
				charIDToCharName[charID] = "/ ".join(xx2)


out = "{\n"
sortedPairs = sorted([(charIDToCharName[idx],idx) for idx in charIDToCharName])
for name,idx in sortedPairs:
	out += '\t"' + idx + '": "' + name + '"\n'
out += "\n}"
					
with open('extraCharNames.json', 'w', encoding='utf-8') as f:
	f.write(out)