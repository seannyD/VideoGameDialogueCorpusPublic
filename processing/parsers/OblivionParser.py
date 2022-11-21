from bs4 import BeautifulSoup
import json


def parseFile(fileName,parameters={"characterClassIdentifier":"DAI"},asJSON=False):
		
	o = open(fileName,encoding="latin-1")
	d = o.read()
	o.close()

	rows = d.split("\n")
	columns = ["Name","Race","Group","Gender","CharacterCode","Quest","ID","X","FileID","File","Found","A","Dialogue","Emotion","Z","Q"]
	
	genderDict = {}
	
	out = []
	i = 1
	for row in rows:
		row = row.split("	")
		if(len(row)>=12):
			n = row[columns.index("Name")].strip()
			race = row[columns.index("Race")]
			group = row[columns.index("Group")]
			gender = row[columns.index("Gender")]
			dialogue = row[columns.index("Dialogue")]
			emotion = row[columns.index("Emotion")]
			quest = row[columns.index("ID")]
		
			if len(n)==0:
				n = "Generic "+race + " "+ gender
		
			try:
				genderDict[gender].append(n)
			except:
				genderDict[gender] = [n]
			
			if race!=group:
				out.append({
					n:dialogue,
					"_Race": race,
					"_Group": group,
					"_Emotion": emotion,
					"_Quest": quest
				})
			else:
				out.append({
					n:dialogue,
					"_Race": race,
					"_Emotion": emotion,
					"_Quest": quest
				})
								
	# Write gender information to a file to be imported to meta
	for k in genderDict:
		x = list(set(genderDict[k]))
		x.sort()
		genderDict[k] = x
		
	
	o = open(fileName[:fileName.rindex("/")]+"/../autoGender.json",'w')
	o.write(json.dumps(genderDict))
	o.close()

	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)
	


	


	

	

	
	



