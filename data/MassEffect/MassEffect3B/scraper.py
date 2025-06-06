from urllib.request import *
import codecs, time, os.path

pages = [
 ("https://mod.gib.me/masseffect3/testdump2.txt","testdump2.txt"),
 ("https://pastebin.com/raw/eVZPgnb2", "bools.txt"),
 ("https://mod.gib.me/masseffect3/conditionals.txt", "conditionals.txt"),
 ("https://pastebin.com/raw/eqiNW7rE","plotDatabase.txt")]

for page,fn in pages:
	fileName = "raw/"+fn
	if not os.path.isfile(fileName):
		req = Request(
			page, 
			data=None, 
			headers={
				'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
			}
		)

		html = urlopen(req).read()#.decode('cp1252').encode('utf-8')#.decode('ISO-8859-1')
		o = open(fileName,'wb')
		o.write(html)
		o.close()
		time.sleep(3)
	#with codecs.open(fileName, "w", "utf-8") as targetFile:
	#	targetFile.write(html)
