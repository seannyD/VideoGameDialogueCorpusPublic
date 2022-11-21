# Dragon Age: Origins

## Gender Coding
In Dragon Age, most species/races have two basic character models for bodies (faces are more customisable): male and female (labelled as such during character creation, with the same models being used for NPCs). So, for instance, there are male and female human models, male and female elf models, and so on. These have typical secondary sex characteristics, and clothing consistently appears differently on male and female bodies (e.g. 'leather armour' has a different visual appearance on a female character than a male character.)

Demons can appear in various forms, although their 'true' forms are singular for each type (so all desire demons are identical, so are all pride demons, sloth demons etc.). Desire demons appear female (pronounced secondary sex characteristics) and are often talked about as such in-game (for instance, the Desire Demon possessing Connor in the Arl of Redcliffe quest speaks about herself in the third person using female pronouns, the Desire Demon bewitching the templar is referred to by party members using female pronouns etc.). Other demons are often talked about as male. Some, like 'Mouse', are seen in multiple forms - I've coded Mouse as male due to his humanoid appearance and voice acting. 'Spirit of Valor' appears in the guise of a male templar with corresponding voice acting - although Mouse calls him 'it', I have coded him as male given how he manifests to the player. "Sloth Demon (Bereksarn)" in the mage origin is referred to with male pronouns and has a male voice actor, and later sloth demons are likewise characterised as male in-game. 'The Spirit of Rage' has a deep masculine voice.

Shale is an interesting case. She is a golem, transformed from - as the game reveals - a female dwarf. For much of the game Shale doesn't remember her history, and there is nothing in her appearance or voice acting that indicates a particular gender (although she does exhibit some behaviour stereotypically associated with women - e.g. checking that her crystals are slimming, showing a penchant for glittering from ear to ear etc.). As the wiki notes (https://dragonage.fandom.com/wiki/Shale):
>"To capture the ambiguity of Shale's gender, the voice actress's already gravelly voice was pitch-shifted down to sound deeper and more masculine."

However, this ambiguity seems to serve a narrative purpose rather than being a commentary on Shale's actual gender, and her narrative arc is likely to affect player's experience of her gender: Shale comes to learn of her previous identity during the game, and displays different sentiments about it as she processes the discovery, e.g. 

>Leliana: I did not realize that you were a woman.
>
>Shale: That is because I am not. I am a golem.

>Morrigan: I am simply finding it difficult to believe that there is a woman inside of there. 
>
>Shale: A woman who was also a warrior. And a dwarf.

In the epilogue slides, the game uses female pronouns to describe Shale, and in at least one version, implies she has regained her original dwarf form. Wynne also uses female pronouns to describe her, and multiple party members talk to Shale about her gender. In a subsequent text (Asunder), we see Shale trying to work out how she might return to her prior form. I have coded Shale as female, but this could be revisited. Notably, this is likely to reflect player experience if they have completed the game, but may not do so if they have only experienced part of the game.  

The Lady of the Forest is a spirit bound to the body of a wolf. She is referred to by female pronouns by various characters throughout the game, is frequently called "Our Lady" or "The Lady", and in humanoid form is almost entirely naked with female secondary sex characteristics. The Grand Oak is a less clear cut case: it's a spirit bound to a tree. However, the voice acting is male, and I so I have coded it as male (it has a bit of a Treebeard vibe). This could be revisited. 

