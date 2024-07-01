import os,json,shutil

####
# Copy data to a minimal folder (not part of public repository)
if os.path.isdir("../data_min"):
	folders = [root+os.sep for root,dirs,files in os.walk("../data/") if "meta.json" in files]
	for folder in folders:
		with open(folder+"meta.json") as json_file:
			meta = json.load(json_file)
		superseded = False
		if "status" in meta:
			superseded = meta["status"]=="superseded"
		if not superseded and os.path.isfile(folder+"data.json"):
			dest = folder.replace("../data/","../data_min/")
			os.makedirs(dest, exist_ok=True)
			shutil.copyfile(folder+"meta.json", dest+"meta.json")
			shutil.copyfile(folder+"data.json", dest+"data.json")