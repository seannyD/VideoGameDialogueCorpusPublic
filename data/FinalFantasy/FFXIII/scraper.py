from urllib.request import *

page = "https://en.wikiquote.org/wiki/Final_Fantasy_XIII"

req = Request(
    page, 
    headers={
        'User-Agent': 'XYZ/3.0'
    }
)

html = urlopen(req, timeout=10).read().decode('utf-8')
o = open("raw/Final Fantasy XIII - Wikiquote.html",'w')
o.write(html)
o.close()