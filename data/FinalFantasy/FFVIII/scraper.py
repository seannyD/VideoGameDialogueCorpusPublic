from urllib.request import *

page = "https://www.neoseeker.com/finalfantasy8/faqs/136092-final-fantasy-viii-script-a.html"

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