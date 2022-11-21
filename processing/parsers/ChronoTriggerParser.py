from bs4 import BeautifulSoup
import json
import re
import xlrd


# Can "rat" be coded accurately?

# Hey? You're not a wimp, are you?! C'mon eat up! Ok. No.


#Hey! It's those people again!	„ÅÇÔºÅ„ÄÄ„ÅäÂÖÑ„Å°„ÇÉ„ÇìÈÅîÔºÅ	Ah! Bro, it's you guys!	literally 'big brother and other(s)', used if Crono is in the  group
#Hey! It's them!	„ÅÇÔºÅ„ÄÄ„ÅäÂßâ„Å°„ÇÉ„ÇìÈÅîÔºÅ	Ah! Sis, it's you guys!	literally 'big sister and  other(s)', used if Marle or Lucca is in the group but Crono isn't

def cleanJapanese(txt):
	txt = txt.replace('[END]'," ")
	txt = txt.replace("\n"," ")
	txt = re.sub(" +"," ",txt)
	txt = txt.replace("ゴホッ、ゴホホ","(ゴホッ、ゴホホ)")
	txt = txt.replace("フフン","(フフン)").replace("うふふ","(うふふ)")
	return(txt)

def parseFile(fileName,parameters={},asJSON=False):


	avoidCharacters = ["these two telepod exhibit lines are unused", "ingthenwngerewess tw"]
	
	o = open(fileName)
	d = o.read()
	o.close()
	
	d = d.replace("(blank)", "[Unused lines]")
	d = d.replace("[heart]", "([heart])")
	# Take out "lost lines" section
	if d.count("you are able to locate any of these"):
		d = d[:d.index("you are able to locate any of these")]
		d = d.replace("Lost Lines","")
	
	
	html = BeautifulSoup(d, 'lxml')
	#table = html.find("table")
 	
	startParse = 2
	if d.count("Chrono Trigger script")>0:
		startParse = 0
	
	charName = ""
	dLineO = ""
	dLineJ = ""
	dLineR = ""
	dLineT = ""
	
	def cleanEnglish(txt):
		txt = txt.replace("*giggle*",'(giggle)')
		txt = txt.replace("*cough*",'(cough)')
		txt = txt.replace("chuckle", " (chuckle) ")
		txt = txt.replace('Â'," ")
		txt = txt.replace("\n"," ")
		txt = re.sub(" +"," ",txt)
		return(txt)
	
	out = []
	for tr in html.find_all("tr"):
		parts = [td.get_text() for td in tr.find_all("td")]
		if startParse<2:
			if parts[0].count("3.) Chrono Trigger script")>0:
				startParse+=1
		else:
			if len(parts)>=5:
				# add in line delimiters to keep track for later
				dLineO += " # "
				dLineJ += " # "
				dLineR += " # "
				dLineT += " # "

			
				original = parts[0].replace("Â","").strip()
				japanese = parts[2]
				retranslate = parts[4]
				translateComment = ""
				
				
				if len(parts)>=7:
					translateComment = parts[6].strip()
				
				if re.match(u"^[A-Za-z \-]+:",original):
					# New character, so dump currently stored line
					outX = {
						charName:cleanEnglish(dLineO.strip()), 
						"_Japanese":cleanJapanese(dLineJ.strip()), 
						"_Retranslate":cleanEnglish(dLineR.strip())}
					if len(dLineT.strip())>0:
						outX["_TranslateComment"] = dLineT.strip()
					if not charName in avoidCharacters:
						out.append(outX)
					dLineO,dLineJ,dLineR,dLineT = ("","","","")
				
					# Change to new character
					charName = original.split(":")[0].strip().replace("[","").replace("]","").lower()
					dLineO += " " + original.split(":")[1].strip()
					dLineT += translateComment.replace("\n"," ").strip()
					try:
						# some lines are misaligned, e.g. see "まりウロウロし" in chapter 2
						dLineJ += " " + japanese.split("「")[1].strip()
						dLineR += " " + retranslate.split(":")[1].strip()
					except:
						pass
				elif re.match("^\[[A-Za-z ,\.'0-9\?\-;:é]+\]$",original):
					# Location, so dump currently stored line
					outX = {
						charName:cleanEnglish(dLineO.strip()), 
						"_Japanese":cleanJapanese(dLineJ.strip()), 
						"_Retranslate":cleanEnglish(dLineR.strip())}
					if len(dLineT.strip())>0:
						outX["_TranslateComment"] = dLineT.strip()
					if not charName in avoidCharacters:
						out.append(outX)
					dLineO,dLineJ,dLineR,dLineT = ("","","","")
				
					if (original.count("A.D.")>0 or  original.count("B.C.")>0):
						location = original.replace("[","").replace("]","").strip()		
						#location = re.sub("\-+","-",location)
						out.append({"LOCATION":location})
					else:
						# Change Character
						charName = original.replace("[","").replace("]","").strip().lower()
				else:
					dLineO += " "+ original.strip()
					dLineJ += " "+ japanese.strip()
					dLineR += " "+ retranslate.strip()
					dLineT += " " + translateComment.strip()
	# Final dump of leftover stuff
	outX = {charName:cleanEnglish(dLineO.strip()), 
			"_Japanese":cleanJapanese(dLineJ.strip()), 
			"_Retranslate":cleanEnglish(dLineR.strip())}
	if len(dLineT.strip())>0:
		outX["_TranslateComment"] = re.sub(" +"," ",dLineT.replace("\n"," ").strip())
	if not charName in avoidCharacters:
		out.append(outX)		
	
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)
	
