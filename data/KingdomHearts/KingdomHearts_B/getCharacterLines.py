import json,codecs


rename = """Sora- 3,16,23,26,36,41,45,49,52,68, 70
Selphie- 40,42,
Wakka- 44, 46,
Tidus- 48, 50,
Riku- 86
Cid-329, 331, 333, 336
Leon- 358, 360, 362, 365, 368
Aerith- 381
Yuffie- 391, 370
hades- 507,
Jafar- 509, 1075,1080, 1363
Ursula- 511,513, 1084
Oogie Boogie- 516, 1078
Captain Hook- 515, 518, 1560, 2294, 2308
Smee- 2309, 2313,
Philoctetes- 731, 733, 738
Maleficent- 519, 521, 880, 1076, 1081, 1083, 1085
Tarzan- 898,900, 903, 909,913, 916, 919, 924,926
Merlin- 1161, 1163, 1165, 1168
Fairy Godmother- 1182
Pooh- 1202, 1204, 1206
Jasmine- 1378, 1380
Piglet- 1576, 1578
Geppetto- 1673, 1676, 1681, 1683
Rabbit- 1774, 1778, 1783
Tigger- 1818
Ariel- 1867
Mayor- 2124
Clayton- 946, 952
Peter Pan- 2327, 2329, 2332, 2334, 2336, 2339, 2341, 2343, 2345, 2348, 2351
Wendy- 2380
Jiminy- 247,249
Xemnas- 3077, 3079, 3081, 3084, 3086, 3088, 3090, 3093, 3095, 3098, 3100
Ansem (in robed form)- 192, 194, 196,200,202,204, 2634, 2636, 2640, 2642, 2644, 2646"""

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

