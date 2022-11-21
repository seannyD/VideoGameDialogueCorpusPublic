from urllib.request import *

page = "https://www.mediafire.com/file/bhkqiqjhfib0waa/dialogueExport.txt/file"
page = "https://download2282.mediafire.com/abg350bn4ovg/bhkqiqjhfib0waa/dialogueExport.txt"

req = Request(
    page, 
    data=None, 
    headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }
)
print("Downloading ...")
dat = urlretrieve(page, "raw/dialogueExport.txt")

#html = urlopen(req).read().decode('utf-8')
#o = open("raw/dialogueExport.txt",'w')
#o.write(html)
#o.close()
