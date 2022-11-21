# Load the rjson library
library("rjson")

try(setwd("~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project/analysis/"))

########################
# Load data            #
########################

# Load data and select only lines of dialogue
d = fromJSON(file="../data/StardewValley/StardewValley/data.json")
lines = unlist(d,recursive = T)
lines = lines[!grepl("\\._",names(lines))]
lines = lines[!grepl("ACTION",names(lines))]
names(lines) = sub("^text\\.","",names(lines))
names(lines) = sub("^CHOICE\\.","",names(lines))

# Load metadata
m = fromJSON(file="../data/StardewValley/StardewValley/meta.json")
maleCharacters = m$characterGroups$male
femaleCharacters = m$characterGroups$female

# Identify lines with gender differences
linesWithGenderDifferences = lines[grepl("\\^",lines)]
# Split text into lines for different gender PCs
linesWithGenderDifferences = strsplit(linesWithGenderDifferences,"\\^")

genderDiff = data.frame(
  "speaker" = names(linesWithGenderDifferences),
  "speakerGender" = sapply(names(linesWithGenderDifferences),function(X){
    c("Female","Male")[1+(X %in% maleCharacters)]}),
  "dialogueToMalePC" = sapply(linesWithGenderDifferences,head,n=1),
  "dialogueToFemalePC" = sapply(linesWithGenderDifferences,tail,n=1),
  stringsAsFactors = F
)

# remove trailing whitespace:
genderDiff$dialogueToFemalePC = trimws(genderDiff$dialogueToFemalePC)
genderDiff$dialogueToMalePC = trimws(genderDiff$dialogueToMalePC)

# Work out length of messages in number of characters
genderDiff$dialogueToMalePC.length = nchar(genderDiff$dialogueToMalePC)
genderDiff$dialogueToFemalePC.length = nchar(genderDiff$dialogueToFemalePC)

# Some lines are identical, so remove those
genderDiff = genderDiff[genderDiff$dialogueToMalePC!=genderDiff$dialogueToFemalePC,]

# Work out difference in dialogue between dialogue to male PC and female PC
# in terms of edit distance (in numbers of characters)
genderDiff$charDifference = diag(adist(genderDiff$dialogueToMalePC,genderDiff$dialogueToFemalePC))

# Optionally: Sort by edit difference (first= smallest difference)
#genderDiff = genderDiff[order(genderDiff$charDifference),]
write.csv(genderDiff,"../results/doNotShare/StardewValleyGenderDiff.csv",row.names = F)

########################
# Analysis             #
########################

# Plot length of message (in number of characters) to men/women
boxplot(genderDiff$dialogueToMalePC.length,
        genderDiff$dialogueToFemalePC.length,
        names = c("To Men","To Women"))

# Simple stats: test difference in mean length
t.test(genderDiff$dialogueToMalePC.length,
       genderDiff$dialogueToFemalePC.length,paired = T)

# Histogram of difference in length
hist(genderDiff$dialogueToMalePC.length -
     genderDiff$dialogueToFemalePC.length,
    main="Male advantage in dialogue length",
    xlab="Number of characters")

