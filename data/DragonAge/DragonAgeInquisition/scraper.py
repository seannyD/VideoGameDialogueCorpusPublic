from urllib.request import urlopen

page = "https://daitranscripts.tumblr.com/post/185385333012/the-wrath-of-heaven-pt-1"
html = urlopen(page).read().decode('utf-8')
o = open("raw/page01.html",'w')
o.write(html)
o.close()
