# https://www.youtube.com/watch?v=xyt8dqqmTbI

import json, csv, re,os
from bs4 import BeautifulSoup

da3 = {}

def parseFile(fileName,asJSON=False):


	def cleanString(txt):
		txt = txt.replace("\x19s","'")
		return(txt)

	# This method just loads the text strings
	# from the StringList_en.csv file
	# see post processing for recursive search 
	#  through the conversation files
	firstLine=True
	for line in open(fileName, encoding='latin-1'):
		if firstLine:
			line = "."+line
			firstLine = False
		line = line[1::2].strip()
		if len(line)>0:
			stringID,text = line.split(",",1)
			text = cleanString(text)
			da3[stringID] = text
	
	out = []
	
	if asJSON:
		print(json.dumps({"text":out}, indent = 4))
		return(json.dumps({"text":out}, indent = 4))
	return(out)
	
###############

def processXMLFile(txt):
	soup = BeautifulSoup(txt, "lxml")
	
	lines = soup.find_all("conversationline")
	plines = processLines(lines)
	
	links = soup.find_all("conversationlink")
	plines += processLines(links)
	
	# Make a dictionary for easy reference
	lineDict = {}
	for lx in plines:
		lineDict[lx["id"]] = lx
	
	# "Conversation" tags start conversation
	conversations = soup.find_all("conversation")
	
	# Build the conversation structure 
	# (need recursive function)
	out = []
	for conv in conversations:
		#print(conv["guid"])
		childIDs = getChildNodes(conv)
		print(childIDs)
	
	return(plines)

def processLines(data):
	# PC dialogue has <ParaphraseReference> (the cue)
	# and ConversationStringReference that contains 
	# the actual line that is spoken by the character
	out = []
	for line in data:
		lx = {"id":line["guid"],"type":line.name}
		# Add dialogue line
		dt = line.find("conversationstringreference")
		if dt:
			stringID = dt.find("stringid").get_text().replace("0x","").strip()
			lx["dialogue"] = da3[stringID.upper()]
		
		# Add other attributes
		for tag in ["ParaphraseReference","Speaker","SpeakerGender","PlotActions","PlotConditions"]:
			addNodeData(line,tag.lower(),lx)
		if "paraphrasereference" in lx:
			lx["paraphrasereference"] = da3[lx["paraphrasereference"].upper()]
		
		# Add child ids
		lx["childIDs"] = getChildNodes(line)
		addNodeData(line,"linkedline",lx)	
		
		# TODO: Add PlotActions and PlotConditions 
		out.append(lx)
	return(out)
	

def addNodeData(soup,tag,d):
	t = soup.find(tag)
	if t:
		txt = t.get_text().replace("0x","").strip()
		if txt!="00000000":
			d[tag] = txt

def getChildNodes(soup):
	cn = soup.find("childnodes")
	childIDs = [member.get_text() for member in cn.find_all("member")]
	childIDs = [re.sub("\\[.+?\\]","",x).strip() for x in childIDs]
	return(childIDs)
		
		
	

def postProcessing(out):
	
	files = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser("../data/DragonAge/DragonAgeInquisition_B/raw/")) for f in fn]
	
	files = [x for x in files if x.endswith(".xml")]
	
	for file in files:
		print(">>>")
		print(file)
		txt = open(file).read()
		out += processXMLFile(txt)
	
	return out

	

	
	



