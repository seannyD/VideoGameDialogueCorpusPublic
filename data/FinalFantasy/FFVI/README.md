# Final Fantasy IV

## Source

The original script is explicit about various parts that are left out. This includes that 'random townsfolk talking will likely not be included'. Note that link suggests FFIII, but the script is really for the (Japanese number) FFVI.

The source does not include some alternative dialogue or dialogue that depends on player actions / status. See the parsing for FFVI_B for some of these.

## Gender coding

There seems to be a default 'male' and default 'female' body shape for sprites (respectively); some of the coding for generic NPCs are based on this (and where possible confirmed with pronouns, wiki entries etc.). As is common in other FF instalments, generic sprites are reused (so all "guard" characters have the same sprite). 

Chadarnook is a demon possessing a painting of a female. Although the painting's subject is female, it's not clear what the gender of the demon is, so I've coded as neutral. 

The NPC called "Fairy" in the data file appears as "Girl" here with a picture of her sprite: http://www.finalfantasyquotes.com/ff3/script/Part_63 (coded female accordingly). "Master" appears as "Man" on this site, and so do "Thief" and "Wolf". 

"Kid" - there are both male and female kid sprites in the area, and I'm not sure which says what line, so I'm coding as neutral. 

From the wiki: "The esper who guards the gate in the esper world in Terra's flashbacks to her birth and the Imperial invasion uses the same sprite as Yura. It is not known if it is intended for this esper to be Yura, or if he just uses the same sprite as him; in all versions of Final Fantasy VI, this esper is unnamed and referred to in dialogue as "Youth"." (https://finalfantasy.fandom.com/wiki/Yura_(Final_Fantasy_VI)) I've coded them as separate male characters accordingly. 
