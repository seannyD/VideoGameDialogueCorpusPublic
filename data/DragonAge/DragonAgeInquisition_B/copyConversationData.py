import os,shutil

sourceFolder = "/Users/seanroberts/OneDrive - Cardiff University/Data/DragonAgeInquisitionData/DA3/Conversations/"

print(os.path.isdir(sourceFolder))
i = 0
for root, dirs, files in os.walk(sourceFolder):
	print("Copying "+root)
	destFolder = "raw/"+ root[len(sourceFolder):]+"/"
	if not os.path.exists(destFolder):
		os.makedirs(destFolder)
	files = [x for x in files if x.count("VoiceOver")==0]
	files = [x for x in files if x!=".DS_Store"]
	for file in files:
		#print(root+"/"+file)
		if not os.path.exists(destFolder+file):
			print((root+"/"+file, destFolder+file))
			shutil.copy(root+"/"+file, destFolder+file)