def postProcessing(out):

	makeChoiceLog = False

	def sliceQuestion(txt,sp1 = "# Yes"):
		if txt.count(sp1)==0:
			for x in ["#  や", "#  買", "#  と", "#  好き", "#  押す", "#  はら", "#  Do"]:
				if txt.count(x)>0:
					sp1 = x
					break

		stub = txt[txt.index(sp1):]
		optionDiv = "# #"
		if stub.count(optionDiv)==0:
			optionDiv = "#   #"
		options = stub[:stub.index(optionDiv)]
		options = [x for x in options.split("#") if len(x.replace("#","").strip())]
		responses = stub[stub.index(optionDiv)+len(optionDiv):]
		responses = [x for x in responses.split("# #") if len(x.replace("#","").strip())>0]
#		print(options)
#		print(responses)
		return((options,responses))
		
#	def isChoice(original):
#		if original.count("# Yes. # No.")>0 or original.count("# Yes # No #"):
#			ypos = original.index("# Yes")
#			originalA = original[original.index("#",ypos):]
#			if len(originalA.replace("#","").strip())>0:
#				return(True)
#		return(False)
		
	def isChoice(japanese):
		if japanese.count("？ #")>0:
			if japanese.count("[END] #   #")>0:
				answer = japanese[japanese.index("[END] #   #")+11:].replace("#","").strip()
				if len(answer)>0:
					return(True)
		if japanese.count("はたし")>0 or japanese.count("よろしい")>0 or japanese.count("本当にそう")>0:
			return(True)
		return(False)
	
	if makeChoiceLog:
		choiceLog = ""
		choiceLogHeader = "X\tXQuestion\tXOp1\tXOp2\tXOp3\tXA1\tXA2\tXA3\tXNext\t"
		for x in ["Orig", "Jap", "Ret"]:
			choiceLog += choiceLogHeader.replace("X",x)
		choiceLog += "\n"
	
	
		choiceCount = 0
		for line in out:
			charName = [x for x in line.keys() if not x.startswith("_")][0]
			original = line[charName]
			foundQuestion = False
			if "_Japanese" in line and "_Retranslate" in line:
				japanese = line["_Japanese"]
				retranslate = line["_Retranslate"]
		
				if isChoice(japanese):
					choiceCount += 1
					# This is a choice
				#origQ,origA = sliceQuestion(original)
				#japQ,japA = sliceQuestion(japanese,"#  はい ")
				#retQ,retA = sliceQuestion(retranslate)
			
					choiceLog += original +"\t\t\t\t\t\t\t\t\t" + japanese +"\t\t\t\t\t\t\t\t\t" + retranslate + '\n'
	
		with open("../data/ChronoTrigger/ChronoTrigger/QuestionSplitter.csv",'w') as f:
			f.write(choiceLog)


	def loadQuestionSlices():
		fn = "../data/ChronoTrigger/ChronoTrigger/QuestionSplitter.xlsx"
		workbook = xlrd.open_workbook(fn)
		worksheet = workbook.sheet_by_index(0)
		
		header = []
		choiceLogHeader = "X\tXQuestion\tXOp1\tXOp2\tXOp3\tXOp4\tXA1\tXA2\tXA3\tXA4\tXNext"
		for x in ["Orig", "Jap", "Ret"]:
			header += choiceLogHeader.replace("X",x).split("\t")
		header = header[1:]
		#print(header)
		d = {}
		for row in range(1, worksheet.nrows):
