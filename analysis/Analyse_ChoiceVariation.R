library(rjson)
library(ggplot2)
library(tidyverse)
source("https://raw.githubusercontent.com/datavizpyr/data/master/half_flat_violinplot.R")

try(setwd("~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project/analysis/"))

folders = list.dirs("../data", recursive = T)
folders = folders[sapply(folders,function(X){
  "transitions.csv" %in% list.files(X)
})]


allGames= NULL
allData = NULL
transitionStrings = NULL
randChoices = NULL
for(folder in folders){
  print(folder)
  js = fromJSON(file = paste0(folder,"/meta.json"))
  alternativeMeasure = FALSE
  if(!is.null(js$alternativeMeasure)){
    alternativeMeasure = js$alternativeMeasure
  }
  if(!alternativeMeasure){
    cvFile = paste0(folder,"/choiceVariation.csv")
    randFile = paste0(folder,"/stats_randomChoices.csv")
    statsFile = paste0(folder,"/stats.csv")
    if(file.exists(cvFile) & file.exists(statsFile) & file.exists(randFile)){
      
      stats = read.csv(statsFile,stringsAsFactors = F)
      d = read.csv(cvFile,stringsAsFactors = F)
      
      totalNonChoiceFemale = d[!is.na(d$totalNonChoice.femaleWords),]$totalNonChoice.femaleWords[1]
      totalNonChoiceMale = d[!is.na(d$totalNonChoice.maleWords),]$totalNonChoice.maleWords[1]
      d = d[is.na(d$totalNonChoice.maleWords),]
      allData = rbind(allData,d[,c("folder","maxF.maleWords",
                                   "maxF.femaleWords","maxM.maleWords",
                                   "maxM.femaleWords")])
      minFemaleProportion = (totalNonChoiceFemale+ sum(d$maxM.femaleWords)) / 
          (totalNonChoiceFemale + totalNonChoiceMale + 
             sum(d$maxM.femaleWords) + sum(d$maxM.maleWords))
      maxFemaleProportion = (totalNonChoiceFemale+ sum(d$maxF.femaleWords)) / 
          (totalNonChoiceFemale + totalNonChoiceMale + 
            sum(d$maxF.femaleWords) + sum(d$maxF.maleWords))
      
      mainFemaleProp = stats[stats$group=="female",]$words/
          (stats[stats$group=="female",]$words + stats[stats$group=="male",]$words)
      
      diffMainToFemaleMax = maxFemaleProportion - mainFemaleProp
      diffMainToFemaleMin = minFemaleProportion - mainFemaleProp 
      
      allGames = rbind(allGames,data.frame(
        folder = folder,
        game = js$game,
        series = js$series,
        minFemaleProportion = minFemaleProportion,
        maxFemaleProportion = maxFemaleProportion,
        mainFemaleProp = mainFemaleProp,
        diffMainToFemaleMax = diffMainToFemaleMax,
        diffMainToFemaleMin = diffMainToFemaleMin,
        stringsAsFactors = F
      ))
      
      # Distributions from random choices
      rand = read.csv(randFile, stringsAsFactors = F)
      rand$folder = folder
      rand$maleWords = rand$maleWords + totalNonChoiceMale
      rand$femaleWords = rand$femaleWords + totalNonChoiceFemale
      rand$femaleProp = rand$femaleWords / (rand$maleWords + rand$femaleWords)
      randChoices = rbind(randChoices,rand)
      
    }
  }
}

allGames = allGames[order(allGames$minFemaleProportion),]
allGames$num = 1:nrow(allGames)
allGames$game = as.character(allGames$game)
allGames$game[grepl("Mario",allGames$game)] = "SuperMario RPG"
allGames$game = factor(allGames$game,levels = allGames$game[order(allGames$minFemaleProportion)])

randChoices$game = allGames[match(randChoices$folder,allGames$folder),]$game

meanRand = tapply(randChoices$femaleProp,randChoices$folder,mean)
quantileRand = tapply(randChoices$femaleProp,randChoices$folder,quantile,probs=c(0.025,0.975))
randStats = data.frame(
  folder = names(meanRand),
  mean = meanRand,
  low = unlist(lapply(quantileRand,head,n=1)),
  high = unlist(lapply(quantileRand,tail,n=1))
)
allGames$randomMean = randStats[match(allGames$folder,randStats$folder),]$mean
allGames$randomLow = randStats[match(allGames$folder,randStats$folder),]$low
allGames$randomHigh = randStats[match(allGames$folder,randStats$folder),]$high

pdf("../results/graphs/Choices_MinMax.pdf", height=3,width=6)
ggplot(data = allGames[!is.na(allGames$minFemaleProportion),], 
       mapping = aes(y = minFemaleProportion*100,x=game)) +
  geom_errorbar(mapping = aes(ymin = minFemaleProportion*100,
                              ymax = maxFemaleProportion*100),
                width=0.6) +
  geom_errorbar(mapping = aes(ymin = randomLow*100,
                              ymax = randomHigh*100),
                width=0.3, colour="red") +
  geom_point(mapping=aes(y=randomMean*100,x=game),
                shape=16, color="red") +
 # theme(legend.position = "top") +
  ylab("Female dialogue (%)")+
  xlab("") +
  coord_flip(ylim=c(0,50))
