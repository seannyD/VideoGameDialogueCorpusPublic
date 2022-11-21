def blockParser(bit,fileName):
	print(list(bit.children))
	choices = []
	for child in bit.children:
		if isinstance(child, NavigableString):
			print(("PASS",child))
			pass
		else:
			print("====")
			print(child)
			print(type(child))
			print(child.get("class"))
			print(fileName)
			if child.name=="p" and (child.get("class") is not None) and (("indent" in child.get("class")) or ("indent-nopad" in child.get("class"))):
				print(("1",child))
				charName,dialogue = dialogueParser(child)
				if len(choices)>0 and isinstance(choices[-1],list):
					choices[-1].append({charName:dialogue})
				else:
					choices.append([{charName:dialogue}])
			elif child.name=="p":
				print("2")
				# Main character choice
				dialogueSpan = child.find("span")
				print("DSPAN")
				print(dialogueSpan)
				if dialogueSpan is not None:
					dialogue = dialogueSpan.get_text()
					if dialogue.strip().startswith("If "):
						choices.append([{"ACTION":dialogue}])					
					else:
						choices.append([{"Cloud":dialogue}])
				else:
					# Action description within a choice
					childClass = child.get("class")
					if childClass is not None and "italic" in childClass:
						choices.append([{"ACTION": child.get_text()}])		
					else:
					# There can be a difference between the option and your dialogue
					# Then the above would be a cue
						dialogue = child.get_text()
						charName = "Cloud"
						choices[-1] = [{charName:dialogue,"_Cue":list(choices[-1][0].values())[0]}]
			elif child.name=="div" and "block" in child.get("class"):
				print("3")
				# Recursion
				subChoices = blockParser(child,fileName)
				choices.append({"CHOICE":subChoices})
	#print(choices)
	return(choices)