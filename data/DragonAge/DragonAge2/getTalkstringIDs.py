# Get talkstring IDs from core_en-us.xml
import re

d = open("raw/campaign_base_en-us.xml").read()

ids = re.findall('id="([0-9]+)"',d)

o = open("talkstringIDs.xml",'w')
o.write(",".join(ids))