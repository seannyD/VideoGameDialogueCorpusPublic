# Mass Effect

## Source

The source is a dump from custom branch of Legendary Explorer: https://github.com/ME3Tweaks/LegendaryExplorer

Note that "ANCHOR" refers to anchor points in the script that "GOTO" commands point back to.


## Gender Coding

Hanar are canonically genderless, so I've coded the preaching hanar accordingly. However the wiki notes that others will ascribe gender to a hanar for ease, and in-game characters refer to Opold as 'him', so I've coded as male. 

NB The data dump includes "Bring Down the Sky" and "Pinnacle Station" DLC. 

"owner_prc1_trig_batarians_dlg": "Batarians" (M) - this is a generic for the batarian mooks that fight in Bring Down the Sky. 

The presrop biotic dialogue are generics - there are four patterns but distributed among different NPCs. 
The same is true for "owner_sp125_amb_crazy_dlg": "Insane Male Scientist" (M)
"owner_sp125_amb_crazyfemale_dlg": "Insane Female Scientist" (F)

"PLAC_Invis_Rp109_RogueAI": "Rogue AI" (M) - male voice. In keeping with other AIs, I've coded with the voice. 

"SYSTEM" are pop-up in-game messages (text, not voiced). They seem to be designed to give the player information (rather than the PC). 

Some cinematics missing, as per the other games. E.g. the approach on Noveria. 

"owner_sta30_officer_01_dlg" - I've coded as the same as the other sta30_officer instances, but this is a best guess (I haven't been able to track it down in game). It's 4 lines. 
Likewise, my best guess from context for "owner_pro10_trig_jenkins_dlg" is Kaidan. It's just one line, but could be revisited. 
