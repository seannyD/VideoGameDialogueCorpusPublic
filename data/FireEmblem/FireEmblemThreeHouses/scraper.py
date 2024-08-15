from urllib.request import *
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import re,time
import os


def openPage(url):
	req = Request(
		url, 
		data=None, 
		headers={
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
		}
	)
	html = urlopen(req).read().decode('utf-8')
	html = BeautifulSoup(html, 'lxml')
	html = html.find("main")
	return(html)
	


# Dummy file for parser
with open("raw/dummyFile.html", "w") as file:
	file.write("dummy")

# Download scenarios
baseURL = "https://houses.fedatamine.com/en-uk/"
rawFolder = "raw/en-uk/"

pageCategories = [("scenarios",370),("monastery",84)]

for cat,maxi in pageCategories:
	folder = rawFolder + cat+"/"
	if not os.path.exists(folder):
		os.mkdir(folder)
	for i in range(maxi):
		fileName = folder + str(i)+".html"
		print(fileName)
		if not os.path.exists(fileName):
			pageURL = baseURL + cat + "/"+ str(i)
			try:
				data = openPage(pageURL)
				with open(fileName, "w") as file:
					file.write(str(data))
			except HTTPError:
				print("ERROR " + pageURL)
				with open(fileName, "w") as file:
					file.write("")				
			time.sleep(2)
	