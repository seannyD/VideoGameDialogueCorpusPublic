from bs4 import BeautifulSoup, NavigableString, Tag
import json, re, csv
import bs4
from urllib.request import urlopen

unknownCount = 0
versperiaSeenURLS = []

def parseFile(fileName,parameters={},asJSON=False):

	global versperiaSeenURLS

	print(fileName)
	html = open(fileName, 'r')
	soup = BeautifulSoup(html, 'html5lib')
	
	scenario = soup.find("span",["scenario-selected"],recursive=True)
	if scenario is None:
		scenario = soup.find("div",["skit-name"],recursive=True)
	scenario = scenario.get_text().strip()
	
	
	# find url
	soup.find("a").extract()
	ukURL = soup.find("a")['href']
	url = ukURL.replace("360",'ps3p')
	url = url.replace("locale=uk","locale=jp")
	url = url.replace("compare=2","compare=c2")
	url = "https://hyouta.com/vesperia/" + url
	
	#print("\n\n\n")
	#print(scenario)
	
	storyBox = soup.find("div", {"class":"storyBox"}, recursive=True)
	storyLines = storyBox.find_all("div",{"class":"storyLine"})
	
	def parseStoryLine(storyLine):
		global unknownCount
		
		blockClassNames = ["storyBlock","skitBlock"]
		# Use class_ to match ANY of the classes in blockClassNames
		storyBlocks = storyLine.find_all("div",blockClassNames)

		JPData = parseStoryBlock(storyBlocks[0])
		EngData = parseStoryBlock(storyBlocks[1])
		
		charName = cleanName(EngData["charName"])
		if charName == "":
			charName = "UnknownChar"+str(unknownCount)
			unknownCount += 1
		line = {charName:cleanText(EngData["text"]),
				"_JChar":cleanName(JPData["charName"]), "_JText":cleanText(JPData["text"])}
		#print(line)
		return([line])
		
	
	def parseStoryBlock(storyBlock):

		charName = ""	
		blockClassNames = ["charaContainer","charaContainer1","charaContainer2","charaContainerSkit"]
		foundClass = ""
		systemTitle = ""
		for cname in blockClassNames:
			charContainer = storyBlock.find("div",{"class":cname}, recursive=True)
			if not charContainer is None:
				if cname in ["charaContainer1","charaContainer2"]:
					charName = "SYSTEM"
					systemTitle = charContainer.getText().strip()
				break

		if charName=="" and not charContainer is None:
			charName = charContainer.getText()
			
		if not charContainer is None:
			charContainer.extract()
		
		# replace images with names
		for img in storyBlock.find_all("img"):
			src = ""
			if "src" in img:
				src = img["src"]
				if "/" in src:
					src = src[src.rindex("/")+1:]
					src = src.replace(".png","")
			img.replace_with(src)
		
		dialogue = storyBlock.getText(" ")
		if len(systemTitle)>0 and charName == "SYSTEM":
			dialogue = systemTitle + ": " + dialogue.strip()
		return({"charName":charName,"text":dialogue})
	
	def cleanName(x):
		x = x.replace("  "," ")
		x = x.strip()
		return(x)
	
	def cleanText(x):
		x = x.strip()
		x = re.sub("\*(.+?)\*","(\\1)",x)
		x = x.replace("..."," ... ")
		x = re.sub(" +"," ",x)
		return(x)
		
	#####
	# Main loop
	
	out = []
	if fileName.count("page_Skit_10000")>0:
		out.append({"ACTION": "Skits"})
	elif fileName.count("page_20000")>0:
		out.append({"ACTION": "Sidequests"})
	
	# Check if we've already parsed this
	#  (some skits are included in the main quest list)
	#print(len(versperiaSeenURLS))
	if not url in versperiaSeenURLS:
		versperiaSeenURLS.append(url)
		out += [{"LOCATION":"Scenario: "+scenario},
			    {"LOCATION": url}]
		for storyLine in storyLines:
			bits = parseStoryLine(storyLine)
			if len(bits)>0:
				out += bits
	else:
		#print("Duplicate:" + scenario)
		pass

	
	if asJSON:
		return(json.dumps({"text":out}, indent = 4))
	return(out)
	

