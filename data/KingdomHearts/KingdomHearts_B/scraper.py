from urllib.request import *

page = "https://gamefaqs.gamespot.com/ps3/684080-kingdom-hearts-hd-15-remix/faqs/68066"

req = Request(
    page, 
    headers={
        'User-Agent': 'XYZ/3.0'
    }
)

html = urlopen(req, timeout=10).read().decode('utf-8')
o = open("raw/page01.html",'w')
o.write(html)
o.close()