from urllib.request import *
from bs4 import BeautifulSoup
import json,re,os,time,sys


skipDownloads = False
if "-s" in sys.argv:
	skipDownloads = True


nameToLinkEdits = {
	"Falkbryda": "/wiki/Falkbryda",
	"Arrivals Attendant": "/wiki/Arrivals_Attendant_(Gridania)"
	#"Arrivals Attendant": "wiki/Arrivals_Attendant_(Limsa_Lominsa)"
}



def loadPage(page):
	req = Request(
		page, 
		data=None, 
		headers={
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
		}
	)

	html = urlopen(req).read().decode('utf-8')
	return(html)

# list of (name,link) tuples
allNPCs = []

if not skipDownloads:

	print("\n\nIdentifying NPCs in raw files")
	for fileName in [x for x in os.listdir("raw") if x.endswith(".html")]:
		o = open("raw/"+fileName)
		d = o.read()
		o.close()
		if len(d)>2:
			# Pages are already cut to "Dialogue" div	
			soup = BeautifulSoup(d,'html5lib')
			# TODO: Check there is a dialogue section
			interactions = soup.find("div",{"title":"Interactions"})
			if not interactions is None:
				trs = interactions.find("table").find("tbody").find("td",{"colspan":"2"},recursive=True)
				npcs = trs.find_all("a",recursive=True)
				allNPCs += [(a["title"],a["href"]) for a in npcs]
				for a in npcs:
					if a["title"].strip() in nameToLinkEdits:
						allNPCs.append((a["title"], nameToLinkEdits[a["title"].strip()]))
					else:
						allNPCs.append((a["title"].strip(), a["href"]))
			
	allNPCs = list(set(allNPCs))

	# Make sure "raw/npcs/" is a folder
	if not os.path.isdir("raw/npcs"):
		os.mkdir("raw/npcs")

	base = "https://ffxiv.gamerescape.com"


	def donwloadNPCPage(name,link):
		print(name + ": "+ link)
		page = None
		try:
			page = loadPage(base+link)
		except:
			print("    Can't load page "+link)
		time.sleep(2)
		if not page is None:
			soup = BeautifulSoup(page,'html5lib')
			app = soup.find("div",{"title":"Appearances"},recursive=True)
			if app is None:
				app = soup.find("div",{"title":"Appearance"},recursive=True)
			if not app is None:
				app1 = app.find("div",{"title":"1"},recursive=True)
				print("    SUCCESS")
			else:
				print("    Can't find data for "+name+ ": "+link)
				app1 = ""
			#  save to raw/npcs
		else:
			app1 = ""
		o = open(fn,'w')
		o.write(str(app1))
		o.close()


	print("\n\nDownloading NPC pages")
	print(len(allNPCs))
	# Download pages that are still needed
	#  (from raw html links)
	for name,link in allNPCs:
		fn = "raw/npcs/"+name+".html"
		if not os.path.exists(fn):
			donwloadNPCPage(name,link)

	# TODO: Get list of NPC names from the data.json file
	with open("data.json") as json_file:
		data = json.load(json_file)	

	def get_keys_recursively(var):
		if not isinstance(var,str) and (not isinstance(var,int)):
			for k in var:
				if isinstance(var, dict):
					if not k.startswith("_"):
						yield k
					v = var[k]
					for result in get_keys_recursively(v):
						yield result
				elif isinstance(var, list):
					for result in get_keys_recursively(k):
						yield result
					
	dataKeys = [x for x in get_keys_recursively(data["text"])]
	dataKeys = list(set(dataKeys))
	dataKeys = [x for x in dataKeys if not x in allNPCs]

	for key in dataKeys:
		fn = "raw/npcs/"+key+".html"
		link = "/wiki/"+key.replace(" ","_")
		if not os.path.exists(fn):
			donwloadNPCPage(key,link)
# ----
# End of skip downloading

def findWeaponTag(soup):
	for td in soup.find_all("td",recursive=True):
		if td.text.strip().count("Weapon/Tools/Shield")>0:
			return(td)
	return(None)

print("\n\nParsing")
# Parse raw/npcs files
npcFiles = os.listdir("raw/npcs/")
npcFiles = [x for x in npcFiles if x.endswith(".html")]
charProperties = []
for f in npcFiles:
	print(f)
	o = open("raw/npcs/"+f)
	d = o.read()
	o.close()
	
	if len(d)>4:
		scriptName = f.replace(".html","")
		#fullName = 
		props = {"Name":scriptName}

		skinColour = ""
		skinColourSearch = re.search('Skin Color: (#.{6})', d)
		if skinColourSearch:
			skinColour = skinColourSearch.group(1)
		props["Skin Color"] = skinColour
	
		hairColour = ""
		hairColourSearch = re.search('Hair Color: (#.{6})', d)
		if hairColourSearch:
			hairColour = hairColourSearch.group(1)
		props["Hair Color"] = hairColour

		soup = BeautifulSoup(d,'html5lib')
		t = soup.find("table",recursive=True)
		t = t.find("table",recursive=True)
		rows = t.find_all("tr",recursive=True)
		
		for row in rows:
			bits = row.find_all("td")
			if len(bits)==2:
				prop = bits[0].getText().strip()
				value = bits[1]
				if value.name == "div" or value.name == "img":
					pass
				else:
					value = value.getText()
				value = value.replace("Option","").strip()
				props[prop]=value
		
		# Weapons
		weapons = []
		weaponTag = findWeaponTag(soup)
		if not weaponTag is None:
			weapons = [x["title"] for x in weaponTag.find_all("a",recursive=True) if not x["title"] is None]
			
		# Extra equipment and features
		extras = []
		bits = soup.find_all(["a"],recursive=True)
		for bit in bits:
			btitle = bit["title"]
			if btitle is not None:
				if btitle.count(":")>0:
					key,value = btitle.split(":")
					print(key,value)
					if not key.strip() in props:
						props[key.strip()] = value.strip()
				elif not btitle in weapons:
					extras.append(btitle)
		
		props["weapons"] = " / ".join(weapons)
		props["extras"] = " / ".join(extras)
		
		charProperties.append(props)

# Make csv output
allHeaders = []
for char in charProperties:
	for k in char:
		if not k in allHeaders:
			allHeaders.append(k)

# Put name and gender first
allHeaders.remove("Name")
allHeaders.remove("Gender")
allHeaders = ["Name","Gender"]+allHeaders

csv = ",".join(allHeaders)+"\n"
out = [allHeaders]
for char in charProperties:
	row = []
	for prop in allHeaders:
		if prop in char:
			row.append(char[prop])
		else:
			row.append("NA")
	out.append(row)
	
import csv
with open('charProperties.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    for row in out:
    	writer.writerow(row)

# Make json output
genders = {}
for char in charProperties:
	g = char["Gender"].lower()
	charName = char["Name"]
	if not g in genders:
		genders[g] = []
	genders[g].append(charName)
	
o = open("autoGender_wiki.json",'w')
o.write(json.dumps(genders, indent = 4))
o.close()