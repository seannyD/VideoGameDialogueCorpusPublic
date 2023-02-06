# Stardew Valley

## Source

The dialogue source files for Stardew Valley used to be publicly available, but they have been removed recently. If you have the game files locally, convert them to yaml and copy them over to the 'raw' folder.

From [this modding guide](https://stardewvalleywiki.com/Modding:Dialogue):

>  "Character dialogue is stored in many different files: The Characters\Dialogue directory is where the majority of NPC-specific dialogue is stored. Data\ExtraDialogue.xnb, Strings\Characters.xnb, Strings\Events.xnb, Strings\SpeechBubbles.xnb, and Strings\StringsFromCSFiles.xnb contain various other pieces of dialogue, some generic, and some NPC-specific."

The source here is the game data for in yaml format. This includes:

-  Character dialogue
-  Marriage dialogue
-  Event dialogue

There are some lines of dialogue that are not captured in the types above. For example, responses of NPCs to giving them items are not included in these files. These seem to be partly procedurally generated, e.g. Elliott being offered a flower says "Hmm, I'm not a huge fan of this". see [here](https://youtu.be/JPCBG8KDZOI?t=1079)

Television reports (such as weather report, fortune teller) are missing from the source file. Some sidequest dialogue (eg Willy fishing quest) is missing too.

Example of difference in male vs. female player:

https://youtu.be/IoThzxp1UL4?t=157
https://youtu.be/l80vb_s7aRQ?t=53

## Gender coding

According to https://stardewvalleywiki.com/Dwarf:
"The Dwarf's gender in the game data is "undefined" (see Content\Data\NPCDispositions.xnb)."