def postProcessing(out):

	# Add Skit Type
	# Load skit index page, which categorises the skits
	skitIndexFileName = "../data/Tales/TalesOfVesperia/raw/skitIndex.txt"
	skitIndexPage = open(skitIndexFileName).read()
	soup = BeautifulSoup( skitIndexPage, 'html5lib')

	# Build dictionary of ulr -> skit type
	skitTable = soup.find("div",{"id":"content"}).find("table").find("tbody")
	skitIndexInfo = {}
	for row in skitTable.find_all("tr"):
		trs = row.find_all("td")
		rowType = trs[0].get_text()
		href = trs[2].find("a")['href']
		href = href[href.index("&section"):]
		if not href in skitIndexInfo:
			skitIndexInfo[href] = rowType
			
	for line in out:
		if "LOCATION" in line and line["LOCATION"].count("&section=skit")>0:
			url = line["LOCATION"]
			url = url[url.index("&section"):]
			print(url)
			if url in skitIndexInfo:
				line["_skitType"] = skitIndexInfo[url]
	
	# Make table of characters to help gender coding
	writeCSV = False
	
	if writeCSV:
		unknownCsv = [["CharName","Line","LastNamedChar","LastButOneNamedChar","location"]]
		loc = ""
		prevChar = ""
		prevPrevChar = ""
		for line in out:
			k = [x for x in line if not x.startswith("_")][0]
			if k.startswith("Unknown"):
				unknownCsv.append([k,line[k],prevChar,prevPrevChar,loc])
			elif k == "LOCATION":
				if line[k].startswith("http"):
					loc = line[k]
					prevChar = ""
					prevPrevChar = ""
			elif not k.startswith("SYSTEM"):
				prevPrevChar = prevChar
				prevChar = k
	
		with open('../data/Tales/TalesOfVesperia/unknownCharacters.csv', 'w', encoding='UTF8') as f:
			writer = csv.writer(f)
			writer.writerows(unknownCsv)
	
	return(out)

# 
# def createNPCImageGallery():
# 	# Write gallery of NPCs
# 	print("Creating gallery of NPCs")
# 	gallery= "<html><body>"
# 	for npc in finalFantasy10WhoGallery:
# 		srcx =finalFantasy10WhoGallery[npc]
# 		if not srcx is None:
# 			srcx = srcx.replace("..?","../?")
# 			srcx = srcx[srcx.index("/")+1:]
# 			imageURL = "http://auronlu.istad.org/ffx-script/"
# 			if srcx.startswith("?"):
# 				imageURL += "index.html" + srcx
# 				attachmentHTML =  urlopen(imageURL).read().decode('utf-8')
# 				bits = re.findall("http://auronlu.istad.org/ffx-script/wp-content/uploads/.+?.jpg'",attachmentHTML)
# 				if len(bits)>0:
# 					imageURL = '<img src="'+ bits[0][:-1] + '" max-height="600">'
# 				else:
# 					imageURL = '<a href="' + imageURL +  '">LINK</a>'
# 				#<img width="98" height="300" src="http://auronlu.istad.org/ffx-script/wp-content/uploads/2015/08/5woman-glasses-98x300.jpg" class="attachment-medium size-medium" alt="Woman with Quistis glasses">
# 			else:
# 				imageURL += srcx
# 				imageURL = '<img src="'+ imageURL + '" max-height="600">'
# 			gallery += npc + "</br>" + imageURL + "</br></br>"
# 	gallery += "</body></html>"
# 	o = open("../data/FinalFantasy/FFX_B/NPC_Gallery.html",'w')
# 	o.write(gallery)
# 	o.close()


#def postProcessing(out):
#	return(out)
		