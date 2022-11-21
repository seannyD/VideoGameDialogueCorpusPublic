from urllib.request import *
from bs4 import BeautifulSoup
import re,time
from os import path

baseURL = "https://elderscrolls.fandom.com"
indexPages = ["https://elderscrolls.fandom.com/wiki/Category:Morrowind:_Characters",
"https://elderscrolls.fandom.com/wiki/Category:Morrowind:_Characters?from=Assumanu+Mantiti",
"https://elderscrolls.fandom.com/wiki/Category:Morrowind:_Characters?from=Carecalmo",
"https://elderscrolls.fandom.com/wiki/Category:Morrowind:_Characters?from=Dralas+Gilu",
"https://elderscrolls.fandom.com/wiki/Category:Morrowind:_Characters?from=Eydis+Fire-Eye",
"https://elderscrolls.fandom.com/wiki/Category:Morrowind:_Characters?from=Ghost+of+Galos+Heleran",
"https://elderscrolls.fandom.com/wiki/Category:Morrowind:_Characters?from=Iingail",
"https://elderscrolls.fandom.com/wiki/Category:Morrowind:_Characters?from=Llether+Vari",
"https://elderscrolls.fandom.com/wiki/Category:Morrowind:_Characters?from=Minglos",
"https://elderscrolls.fandom.com/wiki/Category:Morrowind:_Characters?from=Oleen-Gei",
"https://elderscrolls.fandom.com/wiki/Category:Morrowind:_Characters?from=Salen+Ravel",
"https://elderscrolls.fandom.com/wiki/Category:Morrowind:_Characters?from=Talamu+Sethendas",
"https://elderscrolls.fandom.com/wiki/Category:Morrowind:_Characters?from=Ultis+Salam",
"https://elderscrolls.fandom.com/wiki/Category:Morrowind:_Characters?from=Zelay+Sobbinisun"
]


def openPage(url):
	req = Request(
		url, 
		data=None, 
		headers={
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
		}
	)
	html = urlopen(req).read().decode('utf-8')
	return(html)


for indexPage in indexPages:
	index = openPage(indexPage)
	time.sleep(2)
	pageLinks = re.findall('<a href="(.+?)" class="category-page__member-link"',index)

	for page in pageLinks:
		#print(page)
		fileName = "raw/"+page[page.rindex("/")+1:].replace(" ","").replace("(","_").replace(")","_") + ".html"
		foundDialogue = False
		if not path.exists(fileName):
			pageTxt = openPage(baseURL + page)
			time.sleep(3)
			html = BeautifulSoup(pageTxt, 'html.parser')
			dialogue = html.find_all("div",{"class":["diabox-half","diabox"]})
			gender = html.find_all("div",{"data-source":"gender"})
			name = html.find_all("h1",{"class":"page-header__title"})
			
			otherDataDict = {}
			otherData = html.find_all("div",{"class":["pi-data"]},recursive=True)
			for ot in otherData:
				label = ot.find("h3")
				if not label is None:
					key = label.getText()
					valueDiv= ot.find("div")
					if not valueDiv is None:
						value = valueDiv.getText()
						otherDataDict[key] = value
			stats = html.find_all("td",{"class":["pi-horizontal-group-item","pi-data-value"]},recursive=True)
			statsText = ""
			for s in stats:
				key = ""
				if "data-source" in s.attrs:
					key = s.attrs["data-source"]
				statsText += "\n" + key + "::" + s.getText()
			
			if len(name)>0:
				outTxt = str(name) + "\n"
				if len(dialogue)>0:
					outTxt += str(dialogue) + "\n"
				if len(gender)>0:
					outTxt += str(gender)
					
				if len(otherDataDict)>0:
					outTxt += '\n<div id="OtherData">\n' + str(otherDataDict) + '\n</div>'
				if len(statsText)>0:
					outTxt += '\n<div id="StatsData">\n' + statsText + '\n</div>'
				
				
				if len(outTxt)>2:
					foundDialogue = True
					with open(fileName, "w") as file:
						file.write(outTxt)
			if not foundDialogue:
				print("  No dialogue")
				with open(fileName, "w") as file:
					file.write(" ")
