library(rjson)
library(ggplot2)
library(dplyr)
library(tidyr)
library(lme4)
library(ggrepel)
try(setwd("~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project/analysis/"))

getCharacterNamesInDialogue = function(dialogue){
  nx = unique(names(unlist(dialogue[[1]])))
  nx = unique(gsub("CHOICE\\.","",nx))
  return(nx)
}

# Find main game folders (with meta.json files)
folders = list.dirs("../data/", recursive = T)
folders = folders[sapply(folders,function(X){
  "meta.json" %in% list.files(X) &
  "data.json" %in% list.files(X)
})]

# Double-check altMeasures
alt = sapply(folders, function(folder){
  js = fromJSON(file = paste0(folder,"/meta.json"))
  altMeasure = FALSE
  if("alternativeMeasure" %in% names(js)){
    altMeasure = js$alternativeMeasure
  }
  return(altMeasure)
})
names(alt) = gsub("//","/",names(alt))
names(alt) = paste0(names(alt),"/")

stats = read.csv("../results/generalStats.csv",stringsAsFactors = F)
stats$alternativeMeasure = stats$alternativeMeasure=="True"
toCheck = stats$folder %in% names(alt)
stats$alternativeMeasure[toCheck] = alt[match(stats[toCheck,]$folder,names(alt))]

# Total corpus size
#  (from getAllCharacterTexts, which filters ACTION etc.)
totalDialogue = sum(stats[!stats$alternativeMeasure & stats$group=="TOTAL",]$words,na.rm=T)
totalDialogue
# This is now written by getStatistics.py
#cat(format(totalDialogue,big.mark=","),file="../results/latexStats/totalDialogueWords.tex")


d = sapply(folders, function(folder){
  print(folder)
  shortName = tail(strsplit(folder,"/")[[1]],1)
  js = fromJSON(file = paste0(folder,"/meta.json"))
  
  # We need to check that character names from the meta
  #  actually appear in the dialogue:
  dialogue = fromJSON(file=paste0(folder,"/data.json"))
  charsInDialogue = getCharacterNamesInDialogue(dialogue)
  nMaleChars = sum(charsInDialogue %in% js$characterGroups$male)
  nFemaleChars = sum(charsInDialogue %in% js$characterGroups$female)
  
  altMeasure = FALSE
  if("alternativeMeasure" %in% names(js)){
    altMeasure = js$alternativeMeasure
  }
  folder = gsub("/+","/",folder)
  if(!grepl("/$",folder)){
    folder = paste0(folder,"/")
  }
  return(c(
        folder = folder,
        game = js$game,
        series = js$series,
        year = js$year,
        nMaleCharacters = nMaleChars,
        nFemaleCharacters = nFemaleChars,
        alternativeMeasure = altMeasure,
        shortName = shortName
        ))
})

d = as.data.frame(t(d),stringsAsFactors = F)
d$year=as.numeric(d$year)
d$nMaleCharacters = as.numeric(d$nMaleCharacters)
d$nFemaleCharacters = as.numeric(d$nFemaleCharacters)
d$alternativeMeasure = d$alternativeMeasure == "TRUE"

# Take out alternative script measures
d = d[!d$alternativeMeasure,]


d$propFemaleCharacters = d$nFemaleCharacters/(d$nFemaleCharacters + d$nMaleCharacters)

d$words_Female = sapply(d$folder,function(folder){
  n = stats[stats$folder==folder & stats$group=="female" & !stats$alternativeMeasure,]$words
  if(length(n)==1){
    return(n)
  } else{
    return(0)
  }
})

d$words_Male = sapply(d$folder,function(folder){
  n = stats[stats$folder==folder & stats$group=="male"  & !stats$alternativeMeasure,]$words
  if(length(n)>=1){
    if(length(n)>1){
      print("  Warning: too many cases?")
      print(paste0("   ",folder))
      return(n[1])
    } else{
      return(n)
    }
  } else{
    return(0)
  }
})

d =d[!is.na(d$words_Female),]
d =d[!is.na(d$words_Male),]
d =d[d$words_Female>0 & d$words_Male>0,]

d$propFemaleWords = d$words_Female / (d$words_Female+ d$words_Male)
d$propMaleWords = d$words_Male / (d$words_Female+ d$words_Male)

