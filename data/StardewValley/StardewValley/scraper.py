import time,os
from google_drive_downloader import GoogleDriveDownloader as gdd

sources = [('0BwyXuxAqGS7uZU5VVXdUMXVrMVk', 'Abigail.yaml' ),
 ('0BwyXuxAqGS7uNWY5U2NIOXItRWs', 'Alex.yaml' ),
 ('0BwyXuxAqGS7ueVRUSlVuN3c5Mk0', 'Caroline.yaml' ),
 ('0BwyXuxAqGS7ubWc3eUZnRjk4dkU', 'Clint.yaml' ),
 ('0BwyXuxAqGS7uNnduc2pBdzdDNzg', 'Demetrius.yaml' ),
 ('0BwyXuxAqGS7uZld0VUxydFBxelk', 'Dwarf.yaml' ),
 ('0BwyXuxAqGS7uZk1OTVY0SWdHSGc', 'Elliott.yaml' ),
 ('0BwyXuxAqGS7ud1BWOEFEYU9nLXM', 'Emily.yaml' ),
 ('0BwyXuxAqGS7uYXowVVJiUlczMEE', 'Evelyn.yaml' ),
 ('0BwyXuxAqGS7uczR0T09vYjJLNXM', 'George.yaml' ),
 ('0BwyXuxAqGS7uWFgyRXhneXk1VWc', 'Gil.yaml' ),
 ('0BwyXuxAqGS7uRnRWdlFCd1RDZGs', 'Gus.yaml' ),
 ('0BwyXuxAqGS7uaGQwRnFSTS12VHc', 'Haley.yaml' ),
 ('0BwyXuxAqGS7ubUlfX3NoX1B6bmM', 'Harvey.yaml' ),
 ('0BwyXuxAqGS7uUHVxSVkzZ0ZMb1U', 'Jas.yaml' ),
 ('0BwyXuxAqGS7uNy1tbDJMNDRLS2c', 'Jodi.yaml' ),
 ('0BwyXuxAqGS7uVkNmRmhmUlhObnc', 'Kent.yaml' ),
 ('0BwyXuxAqGS7uejc4X2luZExfZms', 'Krobus.yaml' ),
 ('0BwyXuxAqGS7ucFdNNVNPYXprc0k', 'Leah.yaml' ),
 ('0BwyXuxAqGS7uV0REN1hDS0cyWUE', 'Lewis.yaml' ),
 ('0BwyXuxAqGS7uak9jQ1NIMzJudWc', 'Linus.yaml' ),
 ('0BwyXuxAqGS7uUHlRSzVYSWVwVnc', 'Marnie.yaml' ),
 ('0BwyXuxAqGS7uSFdtNkhnM1FlOWc', 'MarriageDialogue.yaml' ),
 ('0BwyXuxAqGS7uQ1Rsb1RyekVzcTA', 'MarriageDialogueAbigail.yaml' ),
 ('0BwyXuxAqGS7uVWhwcFFCRERuUzA', 'MarriageDialogueAlex.yaml' ),
 ('0BwyXuxAqGS7uUUhzN2trMndvQk0', 'MarriageDialogueElliott.yaml' ),
 ('0BwyXuxAqGS7uRUZ3dkV0Y2Z0MUE', 'MarriageDialogueEmily.yaml' ),
 ('0BwyXuxAqGS7uajBHZEZsSU51d2s', 'MarriageDialogueHaley.yaml' ),
 ('0BwyXuxAqGS7udEFLQWIteFVOVlE', 'MarriageDialogueHarvey.yaml' ),
 ('0BwyXuxAqGS7uekx3eXdyLWcxY28', 'MarriageDialogueLeah.yaml' ),
 ('0BwyXuxAqGS7uU2xEbEdkOHNVbVE', 'MarriageDialogueMaru.yaml' ),
 ('0BwyXuxAqGS7uMEp1VW4wSlhEZFU', 'MarriageDialoguePenny.yaml' ),
 ('0BwyXuxAqGS7uYndqYVdpbGNCRUk', 'MarriageDialogueSam.yaml' ),
 ('0BwyXuxAqGS7uOXpuY3VIUjlVVTA', 'MarriageDialogueSebastian.yaml' ),
 ('0BwyXuxAqGS7uU3lQaE41Z1ZpQWs', 'MarriageDialogueShane.yaml' ),
 ('0BwyXuxAqGS7uR1piUUlWNXI2OTg', 'Maru.yaml' ),
 ('0BwyXuxAqGS7uV2ZQU1RrX3ZJdVk', 'Mister Qi.yaml' ),
 ('0BwyXuxAqGS7uVlBuTjJRY2RvVG8', 'Pam.yaml' ),
 ('0BwyXuxAqGS7uSktQS3BmRVVadlk', 'Penny.yaml' ),
 ('0BwyXuxAqGS7ubzBNZUNucE95NzA', 'Pierre.yaml' ),
 ('0BwyXuxAqGS7uXzhjUVdHQWZud2s', 'rainy.yaml' ),
 ('0BwyXuxAqGS7uczBfT3IzT3YyakU', 'Robin.yaml' ),
 ('0BwyXuxAqGS7uQnlxVEVFUHZmbEE', 'Sam.yaml' ),
 ('0BwyXuxAqGS7uaDZ3QXRPdHlEdnc', 'Sandy.yaml' ),
 ('0BwyXuxAqGS7uSVlxcVpKVnQtMDg', 'Sebastian.yaml' ),
 ('0BwyXuxAqGS7uRTVibldIOG0yc3M', 'Shane.yaml' ),
 ('0BwyXuxAqGS7uXzdyRjdBeTFod3c', 'Vincent.yaml' ),
 ('0BwyXuxAqGS7uVzFBdURDcDYzLUk', 'Willy.yaml' ),
 ('0BwyXuxAqGS7uTWctY1hkYnduM0k', 'Wizard.yaml')]
 
 
