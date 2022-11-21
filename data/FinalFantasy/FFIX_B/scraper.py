from urllib.request import *


page = "https://gamefaqs.gamespot.com/ps/197338-final-fantasy-ix/faqs/42207"

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


