from urllib.request import urlopen

page = "https://kingsquest.fandom.com/wiki/KQ4SCI_transcript"
html = urlopen(page).read().decode('utf-8')
o = open("raw/page01.html",'w')
o.write(html)
o.close()
