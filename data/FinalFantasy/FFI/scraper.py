from urllib.request import urlopen
import time
from os import path

url = "https://archive.rpgamer.com/games/ff/ff1/info/ff1_script.txt"

html = urlopen(url).read().decode("utf-8", "backslashreplace")
o = open("raw/page01.txt",'w')
o.write(html)
o.close()
