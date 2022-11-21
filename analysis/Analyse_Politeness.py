import convokit, os, json

from convokit import Corpus, download, TextParser, PolitenessStrategies, Classifier
import pandas as pd

miniSampleSize = 1000

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

allFolders = [root+os.sep for root,dirs,files in os.walk("../data/") if "meta.json" in files]
#allFolders = [allFolders[0]]

textsF = []
speakerF = []
conversation_idF = []

textsM = []
speakerM = []
conversation_idM = []

textsFMini = []
speakerFMini = []
conversation_idFMini = []
textsMMini = []
speakerMMini = []
conversation_idMMini = []

print("  Loading texts ...")

for folder in allFolders:
	with open(folder+"meta.json") as json_file:
		meta = json.load(json_file)
	with open(folder+"data.json") as json_file:
		d = json.load(json_file)["text"]

	alternativeMeasure = False
	if "alternativeMeasure" in meta:
		alternativeMeasure = meta["alternativeMeasure"]			
	
	miniDat = []
	if not alternativeMeasure:
		bits = getAllCharacterTexts(d,getNames=True)
		for charName, txt in bits:
			if charName in meta["characterGroups"]["male"]:
				textsM.append(txt)
				speakerM.append(charName)
				conversation_idM.append(folder)
				miniDat.append((txt,charName,folder,"male"))
			if charName in meta["characterGroups"]["female"]:
				textsF.append(txt)
				speakerF.append(charName)
				conversation_idF.append(folder)
				miniDat.append((txt,charName,folder,"female"))

		if len(miniDat)>=miniSampleSize:
			for i in range(miniSampleSize):
				txt,cx,idx,gender = miniDat[i]
				if gender == "female":
					textsFMini.append(txt)
					speakerFMini.append(cx)
					conversation_idFMini.append(idx)
				else:
					textsMMini.append(txt)
					speakerMMini.append(cx)
					conversation_idMMini.append(idx)


def toCorpus(dic):
	utt_df = pd.DataFrame.from_dict(dic)
	utt_df["timestamp"] = range(len(dic["text"]))
	utt_df["reply_to"] = " "
	simple_utt_df = utt_df[['timestamp', 'text', 'speaker', 'reply_to', 'conversation_id']]
	ids = list(simple_utt_df.index)
	simple_utt_df = simple_utt_df.reset_index()
	simple_utt_df['id'] = ids
	cx = Corpus.from_pandas(simple_utt_df)
	return(cx)

def getPoliteness(dF,group):
	print("Converting "+ group + " ...")
	corpusF = toCorpus(dF)
	parser = TextParser(verbosity=10000)
	corpusF = parser.transform(corpusF)
	#corpusF.print_summary_stats()

	print("\n\nTagging "+ group + " ...")
	ps = PolitenessStrategies()
	ps.transform(corpusF, markers=True)
	#data = ps.summarize(corpusF, plot=False)#, y_lim = 1.6)
	#print(data)

	polDataF = {}
	for utt in corpusF.iter_utterances():
		for ((k,v),(k1,v2)) in zip(utt.meta["politeness_strategies"].items(),utt.meta["politeness_markers"].items()):
			feature = k[21:len(k)-2]
			n = len(v2)
			if not feature in polDataF:
				polDataF[feature] = 0
			polDataF[feature] += n

	FnumUtterances = len(corpusF.utterances)

	outx = ""
	for feature in polDataF:
		outx += group + "," + feature + "," + str(polDataF[feature]) + "," + str(FnumUtterances) +"\n"
	return(outx)

dF = {
	"text": textsF,
	"speaker": speakerF,
	"conversation_id": conversation_idF
}

dM = {
	"text": textsM,
	"speaker": speakerM,
	"conversation_id": conversation_idM
}

out = "group,feature,count,total\n"
#out += getPoliteness(dF,"female")+"\n"
#out += getPoliteness(dM,"male")

#with open("../results/politeness.csv",'w') as f:
#	f.write(out)
	
print("Running analysis on mini corpus")

dFMini = {
	"text": textsFMini,
	"speaker": speakerFMini,
	"conversation_id": conversation_idFMini
}

dMMini = {
	"text": textsMMini,
	"speaker": speakerMMini,
	"conversation_id": conversation_idMMini
}

outMini = "group,feature,count,total\n"
outMini += getPoliteness(dFMini,"female")+"\n"
outMini += getPoliteness(dMMini,"male")

with open("../results/politenessMini.csv",'w') as f:
	f.write(outMini)