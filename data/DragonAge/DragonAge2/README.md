## Dragon Age 2

### Source

The data comes from game files. Extract the '.cnv' files from the game and copy them to to the 'raw' folder.

### Gender Coding
Some of the lines in the data file may have been cut from the final game, and thus will only appear with modding. E.g. Connor's appearance (https://dragonage.fandom.com/wiki/Connor_Guerrin). Where this is the case for entire characters and it's possible to identify as much, I've added them to the category "cut". I have not attempted to split out cut dialogue for characters that do persist in the game except in straightforward/obvious cases (e.g. where the cut dialogue is bundled under a different character name, e.g. Teagan v Arl Bann Teagan). Some useful information can be found here: https://dragonage.fandom.com/wiki/Cut_content?so=search#Dragon_Age_II - I have used the cut audio to identify some cut lines of dialogue (marked with aliases, e.g. "Aveline (Removed Line)"). 

As with DAO, I've coded the demons in accordance with their voice acting, pronouns and appearance. Desire demons have secondary sex characteristics associated with females and are voice acted accordingly. Other types of demon, by contrast, tend to have male indicators. The "Rock Demon" is a Hunger Demon possessing a Rock Wraith (an abomination). The wiki refers to it with male pronouns, and it has distintly masculine voice acting. I've coded it as male; this could be revisited. "Audacity" is a Pride Demon, and although it possesses Marethari (a female character), in its true form it has male voice acting and is referred to by Merrill with male pronouns. "Torpor" is a sloth demon with male voice acting and is referred to as 'him'. 

There are various city guards around Kirkwall that will speak to the party as they pass. Some in the data file might be generics, e.g. "Cityguard M1" for the male guards and "Cityguard F1" for the female guards. Likewise, there are various commoners, represented by generics in the data file. There are also various NPCs around the town who share line-sets - for instance, there are a number of sets of lines for nobles, for commoners, for refugees, and so forth, and multiple NPCs might speak lines from a single set. 

The Kirkwall City Guard can all be referred to as "Guardsman" (e.g. Guardsman Eustace, over the head of a female noble character model), regardless of their gender (with two exceptions - Aveline is twice referred to as "Guardswoman" by Bran (once) and Jeven (once)). The title alone is thus insufficient evidence of gender (gender has been confirmed through let's play videos and the wiki). The prevalence of female guards is particularly noticeable (and trope-subverting) in this game. "Ser" is also a gender neutral term (e.g. the templars are often called Ser).

Dog is referred to throughout with male pronouns. This trumps the lack of visible genitalia. 

Serendipity is a difficult case - intended as a drag queen by the game's creators (as confirmed by David Gaider) but read by much of the fan-base as a transwoman. Serendipity has a female character model and male voice acting. I've coded Serendipity under both the "female" and "trans" categories; this could be revisited. 

The nexus golem has a deep, masculine-sounding voice (heard here: https://youtu.be/O2XGKjdUDyI?t=504) - much deeper than Shale's from DAO. The party members use "it". It shares the character model for Thaddeus. In the aforementioned youtube video the player calls the golem "this guy". I've coded as male, but this could be revisited. 

Some of the "Fake" characters are visions that appear to Merrill during a battle with a demon (e.g. Fake Chandan, Fake Harshal). In keeping with how I coded the apparitions in the Gauntlet of DAO, I've counted these as the actual people (e.g. Fake Chandan = Chandan), as they appear and sound the same (so in terms of player experience, they hear additional lines from Chandan etc.) For other purposes this may be handled differently. 

"Gen Turn In" 1-5 are responses upon returning items found during the player's travels to their rightful owners. There are more than twenty such NPCs, but they seem to fall into five categories (female human, male mage, male elf, male dwarf, male human - corresponding to each of 1-5), and lines are drawn from the right category when the item is returned. Each of the NPCs is individually named, but because of the apparently random assignment of lines in a given category to a given NPC, I have left them as generics (1-5). 

Justice is a spirit that has merged with Anders. Usually the game indicates which is speaking with visual cues: when Justice takes over, Anders' eyes glow blue. They are, in a sense, a single entity, but the characters in the game treat them as distinct on occasion. The game code seems to treat certain lines as belonging specifically to Justice - I have left those as separate (and coded them as male, based on Justice's features when we do see him, plus his previous appearance in Awakening.)

Insufficient evidence for Melson's Guards (couldn't find a video; wiki is non-specific). Could be revisited upon replaying. 

According to the wiki (https://dragonage.fandom.com/wiki/Imported_saves_and_pre-built_histories#Results_and_pre-built_histories), an imported save from Origins with Harrowmont as king has no quest ramifications. This suggests that the Orz Bln dialogue - in which King Harrowmont is mentioned - was cut. 

All the Qunari in DA2 are male (female Qunari are introduced in the sequel, Dragon Age: Inquisition).

"Abomination" is Olivia transformed - we watch the transformation. Given this, although the voice deepens with the transformation, I've coded the abomination as Olivia: to the player, I think they are likely to read as the same entity. This could be revisited. 

"Chase Guard" and "Chase Thief" might be cut - I can't track them down. Coded as neutral for now. Similarly, the conversations between the Circle Highmage Guard, Templar Commander Guard, Confused Guard Ldr and Aveline seem to have been cut - there is no mention of these interactions on the relevant wiki pages (e.g. https://dragonage.fandom.com/wiki/The_Last_Straw?so=search), or by googling the lines, and I can't find it in let's play videos or in several playthroughs. I've coded them as "cut" (including Aveline's lines), but this could be revisited. "Pickpocket" and "Pickpocket Victim" aren't familiar either, and don't appear in the wiki - coded as 'cut', but again could be revisited. The "Pickpocket" seems to be female based on the victim's slurs. 

The weapons merchant lines are shared or divided between different weaponsmiths - e.g. the Lowtown Weaponsmithy and Korval's Blades. The same is true for the armor merchant lines. 

From context it looks as if the slave characters and slaverguards are from the Birthright Quest; however only the Slavermaster speaks in this quest in let's play videos. It appears the others have been cut. 

For now, coding characters that start with "Hate" as neutral - this can be revisited upon replaying (these seem to be battle lines, but I'm not able to track them down in let's play videos.). I'm not sure if the "Templar Recruit" has been cut; coded as neutral for now. 