#			for col in range(len(header)+1):
#				print(worksheet.cell_value(row, col))
			bits = [worksheet.cell_value(row, col) for col in range(len(header)+1)]
			if len(bits[0].strip())>0:
				cleanBits = [re.sub(" +"," ",x.replace("#"," ")).strip() for x in bits[1:]]
				zp = zip(header,cleanBits)
				#zp = [(h,b) for h,b in zp if len(b)>0]
				d[bits[0]] = dict(zp)
		return((d,header))

	qSlices,header = loadQuestionSlices()
	
	def makeQuestion(charName,q):
		# initial line
		qBit = {charName:q["OrigQuestion"]}
		if len(q["JapQuestion"])>0:
			qBit["_Japanese"] = cleanJapanese(q["JapQuestion"])
		if len(q["RetQuestion"])>0:
			qBit["_Retranslate"] = q["RetQuestion"]
		outx = [qBit]
		
		# Choices
		choices = []
		for i in ["1","2","3","4"]:
			origOp, origA, japOp, japA, retOp, retA = [q["OrigOp"+i], q["OrigA"+i], q["JapOp"+i], q["JapA"+i], q["RetOp"+i], q["RetA"+i]]
			choice = []
			if len(origOp)>0:
				bit = {"crono": origOp}
				if len(japOp)>0:
					bit["_Japanese"] = cleanJapanese(japOp)
				if len(retOp)>0:
					bit["_Retranslate"] = retOp
				choice.append(bit)
			if len(origA)>0:
				cn = charName
				if origA.startswith("STATUS:"):
					cn = "STATUS"
					origA = origA.replace("STATUS:","").strip()
				bit = {cn: origA}
				if len(japA)>0:
					bit["_Japanese"] = cleanJapanese(japA)
				if len(retA)>0:
					bit["_Retranslate"] = retA				
				choice.append(bit)
			if len(choice)>0:
				choices.append(choice)
		if len(choices)>0:
			outx.append({"CHOICE":choices})
			
		# Extra lines
		if len(q["OrigNext"])>0:
			bit = {charName:q["OrigNext"]}
			if len(q["JapNext"])>0:
				bit["_Japanese"] = cleanJapanese(q["JapNext"])
			if len(q["RetNext"])>0:
				bit["_Retranslate"] = q["RetNext"]
			outx.append(bit)
		return(outx)
		
		
	
	out2 = []
	for line in out:
		charName = [x for x in line.keys() if not x.startswith("_")][0]
		origD = line[charName]
		if origD in qSlices:
			qSlice = qSlices[origD]
			toAdd = []
			if qSlice["OrigQuestion"].startswith("["):
				# literal json string
				toAdd = json.loads(qSlice["OrigQuestion"])
			else:
				toAdd = makeQuestion(charName,qSlice)
			if len(toAdd)>0:
				charNameX = [x for x in toAdd[0] if not x.startswith("_")][0]
				if len(toAdd[0][charNameX])>0:
					out2 += toAdd
		else:
			# TODO: Take out #, check if there's any text left	
			newBit = {}
			for k in line:
				# QUESTION SPLITTER:
				#dlg = line[k] # Swap these two lines to see matching for 
				dlg = re.sub(" +"," ",line[k].replace("Â","").replace("#"," ")).strip()
				if len(dlg)>0:
					newBit[k] = dlg
			if len(newBit)>0:
				charNameX = [x for x in newBit if not x.startswith("_")]
				# If there's no character
				if len(charNameX)==0:
					newBit["unused"] = "()"
					charNameX = "unused"
				else:
					charNameX = charNameX[0]
				# If it's still got content, add it:
				if isinstance(newBit[charNameX],str):
					if len(newBit[charNameX])>0:					
						out2.append(newBit)
				else:
					out2.append(newBit)
		

	return(out2)
