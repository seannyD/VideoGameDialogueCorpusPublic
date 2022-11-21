import os, json, re, csv, sys
from corpusHelpers import *

# TODO: are we checking that lines actually have spoken content?


def walkDialogue(var, prevChar=["-"]):
	# the previous line of dialogue can potentially be from multiple 
	# speakers depending on the choice.
	# This algorithm captures all possible transitions in the tree.
	out = []
	if not isinstance(var,str) and (not isinstance(var,int)):
		if isinstance(var,list):
			for i in range(len(var)):
				dx = var[i]
				if isinstance(dx,dict):
					# get character name
					nx = [x for x in dx if not x.startswith("_")][0]
					if nx!="CHOICE":
						out.append((prevChar,nx))
						prevChar = [nx]
					else:
						#print(dx["CHOICE"])
						lastLines = []
						for subchoice in dx["CHOICE"]:
							# TODO: What about empty choices?
							if len(subchoice)>0:
								subchoices = walkDialogue(subchoice,prevChar)
								out += subchoices
								if len(subchoices)>0:
									lastLines.append(subchoices[-1][1])
						prevChar = lastLines

	return(out)

def getGroup(cx):
	global name2Group
	if cx in name2Group:
		if not cx in ["ACTION","LOCATION","NARRATIVE"]:
			return(name2Group[cx])
	# Otherwise
	return("-")


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

name2Group = None

printTransition = False


for folder in foldersToProcess:
	print(folder)
	if os.path.isfile(folder+"meta.json") and os.path.isfile(folder+"data.json"):
		with open(folder+"meta.json") as json_file:
			meta = json.load(json_file)
		with open(folder+"data.json") as json_file:
			d = json.load(json_file)["text"]
		
		includeGame = True
		# alternativeMeasure is true if this parsing should not count 
		# as part of the main list of results (e.g. alternative versions)
		if "alternativeMeasure" in meta:
			if meta["alternativeMeasure"]:
				includeGame = False
		if sys.argv[-1].count("Test/")>0:
			includeGame = True
		
		if includeGame:	
			# See corpusHelpers.py	
			name2Group = getNameToGroup(meta)
			series = meta["series"]
			game = meta["game"]
			
			transitions = {}
			prevGroup = "-"
			currentGroup = "-"
			
			transitionSting = ""

			for prevCharList,currentChar in walkDialogue(d,"-"):
				for prevChar in prevCharList:
					# Some lines of dialogue are just the same person continuing to speak
					# We don't want to count these
					if not prevChar==currentChar:
						prevGroup = getGroup(prevChar)
						currentGroup = getGroup(currentChar)

						try:
							transitions[(prevGroup,currentGroup)] += 1
						except:
							transitions[(prevGroup,currentGroup)] = 1
						
						transitionSting += currentGroup[0]					
						if printTransition:
							if prevGroup=="female" and currentGroup=="female":
								print((prevChar,currentChar))
			
			allGroups = list(set([x[0] for x in transitions.keys()] + [x[1] for x in transitions.keys()]))
			
			out = "folder,series,game,from,to,frequency\n"
			for g1,g2 in transitions.keys():
				out += ",".join([folder, series, game, g1,g2,str(transitions[(g1,g2)])])+"\n"
			
			with open(folder+"transitions.csv",'w') as o:
				o.write(out)
			with open(folder+"transitions_all.txt",'w') as o:
				o.write(transitionSting)
			
