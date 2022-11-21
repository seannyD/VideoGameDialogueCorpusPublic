from urllib.request import urlopen
import time

chapters = [
		"https://kingsquest.fandom.com/wiki/KQC1_transcript",
		"https://kingsquest.fandom.com/wiki/KQC2_transcript",
		"https://kingsquest.fandom.com/wiki/KQC3_transcript",
		"https://kingsquest.fandom.com/wiki/KQC4_transcript",
		"https://kingsquest.fandom.com/wiki/KQC5_transcript",
		"https://kingsquest.fandom.com/wiki/KQC6_transcript"]
		
i = 1
for chapter in chapters:
	html = urlopen(chapter).read().decode('utf-8')
	o = open("raw/page0" + str(i) + ".html",'w')
	i += 1
	o.write(html)
	o.close()
	time.sleep(3)