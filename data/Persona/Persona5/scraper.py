from urllib.request import urlopen

page = "https://transcripts.fandom.com/wiki/Persona_5"
html = urlopen(page).read().decode('utf-8')
o = open("raw/page01.html",'w')
o.write(html)
o.close()
