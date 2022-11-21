from urllib.request import urlopen
import time
from os import path
import re


html = urlopen("https://www.ffcompendium.com/h/faqs/ffx2scriptaschthehated.txt").read().decode("utf-8", "backslashreplace")

o = open("raw/page001.html",'w')
o.write(html)
o.close()