# Total corpus size (just male and female)
sum(d$words_Female+d$words_Male)

#########
# Write general stats
minFemaleProp = d[d$propFemaleWords==min(d$propFemaleWords),]
maxFemaleProp = d[d$propFemaleWords==max(d$propFemaleWords),]

minFemalePropStr = paste0(round(100*minFemaleProp$propFemaleWords),"\\% (\\emph{",minFemaleProp$game,"})")
maxFemalePropStr = paste0(round(100*maxFemaleProp$propFemaleWords),"\\% (\\emph{",maxFemaleProp$game,"})")

# Moved to Analyse_WordsPerGender
#cat(minFemalePropStr,file="../results/latexStats/gameWithMinimumFemaleWords.tex")
#cat(maxFemalePropStr,file="../results/latexStats/gameWithMaximumFemaleWords.tex")

d$wordsPerCharacter_Female = d$words_Female/d$nFemaleCharacters
d$wordsPerCharacter_Male = d$words_Male/d$nMaleCharacters

d$wordsPerCharacter_Ratio = d$wordsPerCharacter_Female / d$wordsPerCharacter_Male

# Test relationship between proportion of female characters and time
propFemaleOverTime = cor.test(d$propFemaleWords,d$year)
#dxxx = d[!d$shortName %in% c("KingsQuest2","KingsQuest4"),]
#cor.test(dxxx$propFemaleWords,dxxx$year)

propFemaleOverTimeStr = paste0("$r$=",round(propFemaleOverTime$estimate,2), ", $n$=",nrow(d), ", $p$=",round(propFemaleOverTime$p.value,3))
##cat(propFemaleOverTimeStr, file="../results/latexStats/propFemaleOverTime.tex")

# Increase in prop female over time
pm = lm(propFemaleWords~year, data=d)
incPropFemalePerDecade = round((pm$coefficients['year']*100) * 10,1)
#cat(incPropFemalePerDecade, file="../results/latexStats/incPropFemalePerDecade.tex")

# Test non-linearity
pm2 = lm(propFemaleWords ~ year + I(year^2), data=d)
anova(pm,pm2)
# (not significant)

#cat(min(d$year), file="../results/latexStats/earliestYear.tex")
#cat(max(d$year), file="../results/latexStats/latestYear.tex")


# Correlation between measures
stats = stats[stats$group %in% c("male","female"),]
lingMeasures = c("lines","sentences","words","syllables")
measureCor = matrix(NA,nrow=length(lingMeasures), ncol=length(lingMeasures))
rownames(measureCor) = lingMeasures
colnames(measureCor) = lingMeasures
for(i in 1:(length(lingMeasures)-1)){
  for(j in (i+1):length(lingMeasures)){
    measureCor[i,j] = cor(stats[,lingMeasures[i]], stats[,lingMeasures[j]],use = "complete")
  }
}
min(measureCor,na.rm=T)
 

# Readability measures are not correlated
readMeasures = c("FleschKincaidReadability","FleschReadability","DaleChallReadability")
measureCorRead = matrix(NA,nrow=length(readMeasures), ncol=length(readMeasures))
rownames(measureCorRead) = readMeasures
colnames(measureCorRead) = readMeasures
for(i in 1:(length(readMeasures)-1)){
  for(j in (i+1):length(readMeasures)){
    measureCorRead[i,j] = cor(stats[,readMeasures[i]], stats[,readMeasures[j]],use = "complete")
  }
}
min(abs(measureCorRead),na.rm=T)

# Readability
getReadabilityTestText = function(readability,rt){
  paste0("game-level mean readability for male characters = ",
         round(mean(readability[1,],na.rm=T),2),
         ", sd = ",
         round(sd(readability[1,],na.rm=T),2),
         ", for female characters = ",
         round(mean(readability[2,],na.rm=T),2),
         ", sd = ",
         round(sd(readability[2,],na.rm=T),2),
         ", paired t-test t = ",
         round(rt$statistic,2),
         ", n = ",
         sum(!is.na(readability[1,])),
         ", p = ",
         round(rt$p.value,3)
  )
}

games = unique(stats$folder)

