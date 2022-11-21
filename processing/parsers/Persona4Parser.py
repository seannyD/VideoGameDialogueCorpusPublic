from bs4 import BeautifulSoup
import json, re, time, os
import xlsxwriter
from io import BytesIO
from urllib.request import urlopen


def cleanLine(txt):
	# don't include player input options
	txt = txt.strip()
	txt = txt.replace("…", " ... ")
	txt = txt.replace("“",'"')
	txt = txt.replace("”",'"')
	# e.g. ["chuckle","sigh","gasp","snrk","yip"]:
	txt = re.sub("\*([A-Za-z]+) ?\*","(\\1)",txt)
	txt = txt.replace('*cough cough*',"(cough cough)")
	txt = txt.replace('*munch munch*',"(munch munch)")
	return(txt)
	
	
def cleanName(name):
	name = name.replace("_"," ")
	return(name)


def parseFile(fileName,parameters={},asJSON=False):

	p5Characters = [
			"Igor",
			"Margaret",
			"Marie",
			"Protagonist",
			"Protag",
			"Yu Narukami"
			"Yosuke Hanamura",
			"Chie Satonaka",
			"Yukiko Amagi",
			"Kanji Tatsumi",
			"Rise Kujikawa",
			"Teddie",
			"Naoto Shirogane",
			"Ryotaro Dojima",
			"Inaba",
			"Ryotaro",
			"Nanako",
			"Tohru Adachi",
			"Taro Namatame",
			"Mitsuo Kubo",
			"Sayoko Uehara",
			"Shu Nakajima",
			"Eri",
			"Yuuta",
			"Kinshiro Morooka",
			"Noriko Kashiwagi",
			"Saki",
			"Hanako Ohtani",
			"Ai Ebihara",
			"Kou Ichijo",
			"Daisuke Nagase",
			"Ayane Matsunaga",
			"Yumi Ozawa",
			"Naoki",
			"Kondo",
			"Yamada",
			"Hosoi",
			"Kimiko Sofue",
			"Queen Tut",
			"Nakayama",
			"Shiroku",
			"Daidara",
			"Fox",
			"Hisano Kuroda",
			"Mumon",
			"Reiko Osa"
			"Mayumi Yamano",
			"Misuzu Hiiragi",
			"Edogawa",
			"Chihiro Fushimi"]
					
	p5CharClues = {}
	for char in p5Characters:
		for x in char.split(" "):
			p5CharClues[x] = char
			
	def getCharFromImage(url):
		imageURL = baseURL + updateURL + url
		url2 = re.sub("[0-9]","",url)
		parts = []
		current = ""
		for letter in url2:
			if letter.isupper() or letter=="_" or letter == "-" or letter == ".":
				if len(current)>0:
					parts.append(current.strip())
					current = ""
			current+=letter
		
		shadowSelf = "Shadow" in parts	
		for part in parts:
			if part in p5CharClues:
				charName = p5CharClues[part]
				if shadowSelf:
					charName = "Shadow "+charName
				return(charName)
				
		return(imageURL)


	o = open(fileName)
	d = o.read()
	o.close()
	
	baseURL = "https://lparchive.org/Persona-4/"
	updateURL = d[:d.index("\n")]
	d = d[d.index("\n")+1:]
	
	#d = d.replace("<i>","*").replace("</i>","*")
	
	soup = BeautifulSoup(d,'html.parser')
	script = soup.find("div")
	
	# Divide into lines
	lines = []
	currentLineParts = []
	for child in script.children:
		if child.name=="br":
			if len(currentLineParts)>0:
				lines.append(currentLineParts)
				currentLineParts = []
		else:
			if len(str(child).strip()) >0:
				currentLineParts.append(child)
	

	# Parse lines
	out = []
	prevChar = ""
	for line in lines:
		if len(line)==1:
			if line[0].name == "img":
				# single image
				url = baseURL+updateURL+line[0]["src"]
				out.append({"ACTION":url})
			elif line[0].name == "h3" or line[0].name == "i" or line[0].name=="b":
				out.append({"ACTION":line[0].getText().strip()})
				prevChar = "ACTION"
			elif line[0].name == "a":
				pass
			elif line[0].strip().startswith(">"):
				out.append({"ACTION":line[0].getText().strip()[1:]})
			else:
				# dialogue leftover
				out.append({prevChar: cleanLine(line[0].getText().strip())})
		else:
			if line[0].name== "img" and line[1].name != "img":
				# char pic followed by line of dialogue
				charName = getCharFromImage(line[0]["src"])
				prevChar = charName
				line = line[1:]
				#out.append({charName: cleanLine(line[1].getText())})
			elif line[0].name == "b":
				if line[0].getText().strip().endswith(":"):
					prevChar = line[0].getText().strip()[:-1]
					line = line[1:]
					
			for spokenBit in line:
				if spokenBit.name == "h3" or spokenBit.name == "b":
					out.append({"ACTION":spokenBit.getText().strip()})
					prevChar = "ACTION"
				elif spokenBit.name == "img":
					# Two people speaking at the same time
					charName = getCharFromImage(spokenBit["src"])
					prevChar += " and " + charName
				elif spokenBit.name == "i":
					out.append({"ACTION":spokenBit.getText().strip()})
				elif spokenBit.strip().startswith(">"):
					out.append({"ACTION":spokenBit[1:].strip()})
				else:
					out.append({prevChar: cleanLine(spokenBit)})

				
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)
	
	
def postProcessing(out):
	# Build directory of imageNames
	
	makeExcelDirectory = False
	
	folder = "../data/Persona/Persona4"
	
	with open(folder+"/meta.json") as json_file:
		meta = json.load(json_file)
	codedChars = meta["characterGroups"]["male"] + meta["characterGroups"]["female"] + meta["characterGroups"]["neutral"]
	
	codedChars += list(meta["aliases"].keys())
	
	out2 = []
	p5CharDirectory = {}
	for line in out:
		charName = [x for x in line.keys() if not x.startswith("_")][0]
		if charName.startswith("http"):
			imageName = charName[charName.rindex("/")+1:]
			imageName = re.sub("^[0-9]+\-","",imageName).replace(".jpg","").replace(".png","")
			imageName = imageName.replace("-"," ").replace("_"," ")
			if not imageName in p5CharDirectory:
				if not imageName in codedChars:
					p5CharDirectory[imageName] = charName
			out2.append({imageName:line[charName]})
		else:
			out2.append(line)

	if makeExcelDirectory:
		# Create an new Excel file and add a worksheet.
		workbook = xlsxwriter.Workbook(folder+"/"+"charDirectory.xlsx")
		worksheet = workbook.add_worksheet()
		worksheet.write("A1","Name")
		worksheet.write("B1","Image")
		worksheet.write("B1","Gender")
	
		rowNum = 2
		print("Dowloading " + str(len(p5CharDirectory)) +" images ...")
		for imageName in list(p5CharDirectory.keys()):
			print(" - "+imageName)
			imageURL = p5CharDirectory[imageName]
			saveFile = folder + "/raw/"+imageURL[imageURL.rindex("/")+1:]
			if not os.path.exists(saveFile):
				try:
					webdata = urlopen(imageURL).read()
					time.sleep(1)
					image_data = BytesIO(webdata)
					with open(saveFile,'wb') as saveF:
						saveF.write(webdata)
				except:
					print("Error downloading "+imageURL)
			else:
				image_data = open(saveFile,'rb').read()
				image_data = BytesIO(image_data)
			worksheet.write('A'+str(rowNum), imageName)
			worksheet.insert_image('B'+str(rowNum), imageURL, {'image_data': image_data})
			worksheet.set_row_pixels(rowNum-1, 100)
			rowNum += 1
		
		workbook.close()
	
	return(out2)