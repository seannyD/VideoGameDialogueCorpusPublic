# Video Games Dialogue Corpus

This is the public repository for the Video Games Dialogue Corpus. It contains programs to process game data on your local machine into a common dialogue script format. This can be used as a corpus of language use in video game dialogue.

If you use this data, please cite the following:

Stephanie Rennick, Seán G. Roberts, (under review) The Video Games Dialogue Corpus. Corpora.

Stephanie Rennick, Seán G. Roberts, Melanie Clinton, Elena Ioannidou, Liana Oh, Charlotte Clooney, E. T., Edward Healy, (under review) Gender bias in video game dialogue. Royal Society Open Science.

## Dependencies

Python nltk with resources: 'punct', 'stopwords'.
pip libraries: numpy, PyYAML, igraph, textatistic, xlrd (version 1.2.0), pykakasi (version 2.2.1), beautifulsoup4 (with html5lib, cssutils, lxml).

Spacy, with the pipeline *en_core_web_trf*.

## Data

The **data** folder contains folders for each series and each game within each series. The name of the game folder will be used as the game's unique ID. Each game folder includes:

-  *meta.json*: Meta data about the game, source, parser, and character groups.
-  *scraper.py*: A python script that downloads files and puts them in the 'raw' folder
-  *raw* folder: A folder for temporary storing of downloaded data. This is not shared in the github repository
-  *data.json*: The dialogue data, created by the parsing program.
-  *characters.txt*: A simple list of all unique characters, created by the parsing program.
-  *stats.csv*: Basic stats for the game as a whole and each group in the metadata.

### JSON format for dialogue

The dialogue is stored in a JSON format. The "text" field is an ordered list of lines of dialogue. Each line is represented by a dictionary with a key for the character's name and a value for the line of dialogue.

The key "ACTION" is reserved for descriptions of game actions that are not dialogue.

The key "CHOICE" is reserved for a point in the game where a player has a choice of dialogue options. The value for this key is a list of possible dialogue sequences. Each sequence is a list of dialogue lines, starting with the player's chosen dialogue. A sequence can contain a sequence, allowing dialogue trees to be represented.

In the example below, there is one choice event with the player either choosing that Cloud says "Yeah" or "Not this time".

```json
{"text": [
		...
		{"ACTION": "Marlene jumps up."},
		{"Barret": "Papa!"},
		{"ACTION": "She sees Cloud and hides in the corner. Tifa goes over to her"},
		{"Barret": "Marlene! Aren't you going to say anything to Cloud?"},
		{"ACTION": "She walks over to Cloud."},
		{"Barret": "Welcome home, Cloud. Looks like everything went well."},
		{"Barret": "Did you fight with Barret?"},
		{"CHOICE": [
				[
					{"Cloud": "Yeah "},
					{"Tifa": "I should have known."},
					{"Tifa": " He's always pushing people around, and you've always been in fights ever since you were little."},
					{"Tifa": "I was worried."}],
				[
					{"Cloud": "Not this time "},
					{"Tifa": "Hmm. You've grown up."},
					{"Tifa": " When you were little you used to get into fights at the drop of a hat."}]]},
		{"ACTION": "The PLAYER names Tifa"},
		{"Tifa": "Flowers? How nice..."},
		...
		]
}
```

The idea is that this is readable by both humans and machines and can represent dialogue trees.

### Metadata

The metadata file is a JSON format file with the following fields:

