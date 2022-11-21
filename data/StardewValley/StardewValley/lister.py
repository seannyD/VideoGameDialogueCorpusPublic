import re
o = open("raw/tmp.html")
d = o.read()
o.close()

links = re.findall('data-id="(.+?)"',d)
filenames = re.findall('aria-label="Binary File: (.+?\\.yaml)"',d)

print([x for x in zip(links,filenames)])

print("-----")

o = open("raw/evt.html")
d = o.read()
o.close()

links = re.findall('data-id="(.+?)"',d)
filenames = re.findall('aria-label="Binary File: (.+?\\.yaml)"',d)

print([x for x in zip(links,filenames)])
