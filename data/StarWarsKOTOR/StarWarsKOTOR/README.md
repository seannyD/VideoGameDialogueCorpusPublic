# Star Wars: Knights of the Old Republic

## Source

This is from game data from [this repository](https://github.com/hmi-utwente/video-game-text-corpora/blob/master/Star%20Wars:%20Knights%20of%20the%20Old%20Republic/data/dataset_20200716.csv) of the work by:

van Stegeren, J. & Theune, M. (2020) Fantastic Strings and Where to Find Them: The Quest for High-Quality Video Game Text Corpora. In proceedings of Intelligent Narrative Technologies Workshop, AAAI Press.

The original game data includes mappings between dialogue and character models. The mapping between character models and dramatic characters has been coded by hand, including identifying "conversation owners" (see "ConversationOwnersToCode_complete.csv").

There appear to be some missing parts that may be filled by variables. For example, this line seems fine:

```
{"Taris Citizen (Upper City South)": "Hey - didn't you just win the big swoop bike race in the Lower City? Yeah, it was you, I'm sure! That race was amazing!", "_ID": "15645"},
```

But then this line does not include a location:

```
{"Lower Taris Citizen 1": "Hey - didn't you just win the big swoop bike race in? Yeah, it was you, I'm sure! Best race I ever saw!", "_ID": "17125"}
```

The "race in?" line is in the source file and has been parsed correctly. It's possible that various options could fit after "in", but that's not represented anywhere in the source.


## Gender Coding

Being a Star Wars game, there is a considerable amount of external lore associated with the species and characters featured. The wiki was used more heavily than with coding some other games (https://starwars.fandom.com/). Many of the alien species are sexually dimorphic, with particular physical characteristics indicating an individual is male or female. There is some information about how gender/sex are treated in-universe here: https://starwars.fandom.com/wiki/Gender/Legends.

Details of the "Alien Prisoner" available here: https://strategywiki.org/wiki/Star_Wars:_Knights_of_the_Old_Republic/North_Apartments. 

Some droids in the Star Wars universe (such as C-3PO, or in game, "C8-42") have gender conferred on them, but many do not. The "Overseer droid", for instance, is discussed in the wiki as 'it', and its visual appearance has no obvious gender signifiers. I've coded it as neutral, but this could be revisited if it were determined, for instance, that droids were better understood as genderless. From the wiki (https://starwars.fandom.com/wiki/Gender/Legends): 
>Droids, which were self-aware automata designed to perform tasks for organic beings, could have masculine programming or a feminine personality; if so, they would be addressed as and refer to themselves with the associated pronouns instead of "it."

The Matale Droids are humanoid in appearance and have male voice acting, so I have coded them as male. "Matale Droid" might well be a generic. The same applies to the Sandral droids. 

"Bith" is instead referred to as a "Duros" here (and indeed, in the video appears to be a Duros): https://strategywiki.org/wiki/Star_Wars:_Knights_of_the_Old_Republic/South_Apartments. Coded male in accordance with the pronouns used at the link and the voice acting. He also appears later in the Sith Base. 

The "Black Vulkar" who surrenders is a Twi'lek male (seen https://strategywiki.org/wiki/Star_Wars:_Knights_of_the_Old_Republic/Black_Vulkar_Base). 

"BlackVulka034" and "BlackVulka035" are two members of the Black Vulkars gang seen talking to Davik's Agent here: http://i.imgur.com/TkQXgHw.png. Coded as male because the agent refers to them as "guys" and "boys". 

"BountyHunt022" details here: https://starwars.fandom.com/wiki/Unidentified_Human_bounty_hunter_(Upper_City); "Bountyhunt023" details here: https://starwars.fandom.com/wiki/Unidentified_Aqualish_bounty_hunter_(Upper_City). Both male. 

"Dark Jedi Master" - https://starwars.fandom.com/wiki/Unidentified_Dark_Jedi_Master_(Manaan)?so=search. 

Conversation between DuelSpec1 and DuelSpec2 can be seen here: https://youtu.be/tcXQFH2l-cM?t=220. 

The Rakatan Guide has details here: https://starwars.fandom.com/wiki/Unidentified_Elder_Rakata_(Guide). 

Based on appearance (and without conflicting evidence), I think the "Hidden Bek (Aqualish)" will be read as male by players, so have coded accordingly, but this could be revisited. 

"HiddenBekCompGuard" is a Rodian, and appears from the character model to be male (female rodian have breasts according to the wiki). 

"Information Droid" details here: https://starwars.fandom.com/wiki/Unidentified_information_droid

"Iridorian Mercenary": https://starwars.fandom.com/wiki/Unidentified_Iridonian_mercenary

"Sith Master": https://starwars.fandom.com/wiki/Unidentified_Sith_Master_(Lehon)

Where the "K-X12a Battle Droid" and its compatriots replay a recording from Marlena Venn I've attributed that line to Marlena with an alias. 

"Lower Taris Citizen": these lines can be spoken by any of four male characters (https://strategywiki.org/wiki/Star_Wars:_Knights_of_the_Old_Republic/Javyar%27s_Cantina), thus the aliases. From this https://strategywiki.org/wiki/Star_Wars:_Knights_of_the_Old_Republic/Undercity it looks like the male and female infected outcasts have the same lines recorded, so I've added aliases so that we count both of their lines. As best I can tell from this https://strategywiki.org/wiki/Star_Wars:_Knights_of_the_Old_Republic/Courtyard and from videos (which seem to show both settlers having the same voice actor), "Settler" lines can be spoken by either of the two female settlers outside the jedi enclave. I've indicated as much with aliases. "Sith Archaeologist" looks like it could be multiple people https://strategywiki.org/wiki/Star_Wars:_Knights_of_the_Old_Republic/Valley_of_Dark_Lords - I couldn't track them all down so have coded as neutral. One set of "Sith Guard" lines looks to be voiceable by two NPCs (https://strategywiki.org/wiki/Star_Wars:_Knights_of_the_Old_Republic/Valley_of_Dark_Lords) (it's also duplicated by the "Sith Patrol"). 

There are multiple Sith students that utter the same set of generic lines. I'm not sure of their number or gender distribution, so have just coded "Sith Student" as neutral (where it doesn't refer to a particular unique NPC). 
Where possible I've separated out particular mercenaries/echani mercenaries. There is likely more work to be done here. The same goes for some of the other generics.

"Noble Youth" can be seen in the Upper City cantina near Gana Lavin (the two Sith Patrons are in this room too). 

Details for "Noble021": https://starwars.fandom.com/wiki/Unidentified_Tarisian_noble

The "Rakghoul Victim" who speaks here is female: https://youtu.be/Wj6ZFM-9bmA?t=644, so I've coded accordingly. 

I've split out the "Sith Soldier" into the various characters with that alias. Some are difficult to track down in-game, e.g. "Patrolling Sith Soldier (Ahto City East Central)" - for now I've coded them as neutral where I don't have contrary evidence but this could be revisited. 

There are three "Sith Thug" characters in the conversation with the "Sith Thug Leader". Two are male and one female. I've identified the lines where I could from youtube videos, but with the others have left them as neutral. This could be revisited upon replaying. 

From this - https://strategywiki.org/wiki/Star_Wars:_Knights_of_the_Old_Republic/Ahto_East - it seems that some of the swoop fans share lines and there's a male swoop fan with a particular set. Noticeably, that particular set contains male PC-specific lines that are quite flirtatious. Of the generic lines, some are spoken by human and alien swoop fans, and some by only the humans. I've indicated as much with aliases. 

Half of the "Swoop Groupie" lines belong to a female NPC, as detailed here: https://strategywiki.org/wiki/Star_Wars:_Knights_of_the_Old_Republic/Swoop_Registration. Contextual clues in the remaining dialogue suggest the rest is probably a Male Swoop Groupie, e.g. 
>"You're beautiful out there, absolutely beautiful. And a pro racer as well!", "_ID": "19576", "_Emotion": "Flirt"

>"Lady, you are the best. I just had to say that.", "_ID": "19577", "_Emotion": "Flirt"

>"I've never seen a woman come into town and take charge like you did out there. You are scary. Wonderfully scary."
However this is just a best guess and could be revisited. 

It wasn't clear if T3M3 was a typo for "T3-M4" (also sometimes written as "T3M4"). There don't seem to be character records/wiki mentions for a T3-M3. I've coded as neutral given the uncertainty (and T3M3 only has one line of dialogue), but this could be revisited. 

The "Tach" lines are Rulan shapeshifted - https://starwars.fandom.com/wiki/Rulan_Prolik. There are a series of other lines uttered by Rulan while shapeshifted into characters of various genders (e.g. Bastila, Mission, Zaalbar). Because the player knows these are Rulan in disguise, I've coded them all as Rulan (and thus male), but note that the imitation is supposed to be uncanny - they could be counted differently. 

The three "Taproomvic" characters are a rodian (31), and two Twi'leks (32 and 33) from the Black Vulkars. 

"Taris Merchant" appears to be a generic set of dialogue shared by multiple NPCs (https://strategywiki.org/wiki/Star_Wars:_Knights_of_the_Old_Republic/Upper_City_North) - have coded neutral given difficulty tracking them down; this could be revisited if replayed. The same seems to be true for "Traveler" on Manaan. 

"Trandoshan" is in fact two identical looking Trandoshans. I've split the lines between them following play through videos (e.g. https://youtu.be/M56k_nbE81A), but in some cases have had to guess which line belongs to which. It shouldn't affect the results significantly (they mainly appear in one scene, and briefly another), they are identical in appearance), but it's worth noting. 

"Twi'lek" is this one: https://starwars.fandom.com/wiki/Unidentified_Twi%27lek_messenger. "Aqualish (North Apartments)" is this one: https://starwars.fandom.com/wiki/Unidentified_Aqualish_(North_Apartments). 

"Vulkar Bartender" pictured here: https://strategywiki.org/wiki/File:KotOR_Model_Vulkar_Bartender.png. Some of the Vulkar lines seem to come from the cut third floor of the Vulkar Base, which was intended to include a Spice Lab and other areas (https://starwars.fandom.com/wiki/Black_Vulkar_Base) - they are missing from the strategy wiki, for instance. I've coded neutral where evidence is unavailable. 

There are sets of lines for male and female wookiees respectively, but they might be uttered by multiple NPCs. I've divided them into "Generic Male Wookiee" and "Generic Female Wookiee" in accordance with https://strategywiki.org/wiki/Star_Wars:_Knights_of_the_Old_Republic/Village_of_Rwookrrorro. Based on body shape, I think the wookiee guards are all male - they are taller and thicker set than the identified female wookiees. The "Wookiee Rebel" lines are uttered by multiple NPCs - I've coded as neutral as they're difficult to track down without playing the game. 

Garrum and Tar'eelok were cut from the final game (https://starwars.fandom.com/wiki/Garrum_(apprentice)?so=search), but a conversation remains in the game files (and thus the source); a mod restores this content. 

"Citizen of Anchorhead" lines are spoken by multiple NPCs (https://strategywiki.org/wiki/Star_Wars:_Knights_of_the_Old_Republic/Anchorhead); I've coded neutral given difficulty of determining how many/which but this could be revisited upon replaying. The same applies to "Czerka Trade Officer". 

The "Computer" speaks to the player via a hologram of a male rakata. 

The "Czerka Guard" NPCs tend to be male. The one in Dreshdae can be seen in the background here: https://youtu.be/YTTV0Zr68u0?t=383. It's not always clear whether lines belong to "Czerka Guard 1 (kill wookiee)" or "Czerka Guard 2 (kill wookiee)" (as they're not distinguished in the file, and it's not possible to track down video of every possible party configuration going through this scene), but generally in such cases the lines are divided equally between the two, so I've approximated that here. 

Based on this description: 
>"Two Czerka merchants stand by the hand rail on the right, on the south side of the walkway as it curves north" (https://strategywiki.org/wiki/Star_Wars:_Knights_of_the_Old_Republic/Czerka_Landing_Port), 

the two Czerka Merchants are seen here on the right: https://youtu.be/HvZGqR4ZkCY?t=64

"Duel Spectator" is multiple NPCs. There is a set of lines for female spectators and one for males, but it's not clear how many of each NPCs are present. I've coded one of each as a generic. 

There is more than one Duros Miner (and they share lines), but it's not clear how many, so am coding as singular for now. 

It appears as though all the generic rakata are male (or will be perceived as such by players) - they have identical body types (while the wiki says female rakata are more slender), and they speak with the same voice. This could be revisited. 

Twi'lek Receptionist: https://starwars.fandom.com/wiki/Unidentified_Twi%27lek_receptionist_(Tarisian_military_base)

Insufficient evidence to determine gender of Jawas 1, 2, 3 and the generic. They have high-pitched but indeterminate voices, and because of their cloaks, no particular gender signifiers. Coded as neutral, but could be revisited. (Certain Jawa, like Iziz, use gender pronouns to refer to themselves. That isn't the case here. )

The patrolling Republic Soldiers on Manaan seem to all be male (there are multiple instances of the same character model). 

The Selkath are tricky - they all share a character model, and they speak with the same deep voice. Several are described with male pronouns with the noticeable exception of Shasa, who looks and sounds the same as the others, but is described with female pronouns and as a daughter. Listening to playthroughs (e.g. https://youtu.be/TvKcv9lePWc) players seem to read the selkath as male, and this matches my experience. In other Star Wars media, selkath females are distinguishable by "the presence of tendrils on the back of their heads" (https://starwars.fandom.com/wiki/Selkath/Legends), which are absent in KOTOR. Given we're tracking likely player-conferred gender, I've coded the other selkath as male unless there is evidence to the contrary. 

Selkath apprentices with Shasa: I've used playthrough videos to determine which lines are spoken by which of the three (identical) NPCs. I'm confident that only the lines spoken by those three have been attributed to the group, but not that each line is correctly attributed to the right one of the three. (Given their indistinguishability and relatively small number of lines the impact of any errors is unlikely to be meaningful). 

As is typical for generic guard-type characters, Sith Troopers are generally in full armor and tend to have male voice acting. "Patrolling Sith Trooper (Taris)" is a generic. 

"Republic Officer" is heard here: https://youtu.be/GOLCtyUSSes?t=1301. 

You can fight up to three "Captive Republic Soldier" NPCs, hearing a selection of their dialogue each time (as detailed here): https://strategywiki.org/wiki/Star_Wars:_Knights_of_the_Old_Republic/Sith_Academy. The NPCs are indistinguishable. I've coded it as male, but note its a generic rather than a specific character. 

"Elder Worshipper" is a generic - there are multiple indistinguishable elder worshippers. 

There are five "Guard" NPCs who share a set of lines. Details here: https://strategywiki.org/wiki/Star_Wars:_Knights_of_the_Old_Republic/Upper_Shadowlands

"Protocol Droid" is a generic. Coded neutral, but this could be revisited. 

The "Rakata" lines from different sets, but each are generics. I've split them out with aliases. 

There are multiple generic sets of dialogue for "Taris Citizens" - usually these are gender-specific (so a set will be allocated either to various female NPCs or to male NPCs). See for examples: https://strategywiki.org/wiki/Star_Wars:_Knights_of_the_Old_Republic/Upper_City_Cantina. Where the allocation is mixed, I've coded neutral. 

There are duplicated Bastila lines in the game data that look to be leftover test dialogue - I've labelled it accordingly so as not to double-count Bastila's lines. 
