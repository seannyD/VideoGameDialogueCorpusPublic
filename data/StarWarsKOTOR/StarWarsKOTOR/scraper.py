from urllib.request import *
import codecs, time

page = "https://github.com/hmi-utwente/video-game-text-corpora/raw/master/Star%20Wars:%20Knights%20of%20the%20Old%20Republic/data/dataset_20200716.csv"

fileName = "raw/dataset_20200716.csv"
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
