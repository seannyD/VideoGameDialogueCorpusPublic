import json


def parseFile(fileName,parameters={},asJSON=False):
		
	jx = json.loads(open(fileName).read())
	out = jx["text"]

	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)
	


	


	

	

	
	



