import json,re,os

def parseFile(fileName,parameters={},asJSON=False):

	def cleanAction(txt):
		return(txt)

	def cleanDialogue(txt):
		txt = txt.replace("\n"," ")
		txt = re.sub(" +"," ",txt)
		return(txt)
	

	
	o = open(fileName)
	d = o.read()
	o.close()
	
	spk = "X"
	dlg = ""
	
	out = [{"LOCATION":fileName}]
	for line in [x for x in d.split("\n") if len(x.strip())>0]:
		if line.strip().startswith(">>"):
			if len(dlg)>0:
				out.append({spk: cleanDialogue(dlg)})
				dlg = ""
			spk = line.replace(">>","").strip()
		elif not line[0] in ["0","1","2","3","4","5","6","7","8","9"]:
			dlg += line.strip() + " "
	# Flush	
	if len(dlg)>0:
		out.append({spk: cleanDialogue(dlg)})
			
	
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)
	
	
