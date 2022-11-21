library(rjson)
library(dplyr)
try(setwd("~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project/analysis/"))

NUMBER_OF_SIMULATIONS = 100000
lengthVar = "words"

randomGender = function(words,groups){
  words = tapply(
    words,
    sample(unique(groups),length(words),replace = T),
    sum)
  words = words[c("female","male")]
  words[is.na(words)] = 0
  diff(words)
}

permuteGender = function(words,group){
  words = tapply(words,sample(group),sum)
  words = words[c("female","male")]
  words[is.na(words)] = 0
  diff(words)
}

getZ = function(true,dist){
  zscore = (true-mean(dist)) / sd(dist)
  pvalue = 1/length(dist)
  numAgainst = sum(true < dist)
  if(numAgainst>0){
    pvalue = numAgainst/ length(dist)
  }
  return(c(zscore=zscore,p=pvalue))
}

getZStats = function(fname=NULL,d=NULL){
  if(is.null(d)){
    d = read.csv(fname,stringsAsFactors = F)
    if(nrow(d)==0){
      return(c(NA,NA,NA,NA))
    }
  }
  
  d = d[d$group %in% c("female","male"),]
  totalWords = tapply(d[,lengthVar],d$group,sum,na.rm=T)
  true_diffInWords = diff(totalWords)
  
  random_diffInWords = replicate(NUMBER_OF_SIMULATIONS, randomGender(d[,lengthVar],d$group))
  zstats.random = getZ(true_diffInWords,random_diffInWords)
  
  permuted_diffInWords = replicate(NUMBER_OF_SIMULATIONS, permuteGender(d[,lengthVar],d$group))
  zstats.perm = getZ(true_diffInWords,permuted_diffInWords)
  return(c(zstats.random,zstats.perm))
}


folders = list.dirs("../data", recursive = T)
folders = folders[sapply(folders,function(X){
  "stats_by_character.csv" %in% list.files(X)
})]

set.seed(451)

res = NULL
for(folder in folders){
  print(folder)
  js = fromJSON(file = paste0(folder,"/meta.json"))
  
  alternativeMeasure = FALSE
  if(!is.null(js$alternativeMeasure)){
    alternativeMeasure = js$alternativeMeasure
  }
  shortName = tail(strsplit(folder,"/")[[1]],1)
  zstats = getZStats(fname = paste0(folder,"/stats_by_character.csv"))
  
  res = rbind(res, data.frame(
               shortName=shortName,
               game = js$game,
               series = js$series,
               year = js$year,
               alternativeMeasure = alternativeMeasure,
               z.random = zstats[1],
               p.random = zstats[2],
               z.perm = zstats[3],
               p.perm = zstats[4],
               stringsAsFactors = F))
}

write.csv(res,"../results/compareToBaseline.csv")

res2 = res[!is.na(res$z.random),]
numGamesSignificantRandomBias = sum(res2$p.random<0.05)
numGamesSignificantRandomBias.prop = numGamesSignificantRandomBias/nrow(res2)
ngStr = paste0(numGamesSignificantRandomBias," games (",round(numGamesSignificantRandomBias.prop*100),"\\%)")
cat(ngStr,file="../results/latexStats/numGamesSignificantRandomBias.tex")

numGamesSignificantPermBias = sum(res2$p.perm<0.05)
numGamesSignificantPermBias.prop = numGamesSignificantPermBias/nrow(res2)
ngStrP = paste0(numGamesSignificantPermBias)
cat(ngStrP,file="../results/latexStats/numGamesSignificantPermBias.tex")

# Run statistic for all games together
allGames= NULL
for(folder in folders){
  js = fromJSON(file = paste0(folder,"/meta.json"))
  # (Only collect one main parsing for each game)
  alternativeMeasure = FALSE
  if(!is.null(js$alternativeMeasure)){
    alternativeMeasure = js$alternativeMeasure
  }
  if((!alternativeMeasure) & (!grepl("Test",folder))){
    print(folder)
    sbcFile = paste0(folder,"/stats_by_character.csv")
    if(file.exists(sbcFile)){
      d = read.csv(paste0(folder,"/stats_by_character.csv"),stringsAsFactors = F)
      allGames = rbind(allGames,d)
    }
  }
}

allGames = allGames[!is.na(allGames$words),]
allGames = allGames[allGames$game!="Test",]

# Number of non-male/female characters
nonBinary = table(allGames[!allGames$group %in% c("male", "female","neutral","playerChoice","undefined","unknown","system","random","GenericFemale","GenericMale","not coded","cut"),]$group)
numNonBinary = sum(nonBinary)
cat(numNonBinary, file="../results/latexStats/numNonBinaryCharacters.tex")
cat(round(100*(numNonBinary / (numNonBinary + sum(allGames$group %in% c("male","female")))),2),
    file="../results/latexStats/percentageNonBinaryCharacters.tex")

allGames = allGames[allGames$group %in% c("male","female"),]
# Number of characters
cat(format(nrow(allGames),nsmall=1, big.mark=","),file="../results/latexStats/numOfCharacters.tex")
bt = binom.test(table(allGames$group))
#cat()

# Some games have vastly larger scripts than others
# Transform word count to words-per-thousand within a game
gameTotals = tapply(allGames$words, allGames$folder, sum)
allGames$words = 1000 * (allGames$words / gameTotals[allGames$folder])

set.seed(451)
zstatsAll = getZStats(d=allGames)
cat(format(zstatsAll[1],nsmall = 2,digits=2),file="../results/latexStats/RandomBaselineZ.tex")
cat(format(zstatsAll[2],scientific = F),     file="../results/latexStats/RandomBaselineP.tex")
cat(format(zstatsAll[3],nsmall = 2,digits=2),file="../results/latexStats/PermutedBaselineZ.tex")
cat(format(zstatsAll[4],scientific = F),     file="../results/latexStats/PermutedBaselineP.tex")

# Correlation between line and words by character
#corBetweenLinesAndWordsTest = cor.test(allGames$lines,allGames$words)
#corBetweenLinesAndWords = paste0("$r$=",round(corBetweenLinesAndWordsTest$estimate,2), ", $n$=",nrow(allGames), ", $p<$0.001")
#cat(corBetweenLinesAndWords, file="../results/latexStats/corBetweenLinesAndWords.tex")


plot(res$z.random,res$z.perm,xlim=c(-6,6))
abline(h=0)
abline(v=0)
rect(-2,-2,2,2)
text(res$z.random,res$z.perm,res$shortName)
plot(res$p.random,res$z.perm)
