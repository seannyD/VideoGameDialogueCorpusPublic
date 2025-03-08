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


############
library(openxlsx)
dmi = loadJSONScripts("../../data/MonkeyIsland/",onlyLoadMainCorpusSources = F)
dmi = dmi[dmi$game=="Return to Monkey Island",]

dmi$dialogue = gsub("\\)([^ ])",") \1",dmi$dialogue)
dmi$k_ES = gsub("\\)([^ ])",") \1",dmi$k_ES)
dmi$k_FR = gsub("\\)([^ ])",") \1",dmi$k_FR)

dmi$dialogue = gsub('"',"'",dmi$dialogue)
dmi$k_ES = gsub('"',"'",dmi$k_ES)
dmi$k_FR = gsub('"',"'",dmi$k_FR)

dmi = dmi[!grepl("internal",dmi$character),]
dmi = dmi[dmi$character!="LOCATION",]
dmi = dmi[!duplicated(dmi$dialogue),]

dmi$dialogue = gsub("\\[.+?\\]","",dmi$dialogue)

dmi = dmi[1:(nrow(dmi)/2),]

dmi$binaryGender = NA
dmi[!is.na(dmi$Group_male) & dmi$Group_male,]$binaryGender = "Male"
dmi[!is.na(dmi$Group_female) & dmi$Group_female,]$binaryGender = "Female"

dmi = dmi[1:2000,]

lines = paste(
  '<seg ',
  'game="',dmi$game ,'" ',
  'gender="',dmi$binaryGender ,'" ',
  'speaker="',dmi$character ,'"',
  ">",dmi$dialogue,"</seg>", sep="")

linesSP = paste(
  '<seg ',
  'game="',dmi$game ,'" ',
  'gender="',dmi$binaryGender ,'" ',
  'speaker="',dmi$character ,'"',
  ">",dmi$k_ES,"</seg>", sep="")

linesFR = paste(
  '<seg ',
  'game="',dmi$game ,'" ',
  'gender="',dmi$binaryGender ,'" ',
  'speaker="',dmi$character ,'"',
  ">",dmi$k_FR,"</seg>", sep="")

#lines = unlist(strsplit(paste(lines,collapse=""),"\n"))
#linesSP = unlist(strsplit(paste(linesSP,collapse=""),"\n"))
#linesFR = unlist(strsplit(paste(linesFR,collapse=""),"\n"))

mix = data.frame(
  English = lines,
  Spanish = linesSP,
  French = linesFR)

write.xlsx(mix,"../../../offline/MonkeyIslandParallel.xlsx")

write.csv(mix,"../../../offline/MonkeyIslandParallel.csv",row.names = F)

#lines = c("English",lines)
#linesSP = c("Spanish",linesSP)
#linesFR = c("French",linesFR)


#out = paste(lines,linesSP,linesFR,sep="\t")
#cat(out,file="../../../offline/MonkeyIslandParallel.tab",sep = "\n")