dev.off()


################################
# OTHER STUFF
################################

ggplot(data = allGames[!is.na(allGames$minFemaleProportion),], 
       mapping = aes(y = 0,x=game)) +
  geom_hline(yintercept = 0,color="gray")+
  geom_linerange(mapping = aes(ymin = diffMainToFemaleMin*100,
                               ymax = diffMainToFemaleMax*100)) +
  geom_point(mapping=aes(y=diffMainToFemaleMax*100,x=game)) + 
  geom_point(mapping=aes(y=diffMainToFemaleMin*100,x=game)) + 
  #geom_point(mapping=aes(y=0,x=game),color="red") + 
  ylab("% difference from full female dialogue proportion") +
  xlab("") +
  coord_flip()

# Example: FFVII

folder = "../data/FinalFantasy/FFVII/"
d = read.csv(paste0(folder,"/choiceVariation.csv"),stringsAsFactors = F)
d = d[!is.na(d$maxM.femaleWords),]

d$maxM.femaleAdvantage = d$maxM.femaleWords - d$maxM.maleWords
d$maxF.femaleAdvantage = d$maxF.femaleWords - d$maxF.maleWords


#par(mfrow=c(2,1),mar=c(4,2,2,0))
#xlim = c(-550,450)
#breaks = seq(from=xlim[1],to=xlim[2],by=20)
#hist(d$maxF.femaleAdvantage,breaks=breaks,xlim=xlim,main="",xlab="")
#hist(d$maxM.femaleAdvantage,breaks=breaks,xlim=xlim,main="",xlab="Female advantage (words)")

dx = data.frame(
  FemaleAdvantage = c(d$maxF.femaleAdvantage,d$maxM.femaleAdvantage),
  Strategy = rep(c("Maximise Female dialogue","Maximise Male dialogue"),
                 times = c(nrow(d),nrow(d)))
  )
dx$Strategy = relevel(factor(dx$Strategy),"Maximise Male dialogue")

ggplot(dx, aes(x=FemaleAdvantage,color=Strategy)) +
  geom_density(bw=20) + 
  theme(legend.position = "top") +
  xlab("Female advantage (words)") +
  geom_vline(xintercept = 0) +
  coord_cartesian(xlim = c(-200,200))

# Test if distribution is centered around zero.
t.test(d$maxF.femaleAdvantage, mu = 0)
t.test(d$maxM.femaleAdvantage, mu = 0)

# We simulated an omnicient player who tries to maximise dialogue from one gender while 
# minimising the dialogue from another (without repeat encounters).
# A player trying to maximise female dialogue over male would succeed in 
# observing more female dialogue than male dialogue in 58.7% of dialogue trees, 
#  on average seeing 2.7 more words spoken by females than males in each dialogue tree (marginally significant, p = 0.04).
#  When maximising male dialogue over female, these figures are 86.9% and 25.3 words (highly significant, p < 0.0001).
prop.table(table(d$maxF.femaleWords > d$maxF.maleWords))
prop.table(table(d$maxM.maleWords > d$maxM.femaleWords))

mean(d$maxF.femaleAdvantage)
abs(mean(d$maxM.femaleAdvantage))

d = d[order(d$maxM.femaleAdvantage),]
barplot(d$maxM.femaleAdvantage,horiz = T)

d = d[order(d$maxF.femaleAdvantage),]
barplot(d$maxF.femaleAdvantage,horiz = T)


# All choices

prop.table(table(allData$maxF.femaleWords > allData$maxF.maleWords))
prop.table(table(allData$maxM.maleWords > allData$maxM.femaleWords))

allData$maxF.femaleAdvantage = allData$maxF.femaleWords - allData$maxF.maleWords
allData$maxM.femaleAdvantage = allData$maxM.femaleWords - allData$maxM.maleWords

#t.test(allData$maxF.femaleAdvantage,mu=0)
#t.test(allData$maxM.femaleAdvantage,mu=0)

# When maximising female words, gain this many female words on average:
mean(allData$maxF.femaleAdvantage)
# When maximising male words, gain this many male words on average:
(-mean(allData$maxM.femaleAdvantage))

# For Maximinsing female words, when succeeding, gain this many female words:
mean(allData[allData$maxF.femaleWords > allData$maxF.maleWords,]$maxF.femaleAdvantage)
# For Maximinsing male words, when succeeding, gain this many male words:
mean(-allData[allData$maxM.maleWords > allData$maxM.femaleWords,]$maxM.femaleAdvantage)

t.test(allData$maxF.femaleAdvantage,allData$maxM.femaleAdvantage,paired = T)

par(mfrow=c(2,1),mar=c(4,2,2,0))
xlim = c(-650,550)
breaks = seq(from=xlim[1],to=xlim[2],by=25)
hist(allData$maxF.femaleAdvantage,breaks=breaks,xlim=xlim,main="",xlab="")
hist(allData$maxM.femaleAdvantage,breaks=breaks,xlim=xlim,main="",xlab="Female advantage (words)")