events = [('0BwyXuxAqGS7uUlEyUERWUzN1WFk', 'AnimalShop.yaml'), ('0BwyXuxAqGS7ua21KYXZteUR0bzQ', 'ArchaeologyHouse.yaml'), ('0BwyXuxAqGS7uNThuZjVBNTN4MEE', 'BathHouse_Pool.yaml'), ('0BwyXuxAqGS7uWDhTdC1Bdmkzenc', 'Beach.yaml'), ('0BwyXuxAqGS7uZktxcTRqZGZIWGM', 'BusStop.yaml'), ('0BwyXuxAqGS7uS29Yd0tXU2pYZDg', 'CommunityCenter.yaml'), ('0BwyXuxAqGS7uVjJ1X2lyNUlwakk', 'ElliottHouse.yaml'), ('0BwyXuxAqGS7uWXY4V1hlR2lHZzg', 'Farm.yaml'), ('0BwyXuxAqGS7uYVZrbXVoQk8xWE0', 'FarmHouse.yaml'), ('0BwyXuxAqGS7uVUNZMHNGNFZQZEk', 'Forest.yaml'), ('0BwyXuxAqGS7uNEtoTkIyZ29vek0', 'HaleyHouse.yaml'), ('0BwyXuxAqGS7uNGYtQmhWc0JBWDA', 'HarveyRoom.yaml'), ('0BwyXuxAqGS7uNGU4NGlrOTZ5T1U', 'Hospital.yaml'), ('0BwyXuxAqGS7uV2tIR3VRM3gxRzQ', 'JoshHouse.yaml'), ('0BwyXuxAqGS7uUzlLd0pfSUVwZTA', 'LeahHouse.yaml'), ('0BwyXuxAqGS7uQmY2S1lXX3owc2s', 'ManorHouse.yaml'), ('0BwyXuxAqGS7uZThTdDB0c2pwRE0', 'Mine.yaml'), ('0BwyXuxAqGS7uU0tiLXVqdGRoMms', 'Mountain.yaml'), ('0BwyXuxAqGS7uVzdlYlRfbC11TFE', 'Railroad.yaml'), ('0BwyXuxAqGS7uUnhjVmhMNVpiVTQ', 'Saloon.yaml'), ('0BwyXuxAqGS7uUmtCX0JjQzY0WDQ', 'SamHouse.yaml'), ('0BwyXuxAqGS7uM01GTm5Ec05fcGs', 'SandyHouse.yaml'), ('0BwyXuxAqGS7uM0VsMlIxM055cWM', 'ScienceHouse.yaml'), ('0BwyXuxAqGS7ub1I3LVg0SlBOWE0', 'SebastianRoom.yaml'), ('0BwyXuxAqGS7uTWZ3eE96UHlkVm8', 'SeedShop.yaml'), ('0BwyXuxAqGS7uWFUyOFliUjhiNVE', 'Sewer.yaml'), ('0BwyXuxAqGS7uNHYxVHM5Z2tvaDQ', 'Temp.yaml'), ('0BwyXuxAqGS7uekE4TTY1VUsxTTQ', 'Tent.yaml'), ('0BwyXuxAqGS7uWmoyY2xTWTFldDg', 'Town.yaml'), ('0BwyXuxAqGS7uNktaeWxjVEVweU0', 'Trailer.yaml'), ('0BwyXuxAqGS7uTEotM0FfeHZCRms', 'WizardHouse.yaml'), ('0BwyXuxAqGS7uQUZNMnpfUUktWEk', 'Woods.yaml')]
 
 
for source in sources:
	print(source)
	outPath = 'raw/'+source[1]
	if not os.path.isfile(outPath):
		gdd.download_file_from_google_drive(file_id=source[0],
                                    dest_path=outPath,
                                    unzip=False)
		time.sleep(3)

for source in events:
	print(source)
	outPath = 'raw/'+"Event_"+source[1]
	if not os.path.isfile(outPath):
		gdd.download_file_from_google_drive(file_id=source[0],
                                    dest_path=outPath,
                                    unzip=False)
		time.sleep(3)
                                    