from urllib.request import *
from bs4 import BeautifulSoup


# ??? characters
# 'you still with me sam?'
# https://www.youtube.com/watch?v=3J3wLlCnCQw&t=5s

page = "https://game-scripts-wiki.blogspot.com/2019/12/death-stranding-full-transcript.html"

req = Request(
    page, 
    data=None, 
    headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }
)

html = urlopen(req).read().decode('utf-8')
soup = BeautifulSoup(html, "html5lib")
post = soup.find("div", {"class":"post-body"})

o = open("raw/page01.html",'w')
o.write(str(post))
o.close()


