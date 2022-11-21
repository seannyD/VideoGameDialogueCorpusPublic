from urllib.request import urlopen

page = "https://kingsquest.fandom.com/wiki/KQ5NES_transcript"
html = urlopen(page).read().decode('utf-8')
o = open("raw/page01.html",'w')
o.write(html)
o.close()
