# Final Fantasy IX

## Source

In the source, whispers are coded similarly to actions (both are enclosed by round brackets within dialogue). These were manually identified and dealt with appropriately in the postProcessing() function.

Some of the Chocobos have dialogue:

```json
{"Gold Choco": "Kweh, kwokkwehkweh, kweh. (The western side of the mountain on Seaways Canyon on the Forgotten Continent also has a crack in it.) Kwok, kwek, kweh. (But it's very hard to find)."}
```

We assume that the "kweh" sounds are the linguistic form, and the English is the meaning. So the English is kept in brackets and not counted by the main word counter.


## Gender coding
Bulletin Board - messages from two moles (Louie and Slaar). Their gender is unclear, so I've left the coding as 'neutral'. 

The moogles are difficult. The wiki notes that "A moogle's attire may indicate gender: males are bare but females wear small, purple coats" (https://finalfantasy.fandom.com/wiki/Moogle_(Final_Fantasy_IX)), but the "may" makes it difficult to be confident. Some moogles do have female gender signifiers (including the coats), and many are described using pronouns in the dialogue. Generally speaking I have coded as femael those with coats and male those without.  Some notes re particular cases follow:  
Kupo: some of the source 'action' descriptions use 'he', as does the wiki. Same goes for "Atla", "Kumool", and "Gumo" (latter is called 'Man' by another moogle). 
Kuppo: described as Kupo's big brother, so coded male. 
Moco: "him"
Grimo: "Grimo himself"
Mimoza: "Mimoza is scary when she gets mad"
Mogsam: insufficient info, left as neutral. Same for Moolan (top-down character model only in the latter, no pronouns). 
Chimomo, Momatose and Mocha are tricky - these are the moogles that help Eiko cook dinner. They have the typical male moogle character model, and Eiko refers to them collectively as 'guys', but there aren't any specific pronouns used. I've coded as male on the basis that the game has otherwise emphasised that that model goes with a male character (and thus may well have shaped player experience accordingly), but this could be revisited. 

Gilgamesh goes by various names in different towns, e.g. Alleyway Jack. Captured as aliases. 

The Black Mage characters are constructs made in three forms. Vivi - who is clearly identified as male in the script and by the characters - is one of them. Vivi calls another one (288) 'Mr. 288', and another refers to No. 44 as 'Mr 44' (and yet another 'Mr 36'). At the end of the game we see black mages identical to Vivi who the wiki report are "dubbed as Vivi's "sons"". Eiko refers to the black mages as Vivi's "brothers". I've coded the black mages as male accordingly, but this could be revisited (if one were interested solely in characters' self-identification, this might be decided differently - some of the black mages arguably haven't gained enough sentience yet to understand gender). Likewise, the Black Waltzes (a variation of the black mage) are described as 'him' in the script. 

The various cooks (-Meister) are collectively referred to as 'boys' by Quina, so have coded accordingly. 

The Fire Guardian ("Fire Guard") is referred to as 'her' in the wiki. The Earth Guardian reads as male. 

Ashley is male (character model/wiki - "Thug" sprite). 

All of Wei and Kal's children have identical character models, but their gender is unclear, so coded neutral. 

Meltigemini is the combined form of Thorn and Zorn. Since they are coded as male, I've coded their fusion as male too. 

Despite the name, "Fan Club Chairman" seems to be a female character model. As far as I can tell, the fan club members are all female too. 

Quan is a complicated case. The Qu are generally thought to be genderless, but Quan is referred to as 'he' throughout (rather than 's/he' like the other Qu) and as Vivi's adoptive grandfather. I've coded as male as a result (tracking conferred gender rather than sex). 

"Alexandrian Soldier" is a generic. They're indistinguishable females. The source doesn't distinguish between them. It may look as if there is a single Alexandrian soldier with a lot of lines; in fact these are distributed between multiple indistinguishable NPCs.  

Likewise, "Scholar" is a generic (in Alexandria at least) - there are multiples in the Alexandria library but I've left them grouped together. Brown-robed male character models with bald spots. "Elite Guard" is also a generic, as are "Soldier", "Attendant", 

"King Leo" is the role Baku plays in the play. 

"Guard (Dali Gate)" - you don't see their face/character model, so coded neutral. 

"Widget" is a tapir-type character. Same character model as the aviator at the Lindblum docks who seems to refer to himself as male, so have coded male, but this is open to be revisited (further evidence is that the engineers in the game tend to be male). The same goes for the South Gate Worker.  

Coded "Bidder" characters in accordance with this video: https://www.youtube.com/watch?v=g1vqDn-IJP0. It's from the PC version - the gil amounts don't match exactly, but screenshots from the original PS version suggest the arrangement of characters is the same. It's not clear who Bidder 1 is (is it just Bidder? Is it the other woman in the screen?), so coded as neutral. 

Vivi refers to "Forest Oracle Kildea" as "her", so I've coded as female. However, some of the other oracles are read by players as male, despite sharing the same character model (judging by commentary in our source file and in other fan scripts, e.g. http://www.ffwa.eu/ff9/script.php?page=d2-02). Additionally, many of their names are typically thought of as 'male' (e.g. Donnegan, Wylan). There are also more obviously female character models on these screens (the maidens). For lack of evidence, I've coded the other oracles as neutral. 

"Kelley Fingerwaver" appears to have a beard, so I have coded as male. 

You only see the lower half of the crew member in the engine room ("Crew Member (Engine)"), and all crewmembers have the same trousers, so I've coded as neutral (insufficient information). 

The genomes have gendered uniform. The adult males wear pink, the adult females orange. The children wear purple, with their chest bare (closer to the adult male outfit). Vivi refers to one of them as a boy. I've coded that one as male, but have left the rest as neutral as presumably there are some female children among them. I've split the genomes in Terra by location, but it's impossible to work out which they correspond to once they move to the Black Mage village (or how they might move around there between visits). Rather than double-count characters, I've just split by purple/pink/orange in the Black Mage village. This could be revisited. 

Scarlet Hair has a beard and is referred to as "he" in the wiki: https://www.youtube.com/watch?v=I1QDEFVcDVw