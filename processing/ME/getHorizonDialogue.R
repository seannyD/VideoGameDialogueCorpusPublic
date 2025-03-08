try(setwd("~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project_public/processing/ME/"))
library(quanteda)
library(dplyr)
library(stringr)
source("../../analysis/_CorpusHelperFunctions.R")

d = loadJSONScripts("../../data/Horizon/",onlyLoadMainCorpusSources = F)
#d = d[!d$character %in% c("ACTION","GOTO","STATUS","LOCATION","CHOICE",'SYSTEM'),]

d$binaryGender = NA
d[!is.na(d$Group_male) & d$Group_male,]$binaryGender = "Male"
d[!is.na(d$Group_female) & d$Group_female,]$binaryGender = "Female"
d[!is.na(d$Group_neutral) & d$Group_neutral,]$binaryGender = "Neutral"
d$trans = "No"
d[!is.na(d$Group_trans) & d$Group_trans,]$trans = "Yes"

d2 = d[d$character == "Aloy",]

d2$Script12th = unlist(tapply(d2$game,d2$game,function(X){
  x = floor(seq(1,13,length.out=length(X)))
  x[x==13] = 12
  return(x)
}))

# Escape html?
d2 = d2 %>% mutate_at("dialogue",
                    stringr::str_replace_all, 
                    pattern = "<", replacement = "&lt;")
d2 = d2 %>% mutate_at("dialogue",
                    stringr::str_replace_all, 
                    pattern = ">", replacement = "&gt;")

d2$dialogue = gsub("\\.\\.\\.","…",d2$dialogue)
d2$dialogue = gsub("…"," … ",d2$dialogue)


write.csv(d2, "../../results/doNotShare/ME/Horizon_AloyDialogue.csv",row.names = F)

lines = paste(
  '<doc ',
  'game="',d2$game ,'" ',
  'gender="',d2$binaryGender ,'" ',
  'speaker="',d2$character ,'" ',
  'scriptTwelfth="',d2$Script12th,'"',
  ">\n",d2$dialogue,"</doc>", sep="")

out = paste(lines,collapse="\n")

writeLines(out,"../../results/doNotShare/ME/Horizon_AloyDialogue.xml")

