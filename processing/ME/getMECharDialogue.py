import json,csv
from textatistic import word_array

with open("../../data/MassEffect/MassEffect1B/data.json") as json_file:
	ME1lines = json.load(json_file)["text"]
with open("../../data/MassEffect/MassEffect2/data.json") as json_file:
	ME2lines = json.load(json_file)["text"]
with open("../../data/MassEffect/MassEffect3C/data.json") as json_file:
	ME3lines = json.load(json_file)["text"]
	

def getTextByCue(lines,cues,speakers=[]):
	if isinstance(lines,dict):
		mainKey = [x for x in lines if not x.startswith("_")][0]
		mainVal = lines[mainKey]
		if isinstance(mainVal,str):
			if len(speakers)==0 or mainKey in speakers:
				mainVal = mainVal.lower()
				# If there are no cues, return the line
				if len(cues)==0:
					yield lines
				# Check if cue appears anywhere
				elif any([mainVal.count(cue)>0 for cue in cues]):
					# Check if cue is a word
					tokens = word_array(mainVal)
					if any([cue in tokens for cue in cues]):
						yield lines
		else:
			for result in getTextByCue(mainVal,cues,speakers):
				yield result
	elif isinstance(lines,list):
		for line in lines:
			for result in getTextByCue(line,cues,speakers):
				yield result

def writeToCSV(lines,fileName):
	with open(fileName, 'w') as csvfile:
		csvwriter = csv.writer(csvfile)
		csvwriter.writerow(["ID","speaker","line"])
		for line in lines:
			mainKey = [x for x in line if not x.startswith("_")][0]
			idx = ""
			if "_ID" in line:
				idx = line["_ID"]
			dialogue = line[mainKey]
			dialogue = dialogue.replace('"','""')
			csvwriter.writerow([idx,mainKey,dialogue])

def getCues(cues,speakers, filePrefix):
	writeToCSV(getTextByCue(ME1lines, cues,speakers),filePrefix+"_ME1.csv")
	writeToCSV(getTextByCue(ME2lines, cues,speakers),filePrefix+"_ME2.csv")
	writeToCSV(getTextByCue(ME3lines, cues,speakers),filePrefix+"_ME3.csv")

# cues should be lowercase
getCues(["benezia"],[],"../../results/doNotShare/ME/Antagonists/Antagonists_BeneziaAbout")
getCues([],["Matriarch Benezia"],"../../results/doNotShare/ME/Antagonists/Antagonists_BeneziaSpeech")
getCues(["mother"],["Liara T'Soni"], "../../results/doNotShare/ME/Antagonists/Antagonists_BeneziaLiaraMother")

getCues(["aria"],[],"../../results/doNotShare/ME/Antagonists/Antagonists_AriaAbout")
getCues([],["Aria T'Loak"],"../../results/doNotShare/ME/Antagonists/Antagonists_AriaSpeech")

getCues([],["Tali'Zorah"],"../../results/doNotShare/ME/SocialRoleTheory/Antagonists_TaliSpeech")
getCues([],["Jack"],"../../results/doNotShare/ME/SocialRoleTheory/Antagonists_JackSpeech")


# Intro ME2: BioD_OmgHub_225Aria_LOC_INT.pcc: omghub_asari_ruler_d_dlg