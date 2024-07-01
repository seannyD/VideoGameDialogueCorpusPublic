import os,sys,json,csv,time
from bs4 import BeautifulSoup

from urllib.request import *

def downloadTropePageLinks(folder,url):
	tropeFolder = folder
	if not tropeFolder.endswith("/"):
		tropeFolder += "/"
	tropeFolder += "tropes/"
	if not os.path.isdir(tropeFolder):
		os.mkdir(tropeFolder)
	
	charFile = url
	if charFile.endswith("/"):
		charFile = charFile[:-1]
	charFile = tropeFolder + charFile[charFile.rindex("/")+1:] + ".csv"
	if not os.path.isfile(charFile):
		req = Request(
			url, 
			data=None, 
			headers={
				'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})
		html = urlopen(req).read().decode('utf-8')
		time.sleep(1)
		o = open(charFile,'w')
		o.write(html)
		o.close()
	
	html = open(charFile).read()
	soup = BeautifulSoup(html, "html5lib")
	main = soup.find("div",{"id":"main-article"})
	soup.find("div",{"class":"wmglead"})
	
	links = [["VGDCName","TvTName","type","url","comment"]]
	for link in main.find_all("a"):
		if link["href"].count("Characters")>0:
			#VGDCName,TvTName,type,url,comment
			links.append([link.text,link.text,"main","https://tvtropes.org"+link["href"],""])
	with open(folder+"tropeSources.csv","w") as o:
		csvwriter = csv.writer(o)
		csvwriter.writerows(links)


#downloadTropePageLinks("../data/MassEffect/MassEffect1B/", "https://tvtropes.org/pmwiki/pmwiki.php/Characters/MassEffectCommanderShepard")
downloadTropePageLinks("../data/FinalFantasy/FFXIV/", "https://tvtropes.org/pmwiki/pmwiki.php/Characters/FinalFantasyXIVScionsOfTheSeventhDawn")