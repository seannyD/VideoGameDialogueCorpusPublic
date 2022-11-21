import json,csv,copy


with open("data.json") as json_file:
	d = json.load(json_file)["text"]
	
					
def getTextByCharacters(var,characterKeys):
	global prevLine
	for k in var:
		if isinstance(var, dict):
			v = var[k]
			if k in characterKeys:
				yield prevLine,v
			if (isinstance(v,str)) and not k.startswith("_"):
				prevLine = k+": "+v
				#print(prevLine)
			for result in getTextByCharacters(v,characterKeys):
				yield result
		elif isinstance(var, list):
				for result in getTextByCharacters(k,characterKeys):
					yield result
					
prevLine = ""
res = getTextByCharacters(d,["Jessie"])

res = [[x[0],x[1]] for x in res]

header = ["PreviousLine","JessieLine"]

with open('../../../results/doNotShare/JessieDialogue_FFVII_Remake.csv', 'wt') as f:
	csv_writer = csv.writer(f, quoting=csv.QUOTE_ALL)
	csv_writer.writerow(header) # write header
	for row in res:
		csv_writer.writerow(row)