import os
from bs4 import BeautifulSoup
import re

xoreosToolLocation = "/Users/seanroberts/OneDrive\ -\ Cardiff\ University/Research/Cardiff/VideoGameScripts/offline/DA/xoreos-tools-0.0.6-mac64/gff2xml"
clFileLocation = "/Users/seanroberts/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/offline/DA/xoreos-tools-0.0.6-mac64/clFiles/"
tmp = "/Users/seanroberts/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/offline/DA/xoreos-tools-0.0.6-mac64/clFilesUnencoded/"

# Files are converted online, since there are
#  too many files to batch convert in the command line.

out = "clFile,indexNum,actorID,tag,actorMappingTag,name,tlkStringID\n"

files = os.listdir(clFileLocation)
#files = ["gen00fl_anders6125218.cl"]

for f in files:
	# convert to xml using xoreos tools
	xmlFile = tmp.replace(" ","\\ ")+f
	clFileLocation2 = clFileLocation.replace(" ","\\ ")
	execLine = xoreosToolLocation+ " " + clFileLocation2+f +" > "+xmlFile

	os.system(execLine)

	# read xml
	xml = open(tmp+f,'r', encoding = 'utf8')
	soup = BeautifulSoup( xml, "lxml")	
	
	actorList = soup.find("struct_list", {"alias":"CutsceneActors"})
	
	for actor in actorList.find_all("struct", {"name":"ACTR"}):
		tlkStrings = actor.find_all("tlkstring")
		if len(tlkStrings)>0:	
			indexNum = actor["index"]
			actorID = actor.find("uint32",{"alias":"CutsceneActorID"},recursive=True).getText().strip()
			name = actor.find("string",{"alias":"Name"},recursive=True).getText().strip()
			tag = actor.find("string",{"alias":"Tag"},recursive=True)
			tag2 = actor.find("string",{"alias":"CutsceneActorMappingTag"})

			tagString = ""
			if not tag is None:
				tagString = tag.getText().strip()
			tagString2 = ""
			if not tag2 is None:
				tagString2 = tag2.getText().strip()
			
			for tlkString in actor.find_all("tlkstring",recursive=True):
				tlkStringID = tlkString.getText()
				out += ",".join([f.replace(".cl",""),indexNum,actorID,tagString,tagString2,name,tlkStringID])
				out += "\n"
				
		# Awakening companions are complicated. Anders has "Justice" within them
		#Line 6125218, "I will get justice, by any means required." https://youtu.be/n62I_sb0l0A?t=909
		# This is linked by
		# <uint32 label="5603" alias="CutsceneActionShakeNoiseSeed">6125234</uint32>
		# Sometimes the name is suggested by:
		#             <struct name="AJSC" label="3">
		#          <string label="1" alias="Tag">cam_justice_player_ots</string>
		# And also additionally:
		#       <string label="5029">cam_justice_ots</string>
		# But not always
		# So sometimes get the stageing name?
		#       <string label="5024">and330st_base_justice_post2</string>
		awa = actor.find("uint32",{"label":"5603"}, recursive=True)
		if not awa is None:
			tlkStringID2 = str(awa.getText()).strip()
			actorID = "Awakened"
			awaIndex = "Awakened"
			ASJC = actor.find("struct",{"name":"AJSC"})
			nameTag = ""
			if not ASJC is None:
				nameTag = ASJC.find("string", {"alias":"Tag"}).getText().strip()
			if len(nameTag)==0:
				altTag = actor.find("string", {"label":"5029"})
				if not altTag is None:
					nameTag = altTag.getText().strip()
			if len(nameTag) == 0:
				stage = actor.find("string",{"label":"5029"}, recursive=True)
				if not stage is None:
					nameTag = stage.getText().strip()
			if len(nameTag) == 0:
				nameTag = "Unknown"
				
			out += ",".join([f.replace(".cl",""),awaIndex,actorID,nameTag,nameTag,nameTag,tlkStringID2])
			out += "\n"
				
	# Some talkstrings are inside Henchman actions:
	#<string label="5050" alias="CutsceneHenchmanTag">gen00fl_isabela</string>
	hench = soup.find("generic_list", {"alias":"CutsceneHenchmanActions"},recursive=True)
	if not hench is None:
		henchTlkStrings = [x.getText() for x in hench.find_all("tlkstring") if len(x)>0]
		if len(henchTlkStrings)>0:
			henchIndex = "Hench"
			actorID = "Hench"
			name = soup.find("string",{"alias": "CutsceneHenchmanTag"}, recursive=True).getText()
			tag = name
			tag2 = name
			for tlkStringID in henchTlkStrings:
				out += ",".join([f.replace(".cl",""),henchIndex,actorID,tag,tag2,name,tlkStringID])
				out += "\n"

		
	
	# clean up
	#os.system("rm " +tmp.replace(" ","\\ ") + "*.cl")

with open("tlkStringToCharName.csv",'w') as f:
	f.write(out)

