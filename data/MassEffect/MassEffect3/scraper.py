from urllib.request import *
import codecs, time

pages = ["https://docs.google.com/document/pub?id=1O5sjL4pL0bTs1MNSmsrhAE-4WTTeE0foicqJrHpiOOg"]

pageNum = 0
for page in pages:
	pageNum += 1
	fileName = "raw/page_"+str(pageNum).zfill(3)+".html"
	req = Request(
		page, 
		data=None, 
		headers={
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
		}
	)


	html = urlopen(req).read()#.decode('cp1252').encode('utf-8')#.decode('ISO-8859-1')
	o = open(fileName,'w')
	o.write(html)
	o.close()
	time.sleep(3)
	#with codecs.open(fileName, "w", "utf-8") as targetFile:
	#	targetFile.write(html)
