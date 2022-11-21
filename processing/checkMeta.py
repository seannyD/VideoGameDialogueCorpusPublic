import os, json, re, csv, sys
from corpusHelpers import *



def checkMeta(folder,meta,d):
	# No coding of neutral and one other category.
	neutral = []
	other = []
	for group in meta["characterGroups"]:
		if group=="neutral":
			neutral = meta["characterGroups"][group]
		else:
			other += meta["characterGroups"][group]
	
	neutralAndOther = set(neutral).intersection(set(other))
	if len(neutralAndOther)>0:
		print("Warning: Characters neutral and other ...")
		print("   "+ ",".join(neutralAndOther))

	# No characters who don't appear in script
	scriptCharacters = [x for x in get_keys_recursively(d)]
	notInScript = set(neutral+other).difference(set(scriptCharacters))
	if len(notInScript) >0:
		print("Warning: Characters in meta but not in script ...")
		print("    "+ ",".join(notInScript))
	
	

allFolders = [root+os.sep for root,dirs,files in os.walk("../data/") if "meta.json" in files]

foldersToProcess  = []

# Allow parsing of just one game
if len(sys.argv)>1:
	fx = sys.argv[-1]
	if not fx.endswith(os.sep):
		fx += os.sep
	foldersToProcess = [fx]
else:
	for f in allFolders:
		foldersToProcess.append(f)

for folder in foldersToProcess:
	print("\n\n\n")
	print("PROCESSING "+folder+ " ...")
	
	if not (os.path.isfile(folder+"meta.json") and os.path.isfile(folder+"data.json")):
		print("##########")
		print("JSON files not found")
		continue

	with open(folder+"meta.json") as json_file:
		meta = json.load(json_file)
	with open(folder+"data.json") as json_file:
		d = json.load(json_file)["text"]
		
	checkMeta(folder,meta,d)
