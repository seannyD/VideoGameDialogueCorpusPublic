from urllib.request import urlopen
import time
from os import path

# TODO: Change to https://static.chronocompendium.com/Black/Publications/CTNAScriptonly.txt
pages = ["https://static.chronocompendium.com/Black/Publications/Retranslation/CT%20Retranslation%20-%20Chapter%201.htm",
"http://chronofan.com/Black/Publications/Retranslation/CT%20Retranslation%20-%20Chapters%202-3.htm",
"http://chronofan.com/Black/Publications/Retranslation/CT%20Retranslation%20-%20Chapters%204-5.htm",
"http://chronofan.com/Black/Publications/Retranslation/CT%20Retranslation%20-%20Chapters%206-7.htm",
"http://chronofan.com/Black/Publications/Retranslation/CT%20Retranslation%20-%20Chapter%209.htm",
"http://chronofan.com/Black/Publications/Retranslation/CT%20Retranslation%20-%20Chapters%2010-11.htm",
"http://chronofan.com/Black/Publications/Retranslation/CT%20Retranslation%20-%20Chapters%2012-14.htm",
"http://chronofan.com/Black/Publications/Retranslation/CT%20Retranslation%20-%20Chapters%2015-17.htm",
"http://chronofan.com/Black/Publications/Retranslation/CT%20Retranslation%20-%20Chapter%2018.htm",
"http://chronofan.com/Black/Publications/Retranslation/CT%20Retranslation%20-%20Chapters%2019-21.htm",
"http://chronofan.com/Black/Publications/Retranslation/CT%20Retranslation%20-%20Chapter%2022.htm",
"http://chronofan.com/Black/Publications/Retranslation/CT%20Retranslation%20-%20Chapter%2023.htm",
"http://chronofan.com/Black/Publications/Retranslation/CT%20Retranslation%20-%20Chapter%2024.htm",
"http://chronofan.com/Black/Publications/Retranslation/CT%20Retranslation%20-%20Chapter%2025-1.htm",
"http://chronofan.com/Black/Publications/Retranslation/CT%20Retranslation%20-%20Chapter%2025-2.htm",
"http://chronofan.com/Black/Publications/Retranslation/CT%20Retranslation%20-%20Chapter%2025-3.htm",
"http://chronofan.com/Black/Publications/Retranslation/CT%20Retranslation%20-%20Chapter%2026.htm",
"http://chronofan.com/Black/Publications/Retranslation/CT%20Retranslation%20-%20Endings%20and%20Lost%20Lines.htm"]


pageNum = 0
for page in pages:
	print(page)
	pageNum += 1
	fileName = "raw/page_"+str(pageNum).zfill(3)+".html"
	if not path.exists(fileName):
		html = urlopen(page).read().decode('cp1252')
		#html = html.encode("utf-8")
		o = open(fileName,'w')
		o.write(html)
		o.close()
		time.sleep(2)

