import json,codecs


rename = u"""Ansem (Ansem, Seeker of Darkness)- 23, 25, 31
Dusk (neutral)- 128
Ansem (Riku~Ansem) - 167, 302, 307, 309, 394, 396, 438, 441, 651, 654, 656, 659
Axel - 544, 546 
Xemnas - 906, 1477, 1480, 1482, 1488, 5614, 5616
Roxas- 907, 910, 7800, 7803, 7805, 7807, 7809
Riku- 909, 971
Xigbar- 1493, 1495, 1497, 1499, 1501, 1504, 1507,1509, 1511
Xaldin- 2061, 2063, 2065
Demyx- 2266, 2491
Saïx-  4793, 4795, 4798, 4800,4804,4806,4808
Luxord - 6097, 6099, 6101"""

charDats = [(x.split("-")[0].strip(),[int(y.strip()) for y in x.split("-")[1].split(",") if len(y.strip())>0]) for x in rename.split("\n")]

o = open("data.json")
d =o.read()
o.close()

d = d.split("\n")

out = {}
for charName,lineNums in charDats:
	dial = []
	for lineNum in lineNums:
		lx = d[lineNum-1]
		if lx.count("??")==0:
			lx = d[lineNum]
		if lx.count("??")==0:
			lx = d[lineNum+2]
		if lx.count("??")>0:
			oldName = lx[:lx.index(":")].replace('"',"").replace("{","").strip()
			dialogue = lx[lx.index(":")+1:lx.rindex('"')+1].replace('"',"").strip()
			
			if not oldName in out:
				out[oldName]={}
			if not charName in out[oldName]:
				out[oldName][charName] = []
			out[oldName][charName].append(dialogue)
		else:
			print(("Error: ",charName,lineNum))



out2= json.dumps(out, indent = 4)
o = open("charLineFixes.json",'w')
o.write(out2)
o.close()

