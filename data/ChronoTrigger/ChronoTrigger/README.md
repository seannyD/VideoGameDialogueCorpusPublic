# Chrono Trigger

The source here is based on a [retranslation project by a fan](https://www.chronocompendium.com/Term/Retranslation.html). It includes a parallel text of lines from the original English translation, Original Japanese, and a retranslation by the fan. The retranslation is often a more faithful translation, and also makes the lore more consistent. Notes from the translator are included at various points.

The source here has been parsed with a combination of automatic script and a manual parse of some of the choices (see QuestionSplitter.xlsx).

## Gender coding

Split out different "Innkeeper" characters and fixed "Inn keeper" typo with alias. 

There are multiple poyozo dolls in the game, as detailed here (https://chrono.fandom.com/wiki/Poyozo_Doll). Original coding has them as a single character, which I've left unchanged. Note that 'poyozo' and 'poyozo doll' are distinct in the source - 'poyozo' calls themself the 'piano man', and according to the wiki isn't a poyozo but rather a 'Kilwala'. I've changed their coding to male.

The sprites for soldiers in the game (http://www.videogamesprites.net/ChronoTrigger/NPCs/Townsfolk/Soldiers.html) read as though intended to be male, especially in light of other Square Enix games of the era. I've changed the coding accordingly. Note that there isn't a single soldier but rather this is a generic name for the class of NPCs (the same is true of "knight"). The Knight Captain talks about his 'men'. I'm not sure about "guard"/"guards" so have left neutral (these appear to be fiends in at least some cases). 

"Knight Captain" is talked about using male pronouns in game. Same with "prophet". 

Although artificial, 'Mother Brain' reads to me as female (and self-identifies with the 'mother' epithet) and so I've coded accordingly. 

Changed coding for some formerly neutral characters (e.g. waitress, mistress, judge). For others used sprites available here: http://www.videogamesprites.net/ChronoTrigger/NPCs/ and maps available here: https://www.snesmaps.com/maps/ChronoTrigger/ChronoTrigger1000PorreTicketOffice.html

I've left 'Sir Krawlie' as neutral, as it isn't obvious that the honorific isn't itself neutral in this context (the retranslation uses 'sama', and the sprite isn't obviously gendered)

"Dream Team" consists of all male characters, so moving from 'neutral' to 'male' (haven't split them out as I'm not sure which of them is speaking in these instances; this could be revisited.)

"Dumb" and "Dumber" are viper sprites - not obviously gendered. However the wiki uses male pronouns and given their film namesakes, it would be unsurprising for audiences to read them as male. I've coded accordingly, but this could be revisited. 

"Servant" is a female sprite - https://youtu.be/ezBq-mQVd3s?t=81

"Dancers" appear here: https://www.snesmaps.com/maps/ChronoTrigger/ChronoTrigger65mMeetingSiteN.html It looks like a mix of male/female sprites. 

"owner" is the owner of Dorino Inn. "village chief" is the porre elder from 600AD. 

"chancellor" is the 1000AD version (really Yakra XIII in disguise). I've added aliases for the other instances. 

There are multiple "nu" - https://chrono.fandom.com/wiki/Nu. All generically coded neutral. 
"strange creature" is the nu that serves as Belthasar's assistant (and contains some of his memories). Have left coding as neutral but could be revisited. 


"flea" is coded as male, e.g.:

>  Frog: Keep your guard up! This is no ordinary woman! Meet Flea, the magician!
>
>  Flea: What the...?! Hey, I'm a GUY!

The "diary" is Lucca's diary. Though this isn't counted as dialogue.

The game includes a secret room with the developers as NPCs. https://www.youtube.com/watch?v=xpbZtAKUksk Information on one developer "akane haruki" was not available to code their gender. Akane is a female name, but the NPC may be a rodent?
