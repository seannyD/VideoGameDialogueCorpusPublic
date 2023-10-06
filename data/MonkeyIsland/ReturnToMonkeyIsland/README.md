# Return to Monkey Island

Dialogue in English, Japanese, French, Cantonese, Russian, Spanish, Korean, Italian, German, Portuguese. 

Yack files can be extracted from game files using [ggtool](https://github.com/jonsth131/ggtool)

```
./ggtool extract-files PATH_TO_RMI_RESOURCES/Weird.ggpack1a "*.yack" . decompile-yack
```

And extract the localisations:

```
./ggtool extract-files PATH_TO_RMI_RESOURCES/Weird.ggpack1a "Text*" . decompile-yack
```

Currently, the dialogue is extracted without the dialogue structure. But the full logic is accessible.

Note that some of the dialogue does not appear in yack files, so is added after from the localisation strings.

Guybrush's monologue to himself when describing things etc. is listed under a character name "Guybrush (internal)", and is counted in the 'neutral' category, since it's not true dialogue.


## Characters

According to [this video](https://www.youtube.com/watch?v=YX5e4n-JtKA):

-  "Youngpirate4" is on the dock.
-  "Youngpirate2" is in the Scumm Bar and has a red hood.
-  "Youngpirate1" is in the Scumm Bar had has an eyepatch.

There are both male and female prisoners, but it's hard to tell which is which because they have overlapping dialogue. Similarly, the Brrrmudians don't differ much in their speech. It might be possible to get the identities of prisoners from their character sprites or locations on the map, or from recordings.
