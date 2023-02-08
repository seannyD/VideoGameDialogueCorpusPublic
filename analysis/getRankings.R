try(setwd("~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project_public/analysis/"))

library(rjson)

stats = read.csv("../results/generalStats.csv",stringsAsFactors = F)
# Remove alternative measures
stats = stats[stats$alternativeMeasure!="True",]
stats = stats[!is.na(stats$words),]
d = NULL
folders = unique(stats$folder)
for(folder in folders){
  sxM = stats[stats$folder==folder & stats$group == "male",]
  sxF = stats[stats$folder==folder & stats$group == "female",]
  js = fromJSON(file = paste0(folder,"meta.json"))
  if(nrow(sxM)>0 & nrow(sxF)>0){
    d = rbind(d,
              data.frame(
                Game = sxF$game,
                PercentFemWords = 100* (sxF$words / (sxF$words + sxM$words))
              ))
  }
}

d = d[order(d$PercentFemWords,decreasing = T),]
d$Rank = 1:nrow(d)
d$PercentFemWords = paste(round(d$PercentFemWords,1),"%")
write.csv(d[,c("Rank","Game","PercentFemWords")],file="../results/GamesRankedByFemaleDialogueProp.csv",row.names = F)