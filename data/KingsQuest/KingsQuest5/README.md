# King's Quest V

## Source

This is from a dump of the game files from the NES release.

However, there seem to be some lines that appear in the game that are not included in this source. For example, [this video](https://youtu.be/XEydkEz6tUQ?t=5826) shows extra dialogue:

```
{"Cedric": "See! Dead end! Let's go back now!"},
{"Graham": "No! I'll figure this out!"},
```

These lines are included in the source for the [original floppy version](https://kingsquest.fandom.com/wiki/KQ5_transcript), but not the [CD version](https://kingsquest.fandom.com/wiki/KQ5CD_transcript). However, the source for the floppy version doesn't indicate who is speaking, and the source for the CD version only notes the differences. So the NES release is the best choice for parsing. 

Some dialogue is dependent on others. For example, when entering a shop, you get the text "Please select something.", then the item descriptions appear as you select items. https://youtu.be/Bcv8RUWKrEg?t=478. This structure is not coded.

The site notes that the line "Mooaaann!" is likey Cedric.

## Coding

No voice acting in NES version, so 'narrator' uncoded (as it's not obvious it's a voice versus system messages in terms of player experience). May be revisited. (Edited to add: On second pass coded as 'neutral', in keeping with subsequent decision to code all dialogue.)

In the CD-Rom version, 'rat' is a mother rat. It's less clear from the NES version (where it sometimes called 'The Mouse'), so I have coded as neutral. 

Yeti is referred to as "he"
