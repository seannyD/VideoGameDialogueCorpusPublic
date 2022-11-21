# Final Fantasy X

## Source

The source is very extensive, but inconsistently coded. There is a lot of scripting and coding to correctly split and unify the character names.

In the source, lines are attributed to "Yojimbo's Fayth", but actually spoken by Yojimbo: https://youtu.be/gm3jwVrVEmc?t=1583

## Gender coding

NB. Because of reused sprites (and the fact that NPCs do travel in the game), it's difficult to get an exact number of characters - for instance, how many crusaders are there with the same face? 

"Al Bhed Child" coded as male, as referred to by male pronouns by the woman accompanying him. "Child" is also an Al Bhed child (in a different room of the airship) - it's not clear what gender they are so I've coded as neutral. Likewise for "Child on right" - they mention a doll, but that's not sufficient for coding purposes. 
I couldn't track down which of two Al Bhed doing squats was referred to by that description, but both have male avatars so I'm coding male. 

Misattribution of lines in the data file (not the original script) for "Al Bhed in Command Center". I've added aliases to get around this. I've coded "Epitaphs" as neutral, as they aren't voiced and instead are system messages like when you read something, but one might argue they're Tidus's thoughts (however Tidus's thoughts are usually voiced, and we don't count read messages as his words). 

"All" refers to all of the Crusaders etc. Seymour is talking to. I've coded as "neutral".

The musician characters (frog drummer; mouse playing the horn; bird) are found in Luca (https://finalfantasy.fandom.com/wiki/Musician_(Final_Fantasy_X)) and in Macalania Temple. They're not voiced or named in this instalment (although some are voiced and named in FFX-2, and we find out they're spirits of Macalania Wood). It's not clear whether the musicians at Macalania Temple are supposed to be the same ones from Luca (and the other trio their cousins - Bayra, Pukutak and Donga, as we learn from FFX-2), or others with the same character models. I've left them separate and coded as neutral but this could be revisited. The exception is Borra, who is voiced in both instalments. 

"Critter" is the Chocobo Eater monster. Coded neutral. 

"Driver" is a hypello; all hypellos are voiced by the same (male) voice actor in FFX and FFX-2, except one called "Darling" who is voiced by a female actor. Thus I've coded "Driver" as male. 

The little Crusaders are best guesses based on their avatars. 

The Flaky Guado teen's hair looks like the male guado sprites' so I've coded accordingly. (Compare with "guado girl in purple").

I've added an alias for "NARRATION" as its Tidus narrating throughout. 

"Guard for dock 4" is male, but the only dialogue associated with him is in fact a system message that he seems to have been put to sleep. This is like "Epitaphs", so I've coded it as neutral. 

Of the three kids at the beginning (who want Tidus to teach them how to blitz), the one with the bandanna appears male, but the other two are really difficult to determine. There aren't any pronoun clues, and their sprites are ambiguous. I've left the other two as neutral. 

"Note": these are notes from the script writer, not from within the game, so I've left them uncoded. 
"Vision": these are descriptions of visions by the script writer. Thus left uncoded. 

It was difficult to track down which lines in the conversation between the woman and the girl in Luca belonged to which, but both are coded female, so hopefully it doesn't make too much of a difference. 

"Vendor in purple" - it's difficult from the avatar to determine likely gender. I've thus coded neutral. 

"Whichever Crusader you talk to first": coded male, as it's one of two male characters.  

Receptionist has female model: http://auronlu.istad.org/ffx-script/?attachment_id=473

Captain of the Liki: https://finalfantasy.fandom.com/wiki/S.S._Liki?file=SS_Liki_Control_Room.png
(The S.S. Winno seems to be a clone of the Liki). Coding "Ship captain" (one line, positioned on Dock 1) as male as other ship captains share the same (male) NPC. 

"Young woman in blue" seems to be a mistake in the source - from context it appears to be the guado youth in blue, who has a male character model. Likewise for 'flaky girl in green'. 

"Warrior monk (Highbridge)" - there are two of them, but only one seems to speak. 
