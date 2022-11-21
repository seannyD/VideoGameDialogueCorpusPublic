# Mass Effect 2

## Source

Some of the lines in the data file have been cut from the game (but only a small percentage). See for instance the extra lines of Preitor Gavorn: https://masseffect.fandom.com/wiki/Mass_Effect_2_Cut_Content#Captain_Gavorn_Dialogue. Not all are captured in the wiki. 

Conversely, some lines of dialogue from certain cut-scenes in-game are not present in the data file. E.g. Conversation between Samara and the Eclipse Lieutenant in Dossier: the Justicar is missing. Some of Wasea's lines are missing too (from her cutscene intro). 

## Gender Coding

Difficult to know whether to code the gender of the reapers. However they have distinctively male voices, and some characters in-game refer to them as 'him'. Only relevant to "Harbinger" in this game - I've coded as male.  

Some characters (but fewer than in other games) represent generics - i.e. a set of lines is recorded by a single voice actor and coded against a single character, but in the game the lines are distributed among mooks in a mission. The following are some instances: 

"owner_jnkkga_moremercs_a_dlg": "Blue Suns Mercs (Korlus)" Coded male as all male voices.

"owner_twrasa_carport_confusion_a_dlg": "Eclipe Trooper (Dantius Towers)" (M) (all male voices)

"jnkkga_radiomerc": "Merc on Radio" (M) Goes by different names ("Agitated Sergeant"; "Blue Suns Trooper" etc., but it's the same voice - essentially the blue suns mercs heard via the radio on Korlus)

Background Quarian chatter in Tali's Loyalty Mission:

"quatll_mutter_f": "Background Female Quarian Chatter" (F)

"quatll_mutter_m": "Background Male Quarian Chatter" (M)


"hench_garrus_romance": "Garrus" (M) - this is romance (and thus female specific) dialogue. 

Notes re specific cases: 

-  "global_collector_general": "Collector General" (M) - coding as male because although the collectors seem neutral, this one is possessed by Harbinger and thus speaks with a male vboice. 
-  "owner_twrmwa_redsand_tgen_dlg" - By process of elimination I think this is Jack. However, some of the dialogue seems to have been cut from the game. 
-  "n7gen_awayteam_vi": By process of elimination I think this is the Shuttle VI. 
-  "owner_endgm1_dogfight_c_dlg" - just repeats Joker's lines. May be cut dialogue (indeed, several of the bits of dialogue here don't seem to appear in game - unused contingencies); or the repetition could be a parsing error. Coding as Joker, but could be revised.
-  "owner_endgm2_boss_fight_a_dlg": "Harbinger"  - these are very Harbinger-like quotes, but I haven't heard them in-game. Possibly cut content. 
-  "owner_n7viq1_cargo_crew_dlg". Based on its code (n7viq1) seems like it should be from the "N7: Wrecked Merchant Freighter" mission. The 'Tiredly:' prefix suggests it's an elcor, and all elcors in ME2 are male. Given this, I've coded as male. However, I can't find mention of the line in the wiki or in playthroughs, so it might be cut content. 

-  "owner_nor_training_vid_a_dlg": "In-game combat training" (M). This is system narration from the in-game combat training videos (training for the player, but using Shepard). Open question whether this should be counted among the dialogue. 
