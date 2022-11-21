from bs4 import BeautifulSoup
import json, re, time, os
import xlsxwriter
from io import BytesIO
from urllib.request import urlopen


# TODO
# ACTION with ":" is being parsed as dialogue.
#  Need to make exceptions list

def cleanLine(txt):
	# don't include player input options
	txt = txt.strip()
	txt = txt.replace("…", " ... ")
	txt = txt.replace("“",'"')
	txt = txt.replace("”",'"')
	txt = re.sub("\*([A-Za-z ]+) ?\*","(\\1)",txt)
	txt = txt.replace("*","")
	#if txt.startswith(">"):
	#	txt = txt[1:].strip()
	return(txt)
	
	
def cleanName(name):
	name = name.replace("_"," ")
	return(name)


def parseFile(fileName,parameters={},asJSON=False):

	p5Characters = ["Protagonist",
					"Protag",
					"Morgana",
					"Ryuji Sakamoto",
					"Ann Takamaki",
					"Yusuke Kitagawa",
					"Makoto Niijima",
					"Queen",
					"Skull",
					"Panther",
					"Mona",
					"Fox",
					"Navi",
					"Noir",
					"Oracle",
					"Futaba Sakura",
					"Haru Okumura",
					"Goro Akechi",
					"Sumire Yoshizawa",
					"Igor",
					"Sojiro Sakura",
					"Chihaya Mifune",
					"Caroline",
					"Justine",
					"Munehisa Iwai",
					"Tae Takemi",
					"Sadayo Kawakami",
					"Ichiko Ohya",
					"Shinya Oda",
					"Hifumi Togo",
					"Yuuki Mishima",
					"Toranosuke Yoshida",
					"Sae Niijima",
					"Takuto Maruki",
					"Kobayakawa",
					"Hiruta",
					"Inui",
					"Ushimaru",
					"Chouno",
					"Usami",
					"Shiho Suzui",
					"Suguru Kamoshida",
					"Ichiryusai Madarame",
					"Junya Kaneshiro",
					"Kunikazu Okumura",
					"Black Mask",
					"Masayoshi Shido",
					"Yaldabaoth",
					"Dreamer",
					"SIU Director",
					"Wakaba Isshiki",
					"Jose",
					"Natsuhiko Nakanohara",
					"Mika",
					"Sugimura",
					"President Tanaka",
					"Shinichi",
					"Coach Hiraguchi",
					"Kasumi",
					"Shibusawa",
					"Rumi",
					"Akio Kawanabe",
					"Angel",
					"Julian",
					"Eiko Takao",
					"Hansaki",
					"Lala Escargot",
					"Nakaoka",
					"Takeishi",
					"Tsukasa",
					"Takekuma",
					"Yamauchi",
					"Ooe",
					"Former noble"]
					
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
					parts.append(current)
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
	
	baseURL = "https://lparchive.org/Persona-5/"
	updateURL = d[:d.index("\n")]
	d = d[d.index("\n")+1:]
	
	#d = d.replace("<i>","*").replace("</i>","*")
	
	r1 = """<img alt="" border="0" class="img" src="132-TV.jpg"/> The correct answer is… B! If you drive someone crazy with noise, that’s bodily harm! If it disrupts the body’s functions, it counts as bodily harm, even if there’s no physical contact! Hair grows back, so it doesn’t count as a wound. That’d be a case of “assault,” not bodily harm.<br/>"""
	r2 = """<img alt="" border="0" class="img" src="132-Game Show Host.jpg"/> The correct answer is… B! If you drive someone crazy with noise, that’s bodily harm!<br/><br/>
<img alt="Lawyer on Game Show" src="Lawyer on Game Show"/>If it disrupts the body’s functions, it counts as bodily harm, even if there’s no physical contact! Hair grows back, so it doesn’t count as a wound. That’d be a case of “assault,” not bodily harm.<br/>"""

	d = d.replace(r1,r2)
	
	#d = d.replace("Anon:","<br/><br/>Anon:")

	# Bold stuff doesn't have info, and complicates the parsing
	# so remove	
	d = d.replace("<b>","")
	d = d.replace("</b>","")
	
	removeColons = [
		"So, lesson learned:",
		"So, to recap:",
		"Just a heads up:",
		"Two things here:",
		"Translation:",
		"Also worth noting:",
		"Spoiler:",
		"Reminder:",
		"Our strategy:",
		"Or alternatively:",
		"Or, and hear me out:",
		"Note:",
		"Neat little detail:",
		"In other words:",
		"It reads:",
		"Fun detail:",
		"Fun detail here:",
		"Fun fact:",
		"Funny detail here:",
		"For real, though:",
		"ChaosArgate posted:",
		"Cool detail here:",
		"Also:",
		"Also great:",
		"Also worth noting:",
		"(edit:",
		"A few things here:",
		"Addendum I:",
		"Addendum II:",
		"Boss\":",
		"Miniboss:",
		"Music:",
		"Worth noting:",
		"Question 1:"
	]
	
	for rex in removeColons:
		d = d.replace(rex,rex.replace(":","-"))
	
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
	out = [{"ACTION": "FILE: "+fileName}]
	for line in lines:
		if len(line)==1:
			if line[0].name == "img":
				# single image
				url = baseURL+updateURL+line[0]["src"]
				out.append({"ACTION":url})
			elif line[0].name == "h3":
				out.append({"ACTION":line[0].getText().strip()})
			else:
				# comment
				txx = line[0].getText().strip()
				if txx[:-2].count(":")==1 and txx.index(":")<20:
					charName,dlg = txx.split(":",1)
					out.append({charName: cleanLine(dlg)})  #xx
				else:
					out.append({"ACTION":txx})
		else:
			if line[0].name== "img" and line[1].name != "img":
				# char pic followed by line of dialogue
				charName = getCharFromImage(line[0]["src"])
				# Underlined text is joke content from the transcriber
				if line[1].name=="u":
					out.append({"COMMENT": charName+": "+cleanLine(line[1].getText())})
				else:
					out.append({charName: cleanLine(line[1].getText())})  #xx
			else:
				# Random text like titles, music, and commentary
				out.append({"ACTION":cleanLine("".join([x.getText() for x in line]))})
				
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)
	
	
def postProcessing(out):
	# Build directory of imageNames
	
	folder = "../data/Persona/Persona5B"
	
	with open(folder+"/meta.json") as json_file:
		meta = json.load(json_file)
	codedChars = meta["characterGroups"]["male"] + meta["characterGroups"]["female"] + meta["characterGroups"]["neutral"]
	
	codedChars += list(meta["aliases"].keys())
	
	
	def splitPlayerChoices(charName,dlg):
		# if isinstance(line[charName],str) and charName!="ACTION":
		if (dlg.count("/>")>0 or dlg.startswith(">")) and charName!="ACTION":
			# Player choices.
			bits = dlg.split('/')
			mainBit = [x for x in bits if x.startswith(">")][0]
			bits = [x.replace(">","").strip() for x in bits]
			mainBit = mainBit.replace(">","").strip()
			bits.remove(mainBit)
			return({charName:mainBit, "_AltOptions": "; ".join(bits)})
		else:
			return({charName:dlg})
	
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
			out2.append(splitPlayerChoices(imageName,line[charName]))
		else:
			out2.append(splitPlayerChoices(charName,line[charName]))


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
			webdata = urlopen(imageURL).read()
			time.sleep(1)
			image_data = BytesIO(webdata)
			with open(saveFile,'wb') as saveF:
				saveF.write(webdata)
		else:
			image_data = open(saveFile,'rb').read()
			image_data = BytesIO(image_data)
		worksheet.write('A'+str(rowNum), imageName)
		worksheet.insert_image('B'+str(rowNum), imageURL, {'image_data': image_data})
		worksheet.set_row_pixels(rowNum-1, 100)
		rowNum += 1
		
	workbook.close()
	
	# Fix alt choices (there are no choice structures at this point)
	out3 = []
	i = 0
	while i < len(out2):
		line = out2[i]
		if "_AltOptions" in line:
			k = [x for x in line.keys() if not x.startswith("_")][0]
			altOp = [x.strip() for x in line["_AltOptions"].split(";") if len(x.strip())>0]
			if len(altOp)>0:
				ops = [line] + [{k:l2} for l2 in altOp]
				# assume next line is direct response
				choices = [[x] for x in ops]
				choices[0].append(out2[i+1])
				out3.append({"CHOICE":choices})
				# skip next line
				i += 1
			else:
				out3.append(line)				
		else:
			out3.append(line)
		i += 1
		
	for i in range(len(out3)):
		line = out3[i]
		if line == {"Aki": "Anon: I’ve been waiting for this"}:
			out3[i] = {"Anon": "I’ve been waiting for this"}
		elif line == {"ACTION": "Man who cannot sing or act voice: (singing) It was him! He stole the silverware! He even stole the candlesticks! Thief! Confess your criiiime!"}:
			out3[i] = {"Man who cannot sing or act voice" : "(singing) It was him! He stole the silverware! He even stole the candlesticks! Thief! Confess your criiiime!"}
	
	return(out3)