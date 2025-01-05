try(setwd("~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project_public/analysis/violence/"))
library(quanteda)
library(dplyr)
library(stringr)
source("../_CorpusHelperFunctions.R")

d = loadJSONScripts("../../data/")
d = d[!d$character %in% c("ACTION","GOTO","STATUS","LOCATION","CHOICE",'SYSTEM'),]
d = d[!duplicated(d[,c("character","dialogue")]),]
#d = d[is.na(d$Group_cut) | !d$Group_cut,]

d$binaryGender = NA
d[!is.na(d$Group_playerChoice) & d$Group_playerChoice,]$binaryGender = "PlayerChoice"
d[!is.na(d$Group_male) & d$Group_male,]$binaryGender = "Male"
d[!is.na(d$Group_female) & d$Group_female,]$binaryGender = "Female"
d = d[!is.na(d$binaryGender),]

freqCharsBySeries = tapply(d$character,d$folder, table)

bigChars = sapply(freqCharsBySeries, function(X){
  minFreq = quantile(X,0.75)
  return(names(X[X>minFreq]))
})

d2 = d[d$character %in% unlist(bigChars),]
set.seed(451)
d2 = d2[sample(1:nrow(d2),130000),]

corp = corpus(d2, text_field = "dialogue")
toks = tokens(corp, remove_punct = FALSE)
sum(sapply(toks,length))

# 9.5 total, 7.8 dialogue, 

#tx = table(grepl("\\?",d$dialogue),d$binaryGender)
#prop.table(tx,2)

# Escape html?
d2 = d2 %>% mutate_at("dialogue",
                    stringr::str_replace_all, 
                    pattern = "<", replacement = "&lt;")
d2 = d2 %>% mutate_at("dialogue",
                    stringr::str_replace_all, 
                    pattern = ">", replacement = "&gt;")

lines = paste(
  '<doc ',
  'game="',d2$game ,'" ',
  'gender="',d2$binaryGender ,'" ',
  'year="',d2$year ,'" ',
  'speaker="',d2$character ,'"',
  ">\n",d2$dialogue,"</doc>", sep="")

out = paste(lines,collapse="\n")

writeLines(out,"../../../violence/VGDC_mainChar.xml")
