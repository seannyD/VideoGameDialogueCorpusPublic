# The Elder Scrolls IV: Oblivion

## Source

Data is from the game files directly (list of audio files and transcript). This covers all audio dialogue from NPCs. There is no dialogue included from the PC. The PC is mostly silent, but occasionally the player gets to choose what the PC character says. This only appears as written text in the options, and is not voice acted. This is not included in the source.

Each line in data.json file also includes data on:

-  "_Race": Race of the NPC.
-  "_Group": Affiliation of the NPC.
-  "_Emotion": Which facial emotion animation plays for this line, including the emotion type and the intensity.
-  "_Quest": Code for the quest that the dialogue is part of.

## Gender coding

Gender is assigned in the source file itself, so the list of characters is auto-generated. 

The characterGroups list also contain 'GenericFemale' and 'GenericMale' groups, which are subsets of the 'male' and 'female' groups for characters that are not named. That is, all generic characters are also members of 'male' or 'female'.