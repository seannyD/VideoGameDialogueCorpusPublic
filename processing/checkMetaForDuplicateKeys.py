import json,os,sys

def dict_raise_on_duplicates(ordered_pairs):
	"""Reject duplicate keys."""
	d = {}
	for k, v in ordered_pairs:
		if k in d:
			print("    duplicate key: %r" % (k,))
		else:
			d[k] = v
	return d

folders = [root+os.sep for root,dirs,files in os.walk("../data/") if "meta.json" in files]
# Allow parsing of just one game
if len(sys.argv)>1:
	fx = sys.argv[-1]
	if not fx.endswith(os.sep):
		fx += os.sep
	folders = [fx]

for folder in folders:
	print(folder)
	with open(folder+"meta.json") as json_file:
		json.load(json_file, object_pairs_hook=dict_raise_on_duplicates)



