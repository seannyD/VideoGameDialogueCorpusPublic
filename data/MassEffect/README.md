# Mass Effect sources

The main sources used for Mass Effect in the analysis come from a dump of the game files. This requires having each Mass Effect game installed on your computer. This dump was created using a customised version of the ME3 Legendary Explorer (https://github.com/ME3Tweaks/LegendaryExplorer). 

## MassEffect1

A fan transcript of the intro and first mission of Mass Effect 1. http://www.masseffectlore.com/transcripts/mass-effect-1-transcripts/

## MassEffect1B

From dump of game files.

## MassEffect2

From dump of game files.

## MassEffect3

Fan transcript, mainly a guide. Source no longer public on the internet.

## MassEffect3B

Parsing of a public dump of the Mass Effect 3 dialogue from game files. The scraper and parser will work without needing to use the Legendary Explorer or have Mass Effect 3 installed. The dialogue is mostly complete, but the parsing doesn't capture the full structure. Still, this is an acceptable source if analysts are just interested in the text rather than the structure.

## MassEffect3C

From dump of game files.


# Structure

Currently, the conversation structure follows a depth-first approach. Basically when a choice comes up, you see embedded all the 'default' choices, then the alternative routes come at the end.

The ideal structure would be something like this, where there's a main sequence and choices are laid side by side. The first choice varies the line depending on the gender of Shepard. There's a "STATUS" check to see if Shepard is female. Then the second option has a status check of "-1 (0)", which is the default option that is selected if none of the other options in the set are true.

```
{"Garrus Vakarian": "Careful, Wrex. Shepard's helping you now.", "_ID": "581539"},
{"CHOICE": [
	[
		{"STATUS": "Shepard is female (0)"},
		{"Urdnot Wrex": "Is she?", "_ID": "581542"}
	],
	[
		{"STATUS": "Shepard is female (0)"},
		{"Urdnot Wrex": "Is he?", "_ID": "581542"}		
	]]},
{"Urdnot Wrex": "Whose side are you on, Shepard?", "_ID": "581547"},
{"CHOICE": [
	[
		{"ACTION": "AGREE", "_PROMPT": "\"I was wrong to destroy data.\""},
		{"Shepard": "Destroying the data was a mistake. ", "_ID": "558582"}
	],
	[
		{"ACTION": "DISAGREE", "_PROMPT": "\"I don't regret what I did.\""},
		{"Shepard": "The krogan weren't ready for a cure.", "_ID": "558583"}
	]]}
```

However, what we currently have is something like this, where choices are embedded inside each other. The second option of the first choice appears way down the page, with a "GOTO" instruction, showing the ID of the line to jump to.

```
{"Garrus Vakarian": "Careful, Wrex. Shepard's helping you now.", "_ID": "581539"},
{"CHOICE": [
	[
		{"STATUS": "Shepard is female (0)"},
		{"Urdnot Wrex": "Is she?", "_ID": "581542"}
		{"ACTION": "", "_ID": "590793"},
		{"Urdnot Wrex": "Whose side are you on, Shepard?", "_ID": "581547"},
		{"CHOICE": [
			[
				{"ACTION": "AGREE", "_PROMPT": "\"I was wrong to destroy data.\""},
				{"Shepard": "Destroying the data was a mistake. ", "_ID": "558582"}
			],
			[
				{"ACTION": "DISAGREE", "_PROMPT": "\"I don't regret what I did.\""},
				{"Shepard": "The krogan weren't ready for a cure.", "_ID": "558583"}
			]]}
	],
	[
		{"STATUS": "Shepard is female (0)"},
		{"Urdnot Wrex": "Is he?", "_ID": "581542"}
		{"GOTO": "590793"}
	]]},
```


## Player gender

In a perfect world, we would count each unique recording of a line of dialogue, separating lines by male/female voice actors. However, for the current project, we just count each line once, as it appears in the script. This is because the effect of player gender on dialogue choices is difficult to capture accurately. Although some conditions specifically test the gender of the player, other choices depend on gender indirectly. For example, the possibility of romancing some NPCs is only available for specific player character genders. Some dialogue choices test the romance flags, which imply player gender indirectly. With complete knowledge of the game, it would be possible to identify which status flags index gender. However, there is no publicly available, comprehensive and totally accurate list of what each status test means. This means that it's very hard to identify whether a male/female Shepard speaks a line or not.