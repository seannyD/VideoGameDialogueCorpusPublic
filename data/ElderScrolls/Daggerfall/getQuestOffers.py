import json,csv

with open("meta.json") as json_file:
	meta = json.load(json_file)
gender = meta["characterGroups"]

with open("data.json") as json_file:
	data = json.load(json_file)["text"]
	
def getBits(line, getLineNum=0):
	charName = [x for x in line.keys() if not x.startswith("_")][0]
	offer = [v for k,v in line.items() if not k.startswith("_")][0]		
	print(">>>>"+charName)		
	print(getLineNum)
	print(line)
	if charName=="CHOICE":
		# sometimes there can be multiple lines that the questor chooses randomly
		# Char name is first 
		charName = [k for k in line["CHOICE"][0][0].keys() if not k.startswith("_")][0]
		offer = " // ".join([i[0][1] for i in [list(bit[0].items()) for bit in line["CHOICE"]] if not i[0][0].startswith("_")])
	return((charName,offer))

out = []
for i in range(len(data)-1):
	line = data[i]
	if "_Type" in line:
		if line["_Type"]=="QuestorOffer":
			nextChoice = data[i+1]
			if "CHOICE" in nextChoice:
				charName,offer = getBits(line)
					
				accept = ""
				refuse = ""
				resp = nextChoice["CHOICE"]
				yesResp = resp[0]
				if len(yesResp)>1:
					print(resp[0][1])
					acceptChar,accept = getBits(resp[0][1],1)
					#accept = list(yesResp[1].values())[0]
				noResp = resp[1]
				if len(noResp)>1:
					print(resp[0][1])
					refuseChar,refuse = getBits(resp[1][1],1)
					#refuse = list(noResp[1].values())[0]
				
				charGender = "random"
				if charName in gender["male"]:
					charGender = "male"
				if charName in gender["female"]:
					charGender = "female"
					
				out.append([charName,charGender,offer,accept,refuse])
				
				
				
with open('questOffers.csv', mode='w') as csv_file:
	csv_writer = csv.writer(csv_file)
	csv_writer.writerow(["name",'gender','offer','accept','refuse'])
	for row in out:
		csv_writer.writerow(row)