from urllib.request import urlopen
from bs4 import BeautifulSoup
import time

page = "https://game-scripts-wiki.blogspot.com/2022/02/horizon-ii-forbidden-west-transcript.html"
html = urlopen(page).read().decode('utf-8')
o = open("raw/page01.html",'w')
o.write(html)
o.close()
