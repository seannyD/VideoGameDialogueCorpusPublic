import sys, time, json, re, os
from urllib.request import urlopen
from bs4 import BeautifulSoup


def findAttribute(characterName,attributName):
	page = urlopen(baseWiki+character).read().decode('utf-8')
	soup = BeautifulSoup(page, 'html.parser')
	attribute = soup.find('div', attrs={"data-source": attributName})
	return(	attribute.find("div").getText())


folder = ""
if len(sys.argv)>1:
	folder = sys.argv[-1]
	if not folder.endswith(os.sep):
		folder += os.sep
else:
	print("No game folder specified")
	exit(1)


with open(folder+"meta.json") as json_file:
	meta = json.load(json_file)	
	
baseWiki = meta["characterInfoSource"]

with open(folder+"characters.txt") as f:
	charList = f.read()
	
charList = re.sub(":[0-9]+","",charList)

characters = eval("["+charList+"]")
print(characters)

alreadyProcessedCharacters = ["ACTION","NARRATIVE","LOCATION",'Girl','Boy',"Woman","Man","Person"]
for k in meta["characterGroups"].keys():
	alreadyProcessedCharacters += meta["characterGroups"][k]

print(alreadyProcessedCharacters)

genders = {}
for character in characters:
	gender = "unclassified"
	if not character in alreadyProcessedCharacters:
		if not re.search("[0-9]",character):
			# Don't look up names with numbers in
			print("Searching for\t"+character, end="")
			try:
				gender = findAttribute(character, "gender")
				print("\t"+gender)
			except:
				pass
			time.sleep(2)
			print("")
	try:
		genders[gender].append(character)
	except:
		genders[gender] = [character]


print(genders)
	
json_data = json.dumps(genders, indent = 4)
json_data = re.sub('{\n\t+','{',json_data)
json_data = re.sub('\n\t+}','}',json_data)
json_data = re.sub('\n\t+]',']',json_data)
o = open(folder+"autoCharInfo.json",'w')
o.write(json_data)
o.close()