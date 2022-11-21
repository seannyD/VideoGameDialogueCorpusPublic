from bs4 import BeautifulSoup
import re

# TODO:
# Remove "<emp>" tags

DAI_existingTalkstringIDs = ""

def parseFile(fileName,parameters={},asJSON=False):
	global DAI_existingTalkstringIDs
	
	# Avoid debug files and cut content
	if fileName.count("_debug")>0 or fileName.startswith("zz_")>0:
		return([])
	
	print(fileName)
	# input is an unencoded dlg file
	
	xml = open(fileName,'r', encoding = 'utf8')
	soup = BeautifulSoup( xml, "lxml")
	
	# Load ids
	if len(DAI_existingTalkstringIDs)==0:
		existingTalkstringIDFile = open("../data/DragonAge/DragonAgeOrigins_B/talkstringIDs.xml").read()
		DAI_existingTalkstringIDs = existingTalkstringIDFile.split(",")
	
	
	out = []
	
	voBank = soup.find("string", {"alias": "ConversationVOBank"}, recursive=True).getText()
	
	ownerCharName = "OWNER_"+voBank
	
	conv = soup.find("generic_list", {"alias":"ConversationLineList"})
	
	
	def parseStruct(struct):
		label = struct["label"]
		speaker = struct.find("string", {"alias":"ConversationLineSpeaker"}).getText().strip()
		listener = struct.find("string", {"alias":"ConversationLineListener"}).getText().strip()
		lineID = struct.find("tlkstring", {"alias": "ConversationLineText"}).getText().strip()
		childList = struct.find("uint32_list", {"alias": "ConversationLineChildrenList"})
		childList = [x.getText() for x in childList.find_all("uint32") if len(x.getText().strip()) >0]
		return (label, speaker, listener, lineID, childList)
	
	bits = {}
	for struct in [x for x in conv if len(x.getText().strip())>0]:
		label, speaker, listener, lineID, childList = parseStruct(struct)
		bits[label] = (speaker, listener, lineID, childList)
	
	# Get conversation starting points
	startingListStruct = soup.find("uint32_list", {"alias": "ConversationStartingList"}, recursive=True)
	startingList = [bit.getText() for bit in startingListStruct if len(bit.getText().strip())>0]

	def getOutFromLabel(label):
		speaker, listener, lineID, childList = bits[label]
		if speaker == "OWNER":
			speaker = ownerCharName
		if label in visitedIDs:
			return([{"GOTO": lineID}])
		else:
			outx = []
			if lineID in DAI_existingTalkstringIDs:
				outx.append({speaker: lineID, "_ID": lineID})
			visitedIDs.append(label)
			choices = []
			for child in childList:
				choices.append(getOutFromLabel(child))
			if len(choices)>0:
				if len(choices)==1:
					outx += choices[0]
				else:
					outx.append({"CHOICE": choices})			
			return(outx)

	visitedIDs = []
	out = [{"ACTION":"File: "+fileName}]
	
	for st in startingList:
		stx = getOutFromLabel(st)
		if len(stx)>0:
			out.append({"ACTION":"---"})
			out += stx
			


	if asJSON:
		print(json.dumps({"text":out}, indent = 4))
		return(json.dumps({"text":out}, indent = 4))
	return(out)


def postProcessing(out):

	talkStrings = {}
	xml = open("../data/DragonAge/DragonAgeOrigins_B/raw/singleplayer_en-us.xml")
	soup = BeautifulSoup( xml, "lxml")
	for st in soup.find_all("string"):
		talkStrings[st["id"]] = st.getText()
	
	def getText(line):
		k = [x for x in line if not x.startswith("_")][0]
		if line[k] in talkStrings:
			#line["_ID"] = line[k]
			line[k] = talkStrings[line[k]]
			
			# TODO: Handle description lines 
			#  (which can also include dialogue)
			#if line[k].startswith("<desc") or line[k].startswith("<act"):
			#	dlg = line[k].replace("<desc>","").replace("</desc>","")
			#	dlg = line[k].replace("<act>","").replace("</act>","")
			#	line["ACTION"] = dlg
			#	line.pop(k)
			#	line["_ID"] = line.pop("_ID")
		else:
			pass # TODO: problem?
			
			
	def walk(var):
		if not isinstance(var,str) and (not isinstance(var,int)):
			for k in var:
				if isinstance(var, dict):
					if not k in ["CHOICE","GOTO"]:
						getText(var)
					v = var[k]
					walk(v)
				elif isinstance(var, list):
					walk(k)
	# Replace dialogue IDs with text
	walk(out)
	
	
	def cleanLine(dlg):
		dlg = dlg.replace("<desc>","(")
		dlg = dlg.replace("</desc>",")")
		# Emphasis
		dlg = dlg.replace("<emp>"," ")
		dlg = dlg.replace("</emp>"," ")
		dlg = re.sub(" +"," ",dlg)
		return(dlg)
	
	def splitAction(line):
		ret = []
		k = [x for x in line if not x.startswith("_")][0]
		dialogue = line[k]
		if dialogue.count("<act>")>0:
			# <act>Lie</act> He's guilty. Here's the lyrium. <act>Give 1 nugget.</act>
			parts = re.split("</?act>",dialogue)
			dialogue = parts[::2]
			actions = parts[1::2]
			for d,a in zip(dialogue,actions):
				a = a.replace("<act>","").replace("</act>","").strip()
				if len(a)>0:
					ret.append({"ACTION": a})
				if len(d.strip())>0:
					ret.append({k: d.strip()})
		return(ret)
	
	def splitActions(outx):
		out2 = []
		for line in outx:
			if "CHOICE" in line:
				choices = []
				for choice in line["CHOICE"]:
					choices.append(splitActions(choice))
				out2.append({"CHOICE": choices})
			else:
				k = [x for x in line if not x.startswith("_")][0]
				dlg = line[k]
				if dlg.count("<act")>0:
					out2 += splitAction(line)
				else:
					line[k] = cleanLine(line[k])
					out2.append(line)
		return(out2)
	
	out2 = splitActions(out)
	
	return(out2)
					
					
					