# Final Fantasy XIV

## Source

The source for this is [GamerEscape](https://ffxiv.gamerescape.com/), where all pages in the ["Main Quest Scenario"](https://ffxiv.gamerescape.com/wiki/Category:Main_Scenario_Quest) have been scraped and parsed. 

Another source is [Fandom.com](https://finalfantasy.fandom.com/wiki/Main_Scenario). The Fandom.com source seems to have more lines, suggesting that the coverage for GamerEscape is not complete. However, the GamerEscape source includes information on player options and choice structures. It also has links from character names to pages about that character, including info on e.g. gender. 

However, the auto-gender-coding has some problems:

-  There are errors in the site source (e.g. Venat, Laniaitte, Wineburg).
-  Site defaults to male in cases where we should go with neutral.
-  Site doesn't account for multiples/generics.
-  Aliases aren't tracked (so we get "Firstname" and "Firstname+Surname" as two different characters)

We want to be clear that looking at a still of a character won't necessarily tell you what the player's experience of a character's gender will be. They learn the gender signifiers of the game, get to witness movement, voice acting etc., and there are linguistic cues as well. So the gender coding for this game is done by hand.

## Gender Coding

The script for FFXIV - and the in-game journal - is full of gendered pronouns, which are very helpful. Along with appearance data available at https://ffxiv.gamerescape.com/wiki/ and the other final fantasy wikis, coding is often straightforward. Breasts are common to the female character models, though tertiary gender signifiers vary between races/species. 

Loupard is categorized as male (https://ffxiv.gamerescape.com/wiki/Loupard#Details and https://ffxiv.consolegameswiki.com/wiki/Loupard). Character model has some features that would signify femininity in other games; nonetheless have coded male in accordance with the aforementioned sources. (The elezen character models in general have features that elsewhere would be weakly indicative of a female character.)

There are also patterns of gender signifiers that differ from what a player might usually expect in a game amongst the other races. E.g. Hythlodaeus wears a long plait on one side of his face. Pronouns, titles and other clues are more reliable indicators of gender in FFXIV. 

Giott is miscategorised as male in the gamerescape wiki despite showing the right (female) character model; here https://finalfantasy.fandom.com/wiki/Giott_(Final_Fantasy_XIV) she is marked as female. Coded accordingly. 

Dwarves appear to have beards, but these are elaborate scarves. Without seeing them removed (or without accompanying pronouns), it's difficult to determine their gender. So, for instance, "Gogg Dwarf" is listed without a gender on the ffxiv.consolegameswiki. The gamerescape lists the gender as male, but I see insufficient evidence for that classification. As a result, coding as neutral. "Dwarf Observer" is coded as male on both wikis, but again I see insufficient evidence (no textual evidence, stills show the character wearing the elaborate scarves, and walkthroughs tend to talk about this character without using gendered pronouns). Coding as neutral; could be revisited. 

There is disagreement among the wikis re the gender of Koko, but I defer to his self-ascription: 
>"My name is Koko. Welcome to Dotharl Khaa. Hm? Koko sounds to your ear the name of a woman? Well, of course. That would be because it is. I died a woman and was reborn a man."

According to the ffxiv.consolegameswiki, 
>"Amaurotines all traditionally wore identical robes and half-masks, as expressions of personal identity were considered rude and unseemly." 
As a result, the gender of NPCs who do not take off their masks is impossible to determine visually. Where there are also a lack of pronouns, I've coded as neutral. E.g. "Secretariat Clerk" (note this is at odds with the gamerescape categorisation, that seems to default to male). "Diplomatic Ancient One" is listed as male in the gamerescape and consolegame wikis, but I don't see any visual or textual clues that would lead the player to that conclusion. The character is voiced here: https://www.youtube.com/watch?v=_DMwj8sytl4, but note the ancient ones voices are distorted, and even Venat - who is canonically female - has a deep, potentially masculine-sounding voice here. As a result, I've coded neutral for lack of evidence. This could be revisited. 

The sylphs are another interesting case. From https://finalfantasy.fandom.com/wiki/Sylph#Final_Fantasy_XIV: 
> "They speak an idiosyncratic form of the common language most notable for its lack of traditional pronouns. Sylphs replace first and third person pronouns with constructions such as "this one" (I/me) or "those ones" (they/them). Second, and sometimes third, person pronouns, as well as names in most contexts, are replaced with similar constructions using adjectives, such as "walking one" for any individual of the player-character races, or "trusted one," "cheerful one," or "nasty ones" for individuals of those descriptions" and "Although all feminine in appearance, sylphs are a dual-gendered species whose names reflect their gender. Neither gender falls into what the other races would would label as "male" or "female". Sylphs grow from seeds known as "podlings" formed from the flowers that grow on the heads of adult sylphs. Sylphs whose flowers bloom at specific times during the pollinating seasons produce podlings and their forenames end in -xio. Sylphs whose flowers bloom at irregular times throughout the seasonal cycle cannot produce podlings and have forenames ending in -xia." 

Given that the characters are feminine in appearance, it might well be that players read them as female gendered, however this wiki treats them as neither. The consolegames wiki (https://ffxiv.consolegameswiki.com/wiki/Sylphs) has a slightly different account: 
>"Sylphic gender, or lack thereof, can also be confusing for outsiders to comprehend. Those sylphs who possess both stamen and pistil are capable of producing bulbs, and are classified as everblooms. Generally considered "male" by other races, their names are characterized by the "xio" suffix. Sylphs whose names end in "xia" are known as lateblooms, a classification which stems from the trait of flowering at irregular times during the pollinating season. The "females" of the race, the lateblooms' inability to produce podlings is balanced by an innate talent for the arcane arts, their undiluted reserves of aether giving them the potential to become powerful spellcasters." 

There is some in-game verification of this (that other races in games treat them as female and male respectively), e.g. Noraxia is referred to as 'she' by Minfilia, Maxio as 'he' by Yda, and Frixio as 'he' by Papalymo, Yda and Buscarron. Another instance is the quest called "Brotherly Love" which focuses on two sylphs, Komuxio and Claxio. The in-game journal refers to these sylphs with male pronouns. Given that players will be exposed to this evidence and their expectations shaped accordingly, I've coded -xio sylphs as male and -xia as female unless otherwise noted. The "Sylph Emissary" has insufficient info so I've coded neutral (same for "Sylphic Servant"). 

The Ananta are an all female race (https://ffxiv.consolegameswiki.com/wiki/Ananta).

In the plot there's some body-switching (as characters possess bodies). Where possible I've identified these instances and used aliases to account for them. There may well be missed instances.

There are three Arrivals Attendants, with some duplication of lines. 

It's not clear who "Ephemeral Voice" is at the end of the Death Unto Dawn quest. It looks a bit like Minfilia Warde. I've coded as female based on visual appearance and voice acting, but it may need an alias once identified. 

"Administrative Node" is an object, and appears to be unvoiced, so coded as neutral. 

"Adorable Voice", "Playful Voice" etc are unvoiced pixies hiding in bushes. I've coded as neutral for lack of available evidence that might inform player experience. "Altima" is an unvoiced Ascian wearing the generic outfit (insufficient evidence - neutral. Wiki uses neutral pronouns). "Boisterous Pixie" is androgynous in appearance and unvoiced - I've coded as genderless rather than neutral in keeping with the treatment of the fae in this game, but this could be revisited (NB. they are magical creatures born of the aether, rather than the results of biological reproduction - https://ffxiv.consolegameswiki.com/wiki/Pixies). 

For characters like the Sahagin Priest, Ixali Chieftain etc, I've used the voice acting, physical appearance and textual clues to make a best guess at the gender likely to be conferred by players. Where there is insufficient evidence (E.g. Bhun Bun), I've coded as neutral. The Vath characters seem to all share a character model (in the Gnathic Deity questline at least - the Nonmind). Multiple are described with male pronouns (e.g. Voracious Vath, Vath Storyteller); I expect that given their indistinguishability, the rest will tend to be read as male as well. I've coded accordingly, but this could be revisited.  

The characters starting "Amaro" are mounts (coded neutral for lack of evidence). "Balloon" is a bomb monster, with no obvious gender signifiers, however it gets used as an alias in the source for a variety of enemies. Some of these I've been able to identify, but in almost all cases its difficult to determine gender, so I've coded as neutral. "Eo An" is an amaro - I'm unsure of gender so coded neutral. "Nimbus" is an amaro, but is described by other characters with male pronouns and is the 'his' in the quests 'In his mistress's name' and 'in his mistress's memory'. 

"Ascian Prime" is a fusion of a male and female character. The wiki uses male pronouns to discuss the fusion (https://finalfantasy.fandom.com/wiki/The_Aetherochemical_Research_Facility#Neurolink_Nacelle); I've coded male but this could be revisited. 

"Beq Lugg" is a nu mou. In FFXIV (unlike FFXII), the nu mou are referred to as 'they/them' consistently throughout the game. I'm coding Beq Lugg as genderless as they are a fae race, but it may be that a different term is more accurate (e.g. non-binary) - there wasn't anything specific on the wikis. This could be revisited. "Marn Ose" is likewise a nu mou. 

Similarly, "Feo Ul" (who becomes "Titania") is a fae, with feminine appearance, but who becomes "King of the Fae". Neutral pronouns in-game and in the wiki suggest that, like, the nu mou, Feo Ul is genderless (or similar). 

Re the Vanu Vanu (from https://ffxiv.consolegameswiki.com/wiki/Vanu_Vanu): 
>"Vanu Vanu names have gender specific suffixes: the masculine "Vanu" and the feminine "Vali". These words translate from the beastmen's tongue to mean "male tribe member" and "female tribe member", and are never used with animals or other species. Encounters between tribes might also occasion the mention of one's bloodline, e.g. "Honu Vanu, chief of Mighty Vundu!""

Pronouns used by other characters at first seem to correlate with this naming system (e.g. Alphinaud refers to Lonu Vanu with male pronouns). However, "Kunu Vali" describes himself as 'he' on several occasions, and the in-game journal likewise records him with male pronouns. By contrast "Sanu Vali" and "Linu Vali" (who are mentioned in the wikis but don't appear in our source as they don't feature in the main quest), are described with female pronouns. 

The two "Hiding Child" characters (who share the same character model) have conflicting gender records on the various wikis. To me though, she appears female, so I've coded accordingly. Could be revisited. 

"Chocobokeep": characters by this name appear throughout the game, and can be of various races/species. The one coded here is from the "Over the Wall quest" (https://ffxiv.gamerescape.com/wiki/Chocobokeep_(Foundation)). 

According to https://finalfantasy.fandom.com/wiki/Convocation_of_Fourteen, Lahabrea serves as the speaker of the convocation so I have added an alias for "Convocation Speaker". The "Convocation Member" with him has a feminine voice, and could be Igeyorhm, but I'm not sure. I've thus not added an alias for the latter, but have coded "Convocation Member" as female. 

"Echoing Voice" is an unvoiced lift. Coded neutral. 

"Fuath Prankster" is a frog-shaped fae. Coded neutral as the fae are tricky, although worth noting that the outfit (waistcoat and cane) would often be read as masculine. 

"Flustered Temple Knight" is seen here: https://youtu.be/YxjtoQKfelA?t=486

"Gyodo" is repeatedly referred to with male pronouns in-game. "Gyoku" and "Gyosan" use the same character model. As a result, I've coded all three as male. 

"Heretic" is a generic, so I've split it up. "Amphitheatre Heretic" is what I'm calling the "Heretic" that speaks in "Sounding out the Amphitheatre". However, there are four heretic NPCs on screen at the time and it's not clear which is speaking. However, all four have male character models; accordingly I've coded "Amphitheatre Heretic" as male. 

"Venat" is reborn as "Hydaelyn". For our purposes (and following what I've done with other characters who take multiple forms, where they keep a continuous gender), I've added Hydaelyn as an alias for Venat (so their dialogue will be counted as belonging to a single character). If one had different purposes, one might remove such aliases and count them as separate. 

Moogle characters are often described using male pronouns in the in-game journal (see for instance "Yearn for the Urn" quest); others are described with female pronouns (e.g. Pukwa Pika, although she is not in the current version of source). This is in keeping with the following from the consolewiki (https://ffxiv.consolegameswiki.com/wiki/Moogle): 
>"Amongst the Black Shroud moogles, male names generally begin with a "K", and female names begin with a "P". It is theorized that these letters serve to echo the consonants in the word "Kupo Nut"-a precious treasure their ancestors are said to have carried with them when they descended from the heavens."

I've coded the K- moogles accordingly. 

On the contrary, the names of the Churning Mist moogles make no obvious distinction between male and female. The names of both genders feature the "Mog" prefix, a tradition purported to have begun long ago with their first ruler, Chieftain Moggle. Often the in-game journal entries for quests use gendered pronouns (e.g. Moghan is described as he/him), and other characters use them too (e.g. "Moglin has finally come to a decision, has he?"). There is insufficient evidence for "Mogtoe", who I have coded as neutral. 

"Loudspeaker" can be heard here: https://youtu.be/_u1xlUUmb5M?t=880. 

Ifrit tends to be treated as male in the FF series (recurring summon). The wiki (e.g. https://finalfantasy.fandom.com/wiki/Ifrit_(Final_Fantasy_XIV)) uses male pronouns throughout. I've thus coded "Lunar Ifrit" as male, but this could be revisited. 

"Masatsuchi" is one of the Lupin (wolf/humanoids). There aren't sufficient indicators for Masatsuchi's gender so I'm coding as neutral. 

Y'shtola's mentor is called Matoya, but Y'shtola also uses the alias 'Matoya' in some parts of the game. As best I can tell, the instances we have captured here are all Matoya proper. 

Some of the imperials seem to be generics (e.g. there are lots of Imperial Centurion NPCs, but they seem to all be one of three very similar male varieties according to the gamerescape wiki). "Resistance Fighter" is also a generic (male Hyur). 

"Fool Me Twice" (quest) has a series of imperial NPCs speak - npca, npcb etc. Although videos show their in-game names (e.g. amiable imperial), folks tend not to speak to them, which makes matching the aliases difficult. I'm confident re "Imperial Centurion" and "Beguiled Imperial" (the latter is the only female character model with them, and you can see her line here: https://talking-time.net/index.php?threads/may-you-ever-walk-in-the-light-of-the-crystal-lets-play-final-fantasy-xiv-a-realm-reborn.14/page-2) The other coded aliases are a best guess, but even if there are errors it shouldn't have an impact on the gender count (they are all male character models and this is the only time they appear). 

"Puro Roggo the Unwashed" is referred to with male pronouns by Matoya. 

"Straggler" dialogue seen here: https://youtu.be/ZEwXv4qE_9Q?t=556. Unvoiced and not clear which NPC is speaking, so coded neutral. 

I've used the gamerescape wiki to identify the Storm Officer, Flame Officer and Serpent Officer NPCs (their aliases are searchable on that wiki) and other similar characters. 

"Villager of the everlasting dark" dialogue seen here: https://youtu.be/uQGJs5QeQdk?t=223. It's unvoiced, and the characters aren't seen. Coded as neutral. 

"Watery Voice" belongs to some combination of Fuath - it's unvoiced and they're submerged (so not visible) - I've coded neutral. 

I think "yellowjacketa" and "yellowjacketb" are the two yellowjacket NPCs standing off to the side of Ryssfloh (during the "Feint and Strike" quest), but I can't find footage of who says which line. I've coded neutral but upon playing this could be revisited. 

Sons of Saint Conach is a group, but the lines we have (Syrcus Trench quest) seem to be spoken by a male character. 

I think "Zenos" in the source is actually "Elidibus" (as opposed to "Zenos Galvus"), but this could be revisited. 

"Beggarly Fellow" and "Beggardly Fellow" look the same ("Beggar*d*ly Fellow" is a typo). Voice acting and model suggest male.
https://youtu.be/qZ9bYWbUK_Y?t=196
https://youtu.be/o6ikcYn26cA?t=30

Drunken Duskwright is male: https://youtu.be/VHua_bReqDA?t=164
https://ffxiv.gamerescape.com/wiki/Drunken_Duskwight

"Amphitheatre Heretic": it's not clear who is speaking, but one is called "swordsman", one calls the others "Brothers", and the character models seem to be male.
https://youtu.be/q6xBPonyj5g?t=271