There are some lines of dialogue that were cut from the game (but are still present in the game files). Where these were identifiably new characters unseen in the game I've coded them as belonging to a new group - "cut" - as they aren't part of what the player experiences. These include: Pomer the Guard, Young Pickpocket, Stanley, Mitteran, and others. There is a bugged quest - Jowen's Intention - that can be played on PC by debugging; since Jowan is a character beyond this quest, I have left this dialogue in (but if one wanted to ignore this dialogue, one could identify it by changing the alias for "OWNER_r_pln_jowan"). At least some of the dialogue that is assigned to characters starting with "OWNER_zz_ss" might have been cut, but it's difficult to determine which lines without multiple playthroughs (some of the lines are reactions to attempted stealing, or ambient comments). The wiki notes (https://dragonage.fandom.com/wiki/Cut_content): 
> Another quest tree similar to Favors for Certain Interested Parties would have been included. 

From context I think this is the Rogue Board quest line, for which some dialogue is still in the game (I've coded it as "cut") - indeed it appears in a "cut content" video on the same page. It's not clear if the Desperate Merchant, Grim Guard and Gravedigger from Redcliffe were cut from the game, or if they appear if Redcliffe Village was destroyed (as videos showing the destruction only go up to the end of the Connor questline, rather than showing the village later in the game). I've coded them as neutral for lack of evidence. I think the Market Patrons are cut content from the propagandist quest, so have coded them accordingly. 

The Mages' Collective Liaison appears in Denerim, Lake Calenhad and Redcliffe Village. This isn't a repeated (generic) NPC, as the wiki notes (https://dragonage.fandom.com/wiki/Mages%27_Collective_Liaison): 
>"He is treated as a singular character by the in-game mechanics and so can only be stolen from once." 

The same is true of the Blackstone Liaison (https://dragonage.fandom.com/wiki/Blackstone_Liaison). 

In the "Notices of Death" quest, the player must alert four widows to their husbands' deaths. There is a set of four lines, one of which is assigned each time you give the news (with the possibility of repeats) - see for instance https://youtu.be/slN0ZkvunLo. However, you only hear one line per widow (the interaction can't be repeated with a single window). I have assigned one of the lines to each widow manually (with aliases), but note that this is only one possible configuration. (All characters are female, so it doesn't materially affect the count.)

Some of the Mage Origin apprentices have duplicates (or perhaps they just move around, it isn't clear). Nonetheless, their categorisation remains consistent (if they are a female human, each instance is a female human, if they're a male elf, each instance is a male elf, and so on). 

"Templar (Circle Tower)" is a generic. There are multiple indistinguishable male templars in the Circle Tower. Likewise, "Lothering Chantry Templar" is a generic - there are multiples, e.g. standing by Ser Bryant; standing near to door to Miriam etc. 

The gender of abominations can be hard to identify, e.g. "Elite Abomination (Circle Tower)" seen here: https://youtu.be/W7Uz8to5zIY?list=PLL5LBLM9GP5fG0R1PSKgev4K1UMH27EWF&t=590. Where there is insufficient evidence, I've coded as neutral. 

While in the Fade, duplicates of some characters appear (something similar occurs during the quest for the Urn of Andraste, during the Trials). Although these aren't real instances of the characters, they look and sound the same, so for our purposes I've coded them as the same (e.g. Duncan in the Fade is just coded as Duncan). Those with other purposes might want to handle this differently, which is possible by looking at the location codes in the aliases - e.g. cir denotes Circle Tower, from where the player accesses the Fade, cir300-cir350 are fade locations, so "OWNER_cir350_duncan" is Duncan in the Fade. Information about characters represented in the Fade is available here: https://dragonage.fandom.com/wiki/The_Fade:_Lost_in_Dreams. 

I couldn't track down "Crazy Chef"/"Crazy Cook". There are a handful of other characters I likewise couldn't find, whose appearance depends on particular conditions being met (and thus they're less likely to appear in playthrough videos/documentation). They are coded as neutral. 

There is some temporary/test dialogue still in the game data - I've labelled it as "SYSTEM" (e.g. Temp Man). Likewise for placeholder text for cutscenes. 

Although the game files indicate he was originally supposed to be a dwarf ("OWNER_lot100_dwarfmerch") the Lothering Merchant ("Unscrupulous Merchant") is a human: https://dragonage.fandom.com/wiki/Merchant_(Lothering). 

"OWNER_lot120_priest_m" - was previously coded as "Chantry Brother (Dane's Refuge)", but upon replaying, both the priests in the pub are female (whereas the bulk of the rest of the patrons are male) - I noted while playing that they each mention listening to the bards' song but with slightly different lines; this corresponds with the data. Recoded as "Chantry Sister 2 (Dane's Refuge)". 

All of the dwarves in the Deep Roads for the Noble Expedition quest appear to be male - see https://static.wikia.nocookie.net/dragonage/images/4/46/A_Noble_Expedition.jpg/revision/latest/scale-to-width-down/1000?cb=20121209182839. Additional indicators (pronouns, wiki entries) are present for many of them. 

I think "City Elf Child" is the child near Elva during the City Elf Origin (male character model). It's not clear who the 'Alienage Commoner' lines belong to - perhaps they're split up between the different city elves. I've coded neutral due to uncertainty but this could be revisited.)

Ser Landry's second appears to be a generic - he has three seconds (see https://dragonage.fandom.com/wiki/Honor_Bound). Whether the lines are divided between them or shared by them isn't obvious - I've coded it as singular to avoid unnecessary duplication.

"Knight (Ostagar)" is a generic - these lines can be spoken by various male NPCs around Ostagar (and likewise "Female Knight (Ostagar)" - in various places the game code specifies female characters and treats males as default - here it is "pre100_knight" and "pre100_knight_fem" respectively.) Some of the Ostagar soldiers are generics too (male human is the default, with female humans or elves specified.) I couldn't track down video showing the people listening to the Ostagar Priest (they speak a line each), so have coded as neutral for now, but this should be revisited upon replaying. There are a few other soldier NPCs that I've likewise coded as neutral because they aren't appearing in let's play videos (so it's not clear which the lines belong to). 

Rumours spoken by Bodahn Feddic, the Bartender at the Gnawed Noble Tavern and Danal from Lothering all appear in the game data as if spoken by the same person - "OWNER_main_rumour_man". The vast majority of lines belong to Bodahn, but I've tried to identify as many as possible that belong to the others and correctly attribute them. Note that all three characters are male, so it doesn't affect gender split. 
According to the wiki (https://dragonage.fandom.com/wiki/Bodahn_Feddic#Dragon_Age:_Origins): 
>Bodahn's voice actor is used for several bartenders in Origins, such as in Denerim and Lothering. Furthermore, the lines when asking Bodahn about rumors are exactly the same for these other characters.

There isn't exact duplication - some of Danal's lines are obviously his uniquely (such as when he introduces himself by name).

Refugees from the Desperate Haven quest are generics - there is a male, female and child line, but differing numbers of each may survive depending on how well you do in the quest (see https://dragonage.fandom.com/wiki/Desperate_Haven). The refugees from Lothering are likewise generics. The "Lothering Chantry Templar" might be too. 

"Gossip 1" and "Gossip 2" are two men in Lothering, but there are identical gossips in other places (such as the entrance to Orzammar in the Frostbacks) who use the same set of lines. 

The majority of guards in the game are male, but Lady Sophie's guard is an exception. 

Most Chantry 'priests' are female - only women can be accepted into the priesthood (known as sisters, mothers, grand clerics etc.), although there are 'lay brothers' of the Chantry, and in Haven they don't follow the standard customs. 

The "Companion" NPCs are sex workers at the Pearl. They are generics, in that there are sets of lines for each type of companion (e.g. female human) but often multiples of each type - you hear a small sample of the lines each time you select one. Note that there are multiple companions labelled 'female companion' and two labelled '"female" companion', who share the female character models but have deeper voices. The implication is that they are trans (although as has been noted, the inverted commas around "female" are a problematic way to signify this. See for instance this mod: https://www.nexusmods.com/dragonage/mods/4893). The alias for them in the game data includes "tran". I have coded them (i.e. the generic) as "trans female companion" (for visibility), and included them under both the trans and female gender categories. 

Sick Female Elf and Sick Male Elf are generics, as are the Elf Woman (Crowd)/Elf Man (Crowd) variants. The "Male Servant (Highever)" and "Female Servant (Highever)" are generics. As are the servants elsewhere (e.g. Redcliffe Castle). 

"OWNER_den300_elf_thugs" - it's not clear which of the three Elven Thugs speaks these lines, but it appears to be 2 here (https://lparchive.org/Dragon-Age-Origins/Update%20106/), so I've coded accordingly. They're all male and all have very limited dialogue. 

The eerie elf children are difficult because the clues are mostly voice acting. However, there is a female and a male voice actor credited with eerie elf child, and the first rhyme mentions being a maiden. Originally I had coded the first eerie elf as female and the second as male (and likewise for the wisps). However, upon replaying, eerie elf child 2 sounds quite close to eerie elf child 1 (and very distinct from the Ghostly boy and the second wisp, who have significantly deeper voices). I've thus recoded eerie elf child 2 as female; however other coders might feel there is insufficient evidence in this case. 

The Rage Demon in the Orphanage seems to be three forms of the same demon, rather than three different demons. I've coded accordingly. 

The cheering soldiers during the Battle of Denerim (as your party walks to the gate) all appear to be male, so I assume the "random" cheering soldier is also male. 

There are some NPCs who only appear after Nature of the Beast in the Brecilian Forest that don't appear in videos/the wiki - they are coded as neutral for insufficient evidence ('ntb' appears in their game code). This could be revisited upon replaying. Various of the Brecilian Forest ('ntb') elves are generics. 

"The Magnificent Gaider" and the various "Grobnard" characters are from the toolset - best I can tell they're easter eggs for folks poking around (https://sharehub.pro/forum/main/discussion/23889-cut_out_of_the_game_and_is_found_in_the_toolset_dragon_age_origins/). I've popped them under "cut" since they don't appear in the main game. 

"Gazarath" is a shade, and doesn't have an obvious gender - in the codex entry giving their background, neutral pronouns are used: https://dragonage.fandom.com/wiki/Codex_entry:_A_Pinch_of_Ashes. I've coded as neutral for lack of evidence. 

Arl of Denerim Estate - the On-Duty Guard characters are generics. Many of the others are unique. 

Spoiled Princess - Disgruntled Patron is a generic; there are at least two of them (both male). 

I think some of the Haven characters (aliases starting with urn100/urn200) are cut content, but it might be that some of their lines are uttered if you don't kill them all and then make a deal with Kolgrim. I've coded as neutral given the uncertainty (and because there's insufficient evidence for their gender - except for the Suspicious Mother, who is evidently female. She should be moved to "cut" if it's determined that she was indeed cut content). 

The Redcliffe castle guard, new guard, returning knight etc. are all generics (and all male). The Redcliffe Castle servant is also a generic (and all female). For some generics, it's difficult to determine how many NPCs share the same lines - they're spread out, the lines are selected randomly and there are enough of them to give the appearance of distinct people etc. (For instance, the Redcliffe Guards are all male, but there are a lot of them, spread out throughout the castle!) However, there are some cases where it's much clearer, e.g. where multiple identical NPCs stand in close proximity and utter the same lines. In these cases, I've indicated as much with aliases. For instance, the three Dwarven Soldiers at Redcliffe Castle all say the same things, often one after another. I've thus split them to reflect the amount of dialogue. Likewise, there are three "Crimon Oars Flunky" NPCs standing in the same room. If interested in using the data file for a different purpose, these 'split' aliases could be altered. 

"Eamon's Bodyguard" - there are three identical NPCs (there are actually four, but only three speak). The long conversation only occurs with one of them (the first you speak to, I think). After that, you receive on of the remaining lines from their line-set (and likewise when you speak with the other two). They are all standing in the main hall of Redcliffe Castle, so you can easily hear the lines said three times - I've added aliases accordingly. 

It is possible that the same line-set is used for Chanter Rosamund (in Denerim) and Chanter Farrah (in Redcliffe). They share a voice actress, which is further evidence (https://www.imdb.com/title/tt1541718/characters/nm1424599). Chanters quote parts of the chant of light when spoken to (ritual dialogue). However, I've only heard Chanter Farrah say one line (and heard it multiple times), so for now I've just attributed that line to her. 

In several of the random encounters, the number of NPCs that can survive varies, and thus the number of NPCs that are available to speak to varies. For instance, in "Desperate Haven" the player saves refugees from an attack. There is a line set for women, men, and young boys, but multiples of each can survive. Likewise, there is a variable number of "Dwarven Soldier (Winding Road)", but in this encounter they are all male. 

"City Gate Defender" is a generic. They're all male soldiers.
