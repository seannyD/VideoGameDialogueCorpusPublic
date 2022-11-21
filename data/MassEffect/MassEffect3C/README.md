# Mass Effect 3

## Source

The source of the data is the "talk" files from the game data, as extracted by a customised version of the ME3Tweaks Legendary Explorer: https://github.com/ME3Tweaks/LegendaryExplorer. Some dialogue from cutscenes are included in a different file type that are not included here. For example, the flashback scenes from the ME3 DLC 'From Ashes' featuring the protheans and their VI Victory. Another example occurs in the Grissom Academy quest where Jack (if she's alive) and Shepard have the following interactions:

```
[When the heavy mech appears]
Jack: Everyone, get down. This thing's outta your league. Shepard, keep it off us.

[When they're making their escape]
Jack: Where the hell's Rodriguez?
Shepard: She needs covering fire.
Jack: She needs more than that.
```

However, some cutscene dialogue is included in the "talk" files.

## Gender coding

I've coded Geth Prime and Legion as male, as they have distinctively male voices so I suspect read to the audience as male. They have no biological sex, but the gender conferred on you by the audience is arguably relevant for gender coding. This could reviewed. It's worth noting that Shepard sometimes refers to Legion as 'he', so seemingly he reads that way to her too. Joker also calls Legion 'him' when he Shep and EDI discuss Legion having become a person.

Some cinematics aren't included, as per the other ME games. E.g. 
Missing line from Jack: "Everyone, get down. This thing's outta your league. Shepard, keep it off us. 
The lines in the cinematic at the end are missing too: 'Where the hell's Rodriguez' (Jack). 'She needs covering fire' (Shepard). 'She needs more than that' (Jack). Cut-scene with Shep and Joker when starting the geth dreadnought mission is missing too. Several of the end cinematics are missing. 

Some of the conditionals ('STATUS') need correcting. This doesn't affect the dialogue or gender coding directly, but may affect the proportion of male/female dialogue you receive (depending on what triggers). This is particularly relevant for romance dialogue. 

"proear_random_guy" - Couldn't track down, but only has one line (which is conditionally triggered) and based on the description plumped for male. Most of the NPCs seen during the scene where the line would appear are male, so it makes contextual sense. Still, could be reviewed. 

"promar_alliance_scientist", - Can't find them, nor the 'owner' lines before them. 

"kro001_cerb_soldier1": "Cerberus Trooper 1 (SurKesh)" Male (sometimes appears as Assault Trooper, sometimes as Cerberus Soldier). These aren't individuals, but they have the same voice/coding. Sometimes 'Combat Engineer'. All the same male voice. 
Similarly, "kron7b_cerberus_soldier2" and "kron7b_cerberus_soldier1". Male (like with the SurKesh mission, there are multiple assault troopers here, but all are coded as one of these two entries. Sometimes they go by different names (e.g. 'Centurion')). They are the generic cerberus mooks. 
"promar_cerberus_main" and "promar_cerberus_second" are generics as well. 
            
"n7slum_fleeing8", Civilian 8 (Benning) - Neutral because I couldn't track them down. 
"n7slum_fleeing5": "Male Civilian 5 (Benning)" - least clear voice. I think male, but not with high credence. 

"store_vi", Store VI (Male). It's the Shepard VI body, but a sales voice until it's unlocked. 

According to the wiki: Hanar are biologically genderless, though others may assign arbitrary gender values to them for convenience. "Blasto" (the fictional spectre Hanar) is often referred to as male in game, so have coded accordingly. Zymandis is referred to as 'he' by other characters as well. Otherwise coding as 'genderless'. 

Lots of characters coded in accordance with voice (e.g. Door VI etc. )

"citprs_csecpilot" - I'm not sure this is in the current version of the game (seems to be commented out as belonging to an old version. Coded as neutral. )

Omega DLC dialogue is not included in the data dump we have. Will leave a save so can replay it if we get it at some point. Several of the main characters (Aria, the Turian companion etc. are female in this one. Still the lackeys tend to be male.) - save 367. 

"citprs_csec_guard02", "citprs_csec_guard03". Lines appear to be during the optional confrontation with Wrex on the citadel, but despite watching multiple playthroughs I can't hear them - they may have been cut from game. All visible C-Sec officers in these scenes are male, but I've coded as neutral as it's not at all obvious who says them (and the person originally meant to may be off-screen).

"global_info_drone", Glyph. Shaped like a sphere, male voiced virtual interface. Referred to as 'it' throughout the game, but is listed as 'masculine personality' on the wiki. I've coded as male in accordance with the wiki, but this could be revised. 

"gth002_reaper": "Reaper (Rannoch)" (M) - Traynor refers to the reaper as 'he'

"citprs_vid_reporter" - News you hear in the Spectre office on the citadel. It's very difficult to hear in-game. The bits I've heard are spoken with a female voice; I couldn't verify if this was true of every line, but it's enough of a pattern that I've coded as female. 

Couldn't find, so coded as neutral: 
    "end001_alliance_captain" (one word)
    "radio_end001_alliance_captain",
    "test_mac"
    "owner_promar_level04_b_dlg"
    "citprs_ak_doctor" (one word)

I have split "end001_radio_comm_officer02" as per https://www.youtube.com/watch?v=pCsgsIRrBLo. It's not clear if they're recorded and allocated randomly; sometimes it seems like a conversation but it's the same voice. 

I haven't tried to separate out Legion from Geth VI (https://masseffect.fandom.com/wiki/Geth_VI).

 "owner_adv_combat_tutorial_Xbox_dlg",
"owner_adv_combat_tutorial_pc_dlg",
"owner_adv_combat_tutorial_ps3_dlg",
I've coded these as 'SYSTEM', as they seem designed for the player rather than the character (i.e. it's combat training with button presses etc.). This could be revisited.

"owner_gth002_turret_bombard1_a_dlg" - I think this is Admiral Han'Gerrel and have coded accordingly, but it's a guess. (Only one line). 

"BioD_OmgJck_500Lobby_LOC_INT.pcc: omgjck_pullsave_i_dlg": I think this dialogue was cut from the game. From context, the missing owner here is "Brennen", and Jack uses male pronouns for them. 

proear_normandy_arrives_c_dlg: Best guess from context is David Anderson, but I can't find the dialogue in-game. 

