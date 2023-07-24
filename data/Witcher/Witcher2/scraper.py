from urllib.request import urlopen
from bs4 import BeautifulSoup
import re,time

indexpage = "https://laurelnose.github.io/"
html = urlopen(indexpage).read().decode('utf-8')

soup = BeautifulSoup(html,'html5lib')
olx = soup.find("ol")
lis = olx.find_all("li")

pages = [li.find("a") for li in lis]
pages = [x for x in pages if not x is None]



href = [x['href'] for x in pages if not 'hidden' in x]
href = list(set([re.sub("#.+","",x) for x in href]))



for url in href:
	print(url)
	try:
		px = urlopen("https://laurelnose.github.io" + url).read().decode('utf-8')
		nx = "raw/P_" + url.replace("/","") + ".html"
		o = open(nx, 'w')
		o.write(px)
		o.close()
	except:
		print("  ERROR")
	time.sleep(2)
	