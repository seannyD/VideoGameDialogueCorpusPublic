
try(setwd("~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project_public/analysis/"))

library(rjson)
library(ggplot2)

folders = list.dirs("../data", recursive = T)
folders = folders[sapply(folders,function(X){
  "stats_by_character.csv" %in% list.files(X)
})]


allGames = NULL
for(folder in folders){
  shortName = tail(strsplit(folder,"/")[[1]],1)
  js = fromJSON(file = paste0(folder,"/meta.json"))
  alternativeMeasure = FALSE
  if(!is.null(js$alternativeMeasure)){
    alternativeMeasure = js$alternativeMeasure
  }
  if(!is.null(js$mainPlayerCharacters) & length(js$mainPlayerCharacters)>0){
    mainChar = js$mainPlayerCharacters
    
    statsByChar = read.csv(paste0(folder,"/stats_by_character.csv"),stringsAsFactors = F)
    statsByChar = statsByChar[!is.na(statsByChar$words),]
    statsByChar = statsByChar[statsByChar$words>0,]
    statsByChar = statsByChar[statsByChar$group!="neutral",]
    
    stats = read.csv(paste0(folder,"/stats.csv"),stringsAsFactors = F)
    #totalWords = sum(statsByChar$words)
    totalWords = stats[stats$group=="TOTAL",]$words
    mainCharWords = statsByChar[match(mainChar,statsByChar$charName),]$words
    mainCharGroups = statsByChar[match(mainChar,statsByChar$charName),]$group
    mainCharProp = mainCharWords/totalWords
    
    dx = data.frame(
      folder = folder,
      series = js$series,
      game = js$game,
      alternativeMeasure = alternativeMeasure,
      group = mainCharGroups,
      charName = mainChar,
      dialogueProp = mainCharProp
      )
    
     allGames = rbind(allGames, dx)
    }
}

allGames = allGames[!is.na(allGames$dialogueProp),]
allGames = allGames[(!allGames$alternativeMeasure)| (allGames$game=="Horizon Forbidden West"),]

HFBProp = allGames[allGames$game=="Horizon Forbidden West",]$dialogueProp
allGames[allGames$dialogueProp>=HFBProp,]


