library(rjson)
try(setwd("~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project/analysis/reliability/"))

folders = list.dirs("../../data", recursive = T)
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
  if(!alternativeMeasure){
    statsByChar = read.csv(paste0(folder,"/stats_by_character.csv"),stringsAsFactors = F)
    if(nrow(statsByChar)>0){
      statsByChar$year = js$year
      statsByChar = statsByChar[!statsByChar$group %in% c("system",'random','playerChoice','not coded'),]
      statsByChar = statsByChar[statsByChar$words>0,]
      statsByChar = statsByChar[statsByChar$lines>2,]
      statsByChar$propDialogue = log10(statsByChar$words)
      allGames = rbind(allGames, statsByChar)
    }
  }    
}

# Some games have gender defined in game code
allGames = allGames[allGames$game!="The Elder Scrolls II: Daggerfall",]
allGames = allGames[allGames$game!="The Elder Scrolls IV: Oblivion",]

allGames = allGames[allGames$charName!="GOTO",]

set.seed(451)

toCode = data.frame()
for(folder in unique(allGames$folder)){
  dx = allGames[allGames$folder==folder,]
  maxSample = min(c(15,nrow(dx)))
  chosenCharacters = sample(1:nrow(dx),maxSample,prob=dx$propDialogue)  
  toCode = rbind(toCode,dx[chosenCharacters,])
}

toCode2 = data.frame()
for(series in unique(toCode$series)){
  dx = toCode[toCode$series==series,]
  # Randomly remove duplicated characters
  dx = dx[sample(1:nrow(dx)),]
  dx = dx[!duplicated(dx$charName),]
  # Keep just 10 from each 
  dx = dx[unlist(tapply(1:nrow(dx),dx$folder,function(X){
    maxSample = min(c(10, length(X)))
    sample(X,maxSample)
  })),]
  toCode2 = rbind(toCode2,dx)
}


toCode2 = toCode2[order(toCode2$series,toCode2$year),c("folder","game","year","series","charName")]
toCode2$gender = ""
toCode2$Confidence = ""
toCode2$Comments = ""
write.csv(toCode2,"../../results/reliabilityCoding.csv",row.names = F)