readability.DC = sapply(games, function(g){
  c(stats[stats$folder==g & stats$group=="male",]$DaleChallReadability,
    stats[stats$folder==g & stats$group=="female",]$DaleChallReadability)})
readability.DC.t = t.test(readability.DC[1,], readability.DC[2,], paired = T)
readability.DC.text = getReadabilityTestText(readability.DC,readability.DC.t)
cat(readability.DC.text,file="../results/latexStats/readability-DC-TTest.tex")

readability.F = sapply(games, function(g){
  c(stats[stats$folder==g & stats$group=="male",]$FleschReadability,
    stats[stats$folder==g & stats$group=="female",]$FleschReadability)})
readability.F.t = t.test(readability.F[1,], readability.F[2,], paired = T)
readability.F.text = getReadabilityTestText(readability.F,readability.F.t)
cat(readability.F.text,file="../results/latexStats/readability-F-TTest.tex")

readability.FK = sapply(games, function(g){
  c(stats[stats$folder==g & stats$group=="male",]$FleschKincaidReadability,
    stats[stats$folder==g & stats$group=="female",]$FleschKincaidReadability)})
readability.FK.t = t.test(readability.FK[1,], readability.FK[2,], paired = T)
readability.FK.text = getReadabilityTestText(readability.FK,readability.FK.t)
cat(readability.FK.text,file="../results/latexStats/readability-FK-TTest.tex")

# Plot Readability
pdf("../results/graphs/Readability.pdf",width=6,height=4)
stats[stats$group %in% c("male","female"),] %>%
  ggplot(aes(x=group,y=DaleChallReadability)) +
  geom_boxplot()
dev.off()




#d$year.center = scale(d$year)
#mx = lmer(propFemaleWords ~ d$year.center + (1+year.center|series), data = d)
#summary(mx)

pdf('../results/graphs/ChangeOverTime.pdf', width=8,height=6)
ggplot(d,
       #d[!d$shortName %in% c("KingsQuest2","KingsQuest4"),],
       aes(x=year,y=propFemaleWords)) + 
  geom_point() +
  stat_smooth(method=lm, se = F) +
  coord_cartesian(ylim=c(0,1),xlim=c(1975,2025))+
  ylab("Proportion of female words spoken") +
  xlab("Year") +
  geom_text_repel(aes(label=shortName),color="dark gray")
dev.off()

ggplot(d,aes(x=year,y=wordsPerCharacter_Ratio)) + 
  geom_point()+
  geom_hline(yintercept=1) +
  ylab("Words per character: female:male ratio")


ggplot(d,aes(x=year,y=propFemaleCharacters)) + 
  geom_point()+
  coord_cartesian(ylim=c(0,1))+
  ylab("Proportion of female characters")


# Moved
# wordsVCharacters = ggplot(d,aes(y=propFemaleWords,x=propFemaleCharacters)) + 
#   coord_cartesian(ylim=c(0,1),xlim=c(0,1))+
#   xlab("Proportion of female characters") +
#   ylab("Proportion of female words") +
#   geom_abline(intercept=0,slope=1) +
#   geom_label(label="Females\nover-represented",x=0.19,y=0.85) +
#   geom_label(label="Females\nunder-represented",x=0.75,y=0.15) 
#   
# pdf("../results/graphs/WordsVsCharacters_noPoints.pdf",width=4,height = 3.5)
#   wordsVCharacters + geom_point(alpha=0)
# dev.off()
# pdf("../results/graphs/WordsVsCharacters.pdf", width=4,height = 3.5)
#   wordsVCharacters + geom_point()
# dev.off()


# Overall percentage of words
allGamesPropFemale = (sum(d$words_Female,na.rm=T)/(sum(d$words_Female,na.rm=T)+sum(d$words_Male,na.rm=T)))*100
allGamesPropMale = 100-allGamesPropFemale
dx = data.frame(
  Gender=factor(c("Male","Female"),levels=c("Male","Female")),
  percentageWords=c(allGamesPropMale,allGamesPropFemale))

