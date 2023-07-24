import os,json,re

names = {
'reg':"Reagan",	
'tia':"Tia",	
'tod':"Todd",	
'can':"Candy",	
'nei':"Neil",	
'bae':"Mrs. Baez",	
'tut':"Tutorial",	
'kev':"Kevin",	
'cou':"Courtney",	
'mil':"Milo",	
'dew':"Miss Dewey",	
'fer':"Mr. Fermat",	
'bar':"Barbie",	
'daw':"Dawn",	
'pat':"Coach Paternal",	
'col':"Cole",	
'raq': "Raquelle"
}

def writeData(out,folder):
	json_data = json.dumps({"text":out}, indent="\t",ensure_ascii=False)
	# make a bit more compact
	json_data = re.sub('{\n\t+','{',json_data)
	json_data = re.sub('\n\t+}','}',json_data)
#		json_data = re.sub('\[\n\t+','[',json_data)
	json_data = re.sub('\n\t+]',']',json_data)
	# Non-dialogue info should not have its own line
	json_data = re.sub('",\n\t+"_','", "_',json_data)
	o = open(folder+"data.json",'w')
	o.write(json_data)
	o.close()
	
	
fixes = [
	("No anything special about coach paternal","Know anything special about coach paternal"),
	("Mrs. bias","Mrs. Baez"),
	("Báez","Baez"),
	("is his bias was away","Mrs. Baez was away"),
	("aloe you want","I'll owe you one"),
	("The woman eats everything","The woman knits everything"),
	("iCloud","a cloud"),
	("cockroach","clockroach"),
	("smell like copter","smell-a-copter"),
	("coach paternal","Coach Paternal"),
	("Meadows","Mayos"),
	("Mr. Fairmont","Mr. Fermat"),
	("firma","Fermat"),
	("Furman","Fermat"),
	("Mr. we really","Miss Dewey really")
]

scratchDir = "/Users/seanroberts/Documents/BarbieDiaries/scratch/"

txtFiles = [x for x in os.listdir(scratchDir) if x.endswith(".txt")]
txtFiles = sorted(txtFiles)
out = []

for file in txtFiles:
	tx = open(scratchDir+file).read()
	for orig,fix in fixes:
		tx = tx.replace(orig,fix)
	charID,lineID = file.split("_",1)
	charName = names[charID]
	out.append({charName: tx.strip(), "_ID":lineID})

writeData(out,"raw/")
