from urllib.request import *
import codecs, time

page = "https://raw.githubusercontent.com/pod7/dragonage_compendium/master/data/origins/csv/cleaned/t_dialogue_clean.csv"

fileName = "raw/t_dialogue.csv"
req = Request(
	page, 
	data=None, 
	headers={
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
	}
)


csv = urlopen(req).read().decode('utf-8')
o = open(fileName,'w')
o.write(csv)
o.close()
time.sleep(3)
