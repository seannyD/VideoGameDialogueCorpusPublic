# Example of how to load corpus data in R

# Load libraries
library(quanteda)
library(quanteda.textstats)
library(quanteda.textplots)
library(rjson)

# Set the working directory to the 'analysis' directory of the corpus on your computer
myAnalysisDirectory = "~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project_public/analysis/"
try(setwd(myAnalysisDirectory))

# Load a local script with some helper functions
source("HowToLoadCorpusData.R")

# Load the Final Fantasy script as a data frame
# Each row is a line of dialogue
ffvii = loadJSONScripts("../data/FinalFantasy/FFVII")
# Print the characters with the most lines
tail(sort(table(ffvii$character)))

# Load 3 games from the Persona series by specifying the series folder:
persona = loadJSONScripts("../data/Persona/")
# remove non-dialogue text
nonDialogueKeys = c("ACTION","STATUS","LOCATION","SYSTEM")
persona = persona[!persona$character %in% nonDialogueKeys,]

# Make a quanteda corpus object
corp = corpus(persona,text_field ="dialogue")
# Tokenize and remove punctuation
toks = tokens(corp, remove_punct = TRUE)
# Count words
totalNumberOfWords = sum(ntoken(toks))

# Keyness analysis: https://tutorials.quanteda.io/statistical-analysis/keyness/
dfmat <- dfm(toks)
tstat_key <- textstat_keyness(dfmat, target = dfmat@docvars$Group_female)
textplot_keyness(tstat_key)