# Moved
# pdf('../results/graphs/OverallWordsByGender.pdf',width=6,height=3)
# ggplot(dx,aes(x=1,y=percentageWords,fill=Gender))+ geom_bar(stat='identity')+
#   geom_hline(yintercept=50,linetype="dotted") +
#   coord_flip(ylim = c(0,100)) +
#   theme(panel.grid.major = element_blank(),
#         panel.grid.minor = element_blank(),
#         panel.background = element_blank(),
#         axis.text.y = element_blank(),
#         axis.ticks.y = element_blank(),
#         legend.position = "top") +
#   scale_fill_discrete(breaks=c("Female","Male"),name="Gender")+
#   ylab("% Words Spoken") +
#   xlab("")
# dev.off()

allSeries = unique(d$series[!is.na(d$series)])

series = "Final Fantasy"
#for(series in allSeries){
  dx = d[d$series==series,]
  dx = dx[!is.na(dx$propFemaleCharacters),]
  dx$game = factor(dx$game, levels = unique(dx$game[order(dx$year,decreasing = T)]))
  sx = gather(dx, group, measurement, propFemaleWords:propMaleWords, factor_key=TRUE)
  sx$group = factor(sx$group,levels=c("propMaleWords","propFemaleWords"),labels=c("Male","Female"))
  sx$measurement = sx$measurement*100
  
  gx = ggplot(sx, aes(x=game,y=measurement,fill=group)) +
    geom_bar(stat='identity')+
    geom_hline(yintercept=50,linetype="dotted") +
    coord_flip(ylim = c(0,100)) +
    theme(panel.grid.major = element_blank(),
          panel.grid.minor = element_blank(),
          panel.background = element_blank(),
          legend.position = "top") +
    scale_fill_discrete(breaks=c("Female","Male"),name="Gender")+
    ylab("% Words Spoken") +
    xlab("")
  
  # write
  fileName = paste0("../results/graphs/series/",series,".pdf")
  fileName = gsub(" ","_",fileName)
  pdf(fileName,width=5,height=4)
  gx
  dev.off()
  
#}

  


# #############
# # Final Fantasy VII characters
#   (MOVED TO Analyse_FFVII_vs_Remake)
# 
# # TODO: rewrite using the stats_by_character.csv files
# sx = read.csv("../data/FinalFantasy/FFVII/stats_by_character.csv",stringsAsFactors = F)
# sx = rbind(sx, read.csv("../data/FinalFantasy/FFVII_Remake/stats_by_character.csv",stringsAsFactors = F))
# #sx = stats[stats$game %in% c("Final Fantasy VII", "Final Fantasy VII Remake"),]
# #sx = sx[grepl("Char_",sx$group),]
# 
# chosenCharacters = c("Aerith","Tifa","Jessie","Marlene","Cloud","Barret","Biggs","Red XIII")
# sx = sx[sx$charName %in% chosenCharacters,]
# sx$charName = factor(sx$charName,levels=chosenCharacters)
# 
# sx = sx %>% group_by(game) %>%
#   mutate(prop = words / sum(words)) 
# 
# change = tapply(sx$words,sx$charName,function(X){
#   print(X)
#   x = round(((X[2] - X[1]) /X[1])*100)
#   paste0(c("","+")[1+(x>0)],x,"%")
#  #paste(round(X[1]/X[2] * 100),"%")
# })
# changeD = data.frame(
#   x2 = 1:length(change),
#   y2 = tapply(sx$prop,sx$charName,max),
#   change = change,
#   game = "Final Fantasy VII"
# )
# 
# 
# pdf("../results/graphs/FFVII_Character_Comparison.pdf",
#     width=6,height=4)
# sx %>% ggplot(aes(x=charName,fill=game,y=prop)) +
#   geom_bar(stat="identity", position = 'dodge') +
#   theme(legend.position = "top",
#         panel.grid.major.x = element_blank()) + 
#   geom_vline(xintercept = seq(1.5,7.5,1),color="white")+
#   scale_fill_brewer(palette="Dark2") +
#   geom_text(data=changeD,aes(x=x2,y=y2,label=change),vjust=-0.2) +
#   coord_cartesian(ylim=c(0,0.55)) +
#   geom_label(label="Female",x=2.5,y=0.5,color="white",fill="black") +
#   geom_label(label="Male",x=6.5,y=0.5,color="white",fill="black") +
#   geom_vline(xintercept = 4.5,size=2)
# dev.off()
#   
#   
  
  
  
  
  