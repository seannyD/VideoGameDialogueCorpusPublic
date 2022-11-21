from urllib.request import *

def loadPage(page):
	req = Request(
		page, 
		data=None, 
		headers={
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
		}
	)

	html = urlopen(req).read().decode('utf-8')
	return(html)


#page = "https://transcripts.fandom.com/wiki/Kingdom_Hearts_3D:_Dream_Drop_Distance"
page = "https://gamefaqs.gamespot.com/3ds/997779-kingdom-hearts-3d-dream-drop-distance/faqs/65008"
#html = urlopen(page).read().decode('utf-8')
html = loadPage(page)
o = open("raw/page01.html",'w')
o.write(html)
o.close()
