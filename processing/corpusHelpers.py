import re
import numpy as np

def get_keys_recursively(var):
	if not isinstance(var,str) and (not isinstance(var,int)):
		for k in var:
			if isinstance(var, dict):
				if not k.startswith("_"):
					yield k
				v = var[k]
				for result in get_keys_recursively(v):
					yield result
			elif isinstance(var, list):
				for result in get_keys_recursively(k):
					yield result

#def countItems(it):
#	k = list(set(it))
#	counts = [it.count(x) for x in k]
#	return(dict(zip(k,counts)))
	
#def countCategories(counts,members):
#	return(sum([count for n,count in counts.items() if n in members]))
	
#def countGroups(counts,groups):
#	groupCounts = [countCategories(counts,members) for group,members in groups.items()]
#	return(dict(zip(groups.keys(),groupCounts)))


def getAllCharacterTexts(var, excludeKeys=["ACTION","CHOICE","LOCATION","COMMENT","SYSTEM","GOTO","NARRATIVE","STATUS"],getNames=False):
	if isinstance(var,dict) or isinstance(var,list):
		for k in var:
			if isinstance(var, dict):
				v = var[k]
				if not (k in excludeKeys or k.startswith("_")):
					if getNames:
						yield (k,v)
					else:
						yield(v)
				for result in getAllCharacterTexts(v,excludeKeys,getNames):
					yield result
			elif isinstance(var, list):
				for result in getAllCharacterTexts(k,excludeKeys,getNames):
					yield result	
	
def getTextByCharacters(var,characterKeys):
	if isinstance(var,dict) or isinstance(var,list):
		for k in var:
			if isinstance(var, dict):
				v = var[k]
				if k in characterKeys:
					yield v
				for result in getTextByCharacters(v,characterKeys):
					yield result
			elif isinstance(var, list):
				for result in getTextByCharacters(k,characterKeys):
					yield result

def cleanText(t):
	# Replace elipses (which confuse the sentence count) with full stops
	re.sub("\\.[\\. -]+",". ",t)
	# Replace full stops after punctuation
	t = re.sub("([!\\?,])\\.","\\1",t)
	# multiple exclamations/question marks
	t = re.sub("([!\\?])[!\\?]+","\\1",t) 
	# Normalise spaces
	t = re.sub(" +"," ",t)
	return(t)
	
def getNameToGroup(meta):
	ret = {}
	for group in meta["characterGroups"]:
		for charName in meta["characterGroups"][group]:
			ret[charName] = group
	return(ret)




def levenshtein_ratio_and_distance(s, t, ratio_calc = False):
	""" levenshtein_ratio_and_distance:
		Calculates levenshtein distance between two strings.
		If ratio_calc = True, the function computes the
		levenshtein distance ratio of similarity between two strings
		For all i and j, distance[i,j] will contain the Levenshtein
		distance between the first i characters of s and the
		first j characters of t
	"""
	# Initialize matrix of zeros
	rows = len(s)+1
	cols = len(t)+1
	distance = np.zeros((rows,cols),dtype = int)

	# Populate matrix of zeros with the indeces of each character of both strings
	for i in range(1, rows):
		for k in range(1,cols):
			distance[i][0] = i
			distance[0][k] = k

	# Iterate over the matrix to compute the cost of deletions,insertions and/or substitutions	
	for col in range(1, cols):
		for row in range(1, rows):
			if s[row-1] == t[col-1]:
				cost = 0 # If the characters are the same in the two strings in a given position [i,j] then the cost is 0
			else:
				# In order to align the results with those of the Python Levenshtein package, if we choose to calculate the ratio
				# the cost of a substitution is 2. If we calculate just distance, then the cost of a substitution is 1.
				if ratio_calc == True:
					cost = 2
				else:
					cost = 1
			distance[row][col] = min(distance[row-1][col] + 1,	  # Cost of deletions
								 distance[row][col-1] + 1,		  # Cost of insertions
								 distance[row-1][col-1] + cost)	 # Cost of substitutions
	if ratio_calc == True:
		# Computation of the Levenshtein Distance Ratio
		Ratio = ((len(s)+len(t)) - distance[row][col]) / (len(s)+len(t))
		return (Ratio)
	else:
		return (distance[row][col])	
	
	
