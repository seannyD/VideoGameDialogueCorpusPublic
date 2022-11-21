import csv, json

with open("data.json") as json_file:
	d = json.load(json_file)
lines = d["text"]

with open("meta.json") as json_file:
	m = json.load(json_file)
groups = m["characterGroups"]

def findGroup(charName):
	for g in groups:
		if charName in groups[g]:
			return(g)
	return("neutral")

csvData = [["CharName","CharGender","EnglishDialogue","JapaneseCharName","JapaneseDialogue","Scenario","URL"]]
loc = ""
scen = ""
for line in lines:
	k = [x for x in line if not x.startswith("_")][0]
	dlg = line[k]
	if k == "ACTION" or k == "SYSTEM":
		pass
	elif k== "LOCATION":
		if line[k].startswith("http"):
			loc = line[k]
		else:
			scen = line[k]
	else:
		jChar = ""
		jDlg = ""
		if "_JChar" in line:
			jChar = line["_JChar"]
		if "_JText" in line:
			jDlg = line["_JText"]
		#print("SSS"+scen)
		
		group = findGroup(k)
		
		csvData.append([k,group, dlg,jChar,jDlg,scen,loc])
		
		
   
with open('data.csv', 'w', encoding='UTF8') as f:
	writer = csv.writer(f)
	writer.writerows(csvData)
