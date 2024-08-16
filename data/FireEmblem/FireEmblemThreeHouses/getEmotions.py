import json,csv
data = json.load(open("data.json"))["text"]

emotions = {}

def walkData(lines):
	global emotions
	out = []
	for line in lines:
		if "CHOICE" in line:
			for choice in line["CHOICE"]:
				walkData(choice)
		else:
			if "_emot" in line:
				charName = [x for x in line if not x.startswith("_")][0]
				if not charName in emotions:
					emotions[charName] = {}
				try:
					emotions[charName][line["_emot"]] += 1
				except:
					emotions[charName][line["_emot"]] = 1
					
walkData(data)

meta = json.load(open("meta.json"))
gender2char = meta["characterGroups"]
char2gender = {}
for group in gender2char:
	for char in gender2char[group]:
		char2gender[char] = group

out = [["charName","gender","emotion","frequency"]]
for charName in emotions:
	gender = ""
	if charName in char2gender:
		gender = char2gender[charName]
	for emotion in emotions[charName]:
		out.append([charName,gender,emotion,str(emotions[charName][emotion])])

with open('characterEmotions.csv', 'w') as csvfile:
	csvwriter = csv.writer(csvfile)
	csvwriter.writerows(out)