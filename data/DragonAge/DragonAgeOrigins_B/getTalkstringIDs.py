# Get talkstring IDs from core_en-us.xml
import re

d = open("raw/singleplayer_en-us.xml").read()

ids = re.findall('id="([0-9]+)"',d)

o = open("talkstringIDs.xml",'w')
o.write(",".join(ids))