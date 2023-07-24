import os,subprocess,time

homedir = "/Users/seanroberts/Documents/BarbieDiaries/program files/Barbie(TM)/Barbie(TM) Diaries High School Mystery/Barbie/sounds/characters/"

scratchDir = "/Users/seanroberts/Documents/BarbieDiaries/scratch/"

doneFiles = os.listdir(scratchDir)


charDirs = [x for x in os.listdir(homedir) if os.path.isdir(homedir+x)]


for char in charDirs:
#char = "bar"
	charHome = homedir + char + "/speech/"
	files = os.listdir(charHome)
	files = [file for file in files if file.endswith(".ogg")]

	for file in files:
		print(file)
		fileStem = file[:file.index(".")]
		outFile = fileStem + ".txt"
		if not outFile in doneFiles:
			convertCommand = "ffmpeg -y -i " + charHome.replace(" ","\ ").replace("(","\(").replace(")","\)") + file + " " + scratchDir+ "tmp.wav"
			subprocess.run(convertCommand, shell=True)
			print("Converted")
			stream = os.popen("hear -i /Users/seanroberts/Documents/BarbieDiaries/scratch/tmp.wav")
			output = stream.read()
			print(output)
			o = open(scratchDir+outFile,'w')
			o.write(output)
			o.close()
			time.sleep(2)
		