-  "game": Full name of the game.
-  "series": Name of the series(e.g. "Final Fantasy").
-  "year": Year of publication.
-  "source": Web source for the raw script.
-  "sourceFeatures": What the source contains, see below.
-  "characterInfoSource" (optional): Source for a wiki-style listing for automatic extraction of character features. 
-  "sampleOnly" (optional): True if the source is only a small sample of the full script.
-  "notes" (optional): Any coder notes about the data.
-  "parserParameters": parameters for the parser. Must include "parser" (name of the parser that's used) and "fileType" (extension of files in the 'raw' folder to parse, 'html' by default). See the parsers for further arguments that can be passed.
-  "mainPlayerCharacters": list of main playable characters main playable characters and party. This is mainly to compare "main" characters who are often in dialogue with "minor" characters.
-  "characterGroups": Dictionary of groups and the characters that are members of each group (see below)
-  "aliases": A mapping from alternative names to canonical names. This helps the parser fix spelling mistakes and unify character dialogue written under alternative names, (e.g. before their name is known, `"Flower girl": "Aerith"`).

'sourceFeatures' is a dictionary with the following properties:

-  "type": One of 'fan transcript', 'game data', 'wiki'
-  "completeness": One of 'sample', 'high', 'complete'
-  "dialogueOrder": true (appropriate for studying transisions between speakers) or false (some other order, e.g. ordered by )
-  "choices": What is the coverage of dialogue choices?
	-  "NA" (game has no choices)
	-  "not included"
	-  "partial"
	-  "complete"

### Character groups

The characterGroups field in the metadata is a mapping from group names to a list of character names who are members of that group.

The group labels can be any string, and there can be as many groups as is necessary to capture the diversity in the character groupings. Character names should be the final canonical names, after the aliases are applied.

```json
	"characterGroups": {
		"male": [
			"Cloud",
			"Barret",
			...
			],
		"female": [
			"Tifa",
			"Aerith",
			...
			],
		"neutral": [
			"Chocobo",
			"Jenova",
			...
			],
		...
		}
```

Tracking for individual characters can be done by creating a group just for that character:

```json
	...
	"Char_Cloud": ["Cloud"],
	"Char_Barret": ["Barret"],
	"Char_RedXIII": ["Red XIII"],
	...
```

### Aliases

Sometimes, a character has multiple names in the script. This can happen if: 

-  The character is disguised as another character (e.g. Prince Edgar is transformed into King Otar in King's Quest VII). 
-  The character speaks before revealing their name (e.g. Aerith in Final Fantasy VII) 
-  The name is shortened (e.g. "Red" instead of "Red XIII" in Final Fantasy VII) 
-  There are stage directions in the name (e.g. "Cara [to Mid]" in Final Fantasy V) 
-  There is variation in upper case/lower case letters (e.g. "Shinra manager" and "Shinra Manager"). 
-  There is a typo in the script. 

These issues can be fixed by adding alias information to the metadata. This is placed after the "characterGroups". It includes a list of 'wrong' names and what they should be corrected to. E.g. below all instances of "Flower girl" are converted to "Aerith". 

```json
"aliases": {
		"Flower girl": "Aerith",
		"Aries": "Aerith",
		"Muuki": "Mukki",
		"Red": "Red XIII",
		"Shinra manager": "Shinra Manager",
		"Village headman": "Village Headman",
		...
	}
```

Some scripts assign one line of dialogue to multiple characters if they're saying the same thing at the same time. This can lead to some 'character names' like "Cloud & Aerith". These can be split into individual lines for each character by using a list in the aliases (instead of just a character name string):

```json
"aliases": {
	...
	"Cloud & Aerith": ["Cloud", "Aerith"],
	"Biggs & Jessie": ["Biggs","Jessie"],
	"Biggs, Jessie, & Wedge": ["Biggs","Jessie", "Wedge"]
	}
```

Sometimes, multiple characters are given the same label if they are not known to the transcriber or the player at the time of speaking. Characters can be identified by line of dialogue. In the example below, the label "???" is converted based on the line of dialogue. For example, if the dialogue matches "Ha ha ha ha. I'm so ...", then it will be converted to "Birdo":

```json
"aliases":{
			"Elder":"Real Elder",
			"Toadn":"Toad",
			"???": {"Birdo": ["Ha ha ha ha. I'm so ... lonely. Will you play with me?",
							  "Oh ... If you had played with me, I was going to give you the key to",
							  "this room.","Thanks!"],
					"Jinx": ["You did well for your inexperience, Jagger."],
					"Geno": ["Stop! Hold it right there! You don't know what you're doing. ",
							"I serve ... a higher authority ... That Star Piece belongs to everyone.",
							"Hey! Chill out!",
							"Stop it! That's enough.",
							"Thanks for the help! But ... who are you?"]
					  }
			}
```

Note that:

-  Matching is done by checking if the dialogue in the script *starts with* the line of dialogue in the metadata, so there's no need to include the whole line, just a recognisable portion.
-  If a line of dialogue in the script does not match any of the lines in the metadata, the name remains as it is.
-  Alias changes apply during parsing, so the incorrect names won't appear in the script. Therefore, when including aliases, the names in the "characterGroups" list should reflect the corrected name or individual name, not the original name.
-  A "default" character name can be used that covers all instances that are not listed (thanks to the way that `startswith()` treats the empty string). In the example below, the dialogue for "Voice" is delivered by the Mist Dragon, except for one line by Scarmiglione:

```json
	"Voice": {
				"Scarmiglione": ["Such pleasure I will take"],
				"Mist Dragon": [""]
			},
```

The order is important here - the default should come last. 

### Error checking

This section describes the procedure for error checking in order to ensure that the data is accurate and representative.

If the data source is directly from the game files, then only the check for false positives and parsing errors is required. Otherwise, both tests below are required.

After the checks have been carried out, the results should be added into the metadata after the “source” entry. for example:

```json
"errorChecks": {
  "truePositive_numTestsDone": "5",
  "truePositive_numParsingErrors": "0",
  "truePositive_numSourceErrors": "1",
  "truePositive_notes": "One line inaccurate transcript: [EXAMPLE]",
  "falsePositive_numTestsDone": "5",
  "falsePositive_numErrors": "1",
  "falsePositive_notes": "Parsing error: no space after full stop."
}
```

A Github issues should be raised for any problem that could potentially be fixed. 

#### Check for true positives and transcription errors

Follow the procedure below to check for true positives (lines that are in the source that are in the game) compared with transcription errors (lines that may have been miss-transcribed in the source).

1. Find a video on YouTube of someone playing the game. Try to find one that documents an entire play through the game (rather than clips), without mods, and that is not a speed run or specialist run (e.g. pacifist). Typically, “let’s play” videos will be suitable.

2. If a run is split over several videos, choose one at random.

3. Choose a random place in the video. This website will help you do that: https://correlation-machine.com/VideoGameCorpus/randomVideoLocation.html 

4. Find the next piece of dialogue. If you reach the end of the video, loop around to the beginning. Look at up to three lines of dialogue that are spoken together.

5. Search the data.json file to answer:

-  Does the dialogue in the video exist in the corpus? (ignoring small errors in punctuation, capitalisation, and also ignoring typos - the question is whether the line is represented somehow)
-  Is the text of the transcript of the video accurate? Note that consecutive lines spoken by the same character are collapsed into one line in the corpus.
-  Is the structure of the conversation correct? (Are options defined in “CHOICE” structures? Are all options available? Does the sequence match?). Note that the dialogue in the game may be randomised, optional or status-dependent, so all lines in the corpus may not appear in the video. The question is whether the dialogue in the video is covered by the corpus.
-  If there are any errors, can we identify the source?
    -  Error in parsing program.
    -  Error in original transcript source.

Repeat steps 2-5 for 5 parts of the video.

#### Check for false positives and parsing errors

Repeat the following procedure 5 times to check for false positives (lines in the source that are not really in the game) and parsing errors (lines that are in the data, but parsed incorrectly in terms of character assignment or dialogue structure).

Pick a random line in the corpus data.json file. Confirm that:

-  The character name is plausible (not some possible parsing error like “and so”).
-  There are no strange typographic characters.
-  There are no obvious parsing errors (e.g. another character’s dialogue line enclosed in the dialogue string, words not separated properly). If it is possible, find this line in the source transcript. This might involve finding the location of the source in the meta.json file, then using a google search like: "site:http://www.yinza.com/Fandom/Script/ “This is a church in the”"
-  Confirm that the line in the source has been correctly parsed into the corpus.

##  Processing

Folder of python scripts for downloading and parsing raw scripts.

### parseRawData.py

Iterate over all games and parse raw data. You can also parse text for just one game:

```bash
> python3 parseRawData.py ../data/FinalFantasy/FFVII
```

### getStatistics.py

Iterate over all games and calculate and compile statistics. Stats files are written to the data folder for each game.  You can also re-compile stats for just one game e.g:

```bash
> python3 getStatistics.py ../data/FinalFantasy/FFVII
```

### getCharacterInfo.py

Attempt to automatically identify an attribute for each character using a specific wiki. The source for the wiki is included in the "characterInfoSource" property of the metadata. Must be run with a specific game folder as an argument. Creates the file 'autoCharInfo.json' in the game's data folder.

###  parsers module

A list of parser modules for different source types. Each parser must iniclude a function `parseFile()` with arguments:

-  fileName: path to a raw file to parse (usually in the game data folder's 'raw' folder)
-  parameters (optional): dictionary of parameters for the parse. These can vary for each parser. Defaults to an empty dictionary.
-  asJSON (optional): boolean. If False, the function should return the parsed data as a list of dictionaries with the character name as the key and a line of dialogue as the value. If True, the function should return the same format, but with a JSON header and as a string (suitable for writing to the game data folders). Defaults to False.

When creating a parser, remember to add it to the __init__.py import call.


## Gitignore

The gitignore file should include the following:

```
# Data files
raw/
__pycache__/
processing/*.txt
.DS_Store
data/ALL/*

# History files
.Rhistory
.Rapp.history

# Session Data files
.RData

# User-specific files
.Ruserdata

# knitr and R markdown default cache directories
*_cache/
/cache/

# Temporary files created by R markdown
*.utf8.md
*.knit.md
```