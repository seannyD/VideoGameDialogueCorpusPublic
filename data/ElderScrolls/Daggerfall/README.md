# The Elder Scrolls II: Daggerfall

## Source

The source contains all quest dialogue from the [recent re-implementation of Daggerfall](https://github.com/Interkarma/daggerfall-unity/). There is more dialogue in the game, including procedurally generated "general talk" that can happen with any NPC. For example, the player can ask about the location of various things or people, and the NPC will automatically generate a response fitted to it. The responses depend on the current location and the NPCs demeanour. Some appears to be procedurally generated. So there are a LOT of possible unique lines of dialogue (like millions). However, they aren't affected by the gender of the player or NPC, as far as I can tell. That is, none of this type of talk is written specifically for specific characters. In contrast, the quest dialogue is written directly.


## Notes on the procedural generation of characters

According to the [recent re-implementation of Daggerfall](https://github.com/Interkarma/daggerfall-unity/), procedural generation of NPCs is done via the algorithm below. First, the NPC is assigned to be a guard with 1/31 chance. If they are a guard, then they are male. Otherwise the gender is determined 50/50.

See [here](https://github.com/Interkarma/daggerfall-unity/blob/b5434559f8e24371f973c5bc00cd4a65bca4bbfc/Assets/Scripts/Game/MobilePersonNPC.cs#L129)

```
        public void RandomiseNPC(Races race)
        {
            // Randomly set guards
            if (Random.Range(0, 32) == 0)
            {
                gender = Genders.Male;
                personOutfitVariant = 0;
                IsGuard = true;
            }
            else
            {
                // Randomize gender
                gender = (Random.Range(0, 2) == 1) ? Genders.Female : Genders.Male;
                // Set outfit variant for npc
                personOutfitVariant = Random.Range(0, numPersonOutfitVariants);
                IsGuard = false;
            }
            // Set race (set current race before calling this function with property Race)
            SetRace(race);
            // Set remaining fields and update billboards
            SetPerson();
        }
```

This brings the theoretical proportion of NPC genders to 51.6% male, 48.4% female.

The random assignment of gender to 'foes' (monsters and antagonistic characters) has a bias for male characters:

See [here](https://github.com/Interkarma/daggerfall-unity/blob/b5434559f8e24371f973c5bc00cd4a65bca4bbfc/Assets/Scripts/Game/Questing/Foe.cs)
 
```
// Randomly assign a gender for humanoid foes
            humanoidGender = (UnityEngine.Random.Range(0.0f, 1.0f) < 0.55f) ? Genders.Male : Genders.Female;
```

This was actually changed from 0.5 - see [here](https://github.com/Interkarma/daggerfall-unity/commit/548f01e97b03bcef8fb6bd6c9f25fc195ffd3ba4) - but it's not clear why. One possibility is that an addition around this time was to include a possibility of meeting a pair of female foes. Perhaps the contributor felt like this would shift the gender distribution, so needed balancing. Still, a 10% difference seems like an over-adjustment.


Interesting note on the representation of gender in the original implementation - see [here](https://github.com/Interkarma/daggerfall-unity/blob/b5434559f8e24371f973c5bc00cd4a65bca4bbfc/Assets/Scripts/API/Save/CharacterRecord.cs):

```
        Genders ReadGender(BinaryReader reader)
        {
            byte value = reader.ReadByte();

            // Daggerfall uses a wide range of gender values
            // It is currently unknown what these values represent
            // However it seems that first bit always maps to
            // 0 for male and 1 for female
            if ((value & 1) == 1)
                return Genders.Female;
            else
                return Genders.Male;
        }
```