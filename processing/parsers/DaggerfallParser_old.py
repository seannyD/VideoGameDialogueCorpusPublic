from bs4 import BeautifulSoup
import json, re

# Todo: Track non-named NPCs and their gender
#   Add quest ID to non-named NPC name
#   Fix: "Chulmore Quill\nPerson"
# TODO: Handle 'do' links  "repute with _gaffer_ exceeds 10 do _S.30_ "

def cleanLine(txt):
	if txt.strip().startswith(">"):
		return("")
	txt = re.sub("^:","",txt)
	# don't include player input options
	txt = txt.strip()
	# Remove lines that start with parentheses and have nothing else
	txt = re.sub(r'^\([^)]*\)', '', txt)
	txt = txt.replace("...","... ")
	return(txt)
	

def parseFile(fileName,parameters={},asJSON=False):

	o = open(fileName)
	d = o.read()
	o.close()
	
	d = d.replace("_\n_","_\n\n_")
	
	events = [x.strip() for x in d.split("\n\n") if x.strip().startswith("_S") or x.strip().startswith("QuestorOffer:")]
	
	#Person _gaffer_ face 73 named Chulmore_Quill
	
	people = re.findall("\nPerson ([^ ]+).*? named ([^ \n]+?)[ \n]",d)
	idToName = {}
	for p in people:
		idToName[p[0]] = p[1].replace("_"," ")
	
	talkTo = {}
	say = []
	prompts = []
	for event in events:
		idx = event[:event.index(" ")].replace(":","")

		links = re.findall("when (_.+?_)",event) + re.findall("when.+? and (_.+?_)",event)
		if event.count("say ")>0:
			links += [idx]

		#links = re.findall("_S\\..+?_",event)
		talkingTo = re.findall("clicked npc ([^ \n]+)",event)
		talkingTo += re.findall(" ([^ ]+?) clicked",event)
		if len(talkingTo)>0:
			talkTo[idx] = talkingTo[-1]
		ss = re.findall("say ([0-9]+)",event)
		for link in links:
			for s in ss:
				say.append((link,s))
#		if len(ss)>0 and len(links)==0 and len(talkingTo)>0:
#			talkTo[idx] = talkingTo[-1]

		ps = re.findall("prompt ([^ ]+) yes ([^ ]+) no ([^ ]+)",event)
		#plinks = re.findall("_S.+?_",event)
		for p in ps:
			lx = [re.findall("_S.+?_",x) for x in event.split('\n') if x.strip().startswith("when")]
			plinks = sum(lx, []) # unlist
			prompts.append((idx,p,plinks))

	print(talkTo)
	print(say)
	
	d = re.sub("\n +\n","\n\n",d)
	messages = [x.strip() for x in d.split('\n\n') if x.strip().startswith("Message:") or any([x.startswith(y) for y in ["QuestorOffer","RefuseQuest","AcceptQuest"]])]
	
	dialogue = {}	
	for m in messages:
		txt = m[m.index('\n')+1:]
		txt = re.sub(" +"," ",txt.replace("<ce>"," ").replace("\n", " ")).strip()

		p1 = m[:m.index(":")]
		if p1 in ["QuestorOffer","RefuseQuest","AcceptQuest"]:
			dialogue[p1] = txt
		else:
			mnum = m[m.index(":")+1:].replace("[","").replace("]","").strip()
			mnum = mnum[:mnum.index("\n")].strip()		
			dialogue[mnum]=txt
		
	out = []
	addedDialogue = []
	
	# Handle prompts first
	for prompt in prompts:
		sID = prompt[0]
		dID = prompt[1][0]
		yesID = prompt[1][1]
		noID = prompt[1][2]
		slinks = prompt[2]
		slinks = [x for x in slinks if x in talkTo]

		if len(slinks)>0:
			charID = talkTo[slinks[0]]
			if yesID == "yes":
				yesID2 = "AcceptQuest"
			else:
				yesID2C = [x[1] for x in say if x[0]==yesID]
				if len(yesID2C)>0:
					yesID2 = yesID2C[0]
			if noID == "no" or noID=="_no_":
				noID2 = "RefuseQuest"			
			else:
				noID2C = [x[1] for x in say if x[0]==noID]
				if len(noID2C)>0:
					noID2 = noID2C[0]
			if dID in dialogue and yesID2 in dialogue and noID2 in dialogue:
				charName = charID
				if charID in idToName:
					charName = idToName[charID]
				out.append({charName:dialogue[dID]})
				addedDialogue.append(dID)

				out.append({"CHOICE":[
						[{"PC":"Yes"},{charName:dialogue[yesID2]}],
						[{"PC":"No" },{charName:dialogue[noID2 ]}]]})
				addedDialogue.append(yesID2)
				addedDialogue.append(noID2)
				
	for s in say:
		sLink = s[0]
		dialogueID = s[1]
		if dialogueID in dialogue and not dialogueID in addedDialogue:
			dtxt = dialogue[dialogueID]
			if dtxt.count("seduce")>0:
				print("---")
				print(sLink)
				print(talkTo)
			if sLink in talkTo:   # SOME PROBLEM HERE - should this be ""
				charID = talkTo[sLink]
				charName = charID
				if charID in idToName:
					charName = idToName[charID]
				out.append({charName:dtxt})
				addedDialogue.append(dialogueID)
	
				
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)