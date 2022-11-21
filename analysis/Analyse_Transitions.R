
# Notes on the Bechdel test:
# First, not all the scripts have the dialogue in the order in which they appear to the player, with markers for breaks between conversations. This makes it difficult to automatically detect a conversation between two women. (the stats on transitions are only run on games where this information is available).
# The second issue is that the Bechdel test is very strict. The data in our corpus is often a sample, and often only one possible play-through. For any given game, it would be very hard make the claim that there is NO dialogue between two women.
# The third issue is that video games often have more dialogue than the average TV show or film. So the probability of there being NO female-female dialogue is very low. So most games would pass the test. But this doesn't necessarily mean that there are no problems, and it doesn't show which games have more problems than others.
# The fourth issue is that it's possible for a game to potentially pass the Bechdel test, while not actually passing it for a specific player's experience. The test is well suited to short scripts with canonical forms (like TV, Film, books), but conceptually more difficult to apply to interactive texts like video games.
# 
# So, I think it makes more sense to apply a probabilistic test that shows a bias away from an expected value. That's what the transition stats tried to do.
# 
# Having said that, it's perfectly possible to go through the game's code and find cases of dialogue between women. I could even write a script that found potential cases that could be shown to a human to verify.
# 
# I'm fairly certain that The Secret of Monkey Island does not pass the Bechdel test, simply because there are so few female characters and I don't think there's a scene with two women in. The stats support this. According to our corpus, there apparently is only one case of a transition between two women in any of Monkey Island 1, 2 or 3. But when I looked it up, it was this from Monkey Island 2:
#   
#   {"Woman 1 watching spit contest": "(claps)"},
# {"Woman 2 watching spit contest": "(claps)"},



library(rjson)
library(Gmisc)
library(dplyr)
library(RColorBrewer)
library(grid)
library(ggplot2)
library(ggrepel)

try(setwd("~/Documents/Cardiff/VideoGameScripts/project/analysis/"))

numberOfPermutationsForAllGames = 10000
numberOfPermutationsForEachGame = 1000

folders = list.dirs("../data", recursive = T)
folders = folders[sapply(folders,function(X){
  "transitions.csv" %in% list.files(X)
})]


allGames= NULL
transitionStrings = NULL
for(folder in folders){
  print(folder)
  shortName = tail(strsplit(folder,"/")[[1]],1)
  js = fromJSON(file = paste0(folder,"/meta.json"))
  alternativeMeasure = FALSE
  if(!is.null(js$alternativeMeasure)){
    alternativeMeasure = js$alternativeMeasure
  }
  suitableForTransitions = TRUE
  if(!is.null(js$sourceFeatures$dialogueOrder)){
      suitableForTransitions = js$sourceFeatures$dialogueOrder
  }
  
  if(suitableForTransitions & (!alternativeMeasure)){
    sbcFile = paste0(folder,"/transitions.csv")
    if(file.exists(sbcFile)){
      d = read.csv(sbcFile,stringsAsFactors = F)
      if(nrow(d)>0){
        d$shortName = shortName
      }
      allGames = rbind(allGames,d)
    }
    tsFile = paste0(folder,"/transitions_all.txt")
    if(file.exists(tsFile)){
      ts = suppressWarnings(readLines(tsFile)[1])
      transitionStrings = rbind(transitionStrings,
                    data.frame(folder=folder,series=d$series[1],
                               game=d$game[1],
                               ts = ts,
                               stringsAsFactors = F))
    }
  }
}
# Trim final stroke to make consistent
transitionStrings$folder = gsub("/$","",transitionStrings$folder)
allGames$folder = gsub("/$","",allGames$folder)


hasFemaleToFemale = sapply(unique(allGames$folder), function(fld){
  any(allGames[allGames$folder==fld,]$from=="female" & allGames[allGames$folder==fld,]$to=="female", na.rm = T)
})

hasFemaleToFemale[!hasFemaleToFemale]

getTransitions = function(allGames, raw=F){

  maleToMale = sum(allGames[allGames$from=="male" & allGames$to=="male",]$frequency)
  maleToFemale = sum(allGames[allGames$from=="male" & allGames$to=="female",]$frequency)
  femaleToMale = sum(allGames[allGames$from=="female" & allGames$to=="male",]$frequency)
  femaleToFemale = sum(allGames[allGames$from=="female" & allGames$to=="female",]$frequency)
  
  if(raw){
    maleToMaleP = maleToMale
    maleToFemaleP = maleToFemale
    femaleToMaleP = femaleToMale
    femaleToFemaleP = femaleToFemale
  }
  else{
    total = sum(maleToMale,maleToFemale,femaleToMale,femaleToFemale)
    maleToMaleP = maleToMale/(maleToMale+maleToFemale)
    maleToFemaleP = maleToFemale/(maleToMale+maleToFemale)
    femaleToMaleP = femaleToMale/(femaleToMale+femaleToFemale)
    femaleToFemaleP = femaleToFemale/(femaleToMale+femaleToFemale)
  }
  
  transitionTable =matrix(c(maleToMaleP, femaleToMaleP, maleToFemaleP, femaleToFemaleP),nrow=2)
  rownames(transitionTable) = c("m","f")
  colnames(transitionTable) = c("m","f")
  
  return(transitionTable)
  
}

permuteTransitionString = function(X){
  X = sample(X)
  tab = table(X[1:(length(X)-1)], X[2:length(X)])
  tab = tab[c("m","f"),c("m","f")]
  tab[is.na(tab)] = 0
  transitionProbs = prop.table(tab,1)
}

getZP = function(tpPerm,trueProb){
  Z = (trueProb - mean(tpPerm))/sd(tpPerm)
  sx = sum(tpPerm >trueProb)
  P = 1/length(tpPerm)
  if(sx>0){
    P = sx/length(tpPerm)  
  }
  if(Z<0){
    P = 1 - P
  }
  if(P==0){
    P = 1/length(tpPerm)
  }
  return(c(mean = mean(tpPerm), z = Z,p = P))
}

getPermutedStats = function(ts, trueTransitionProbs,numPerm){
  lines = strsplit(ts,"")[[1]]
  transProbsPerm = replicate(numPerm, permuteTransitionString(lines))
  m2m = getZP(transProbsPerm["m","m",],trueTransitionProbs["m","m"])
  m2f = getZP(transProbsPerm["m","f",],trueTransitionProbs["m","f"])
  f2f = getZP(transProbsPerm["f","f",],trueTransitionProbs["f","f"])
  f2m = getZP(transProbsPerm["f","m",],trueTransitionProbs["f","m"])
  
  return(c(m2m, f2m, m2f, f2f))
}


# STATS FOR ALL DATA

trueTransitions.AllGames = getTransitions(allGames)
trueTransitions.AllGames.Raw = getTransitions(allGames,raw=TRUE)

trueTransitionsString.AllGames = paste0(transitionStrings$ts)
permutedTransitionStats.AllGames = 
  getPermutedStats(trueTransitionsString.AllGames,
                   trueTransitions.AllGames,
                   numberOfPermutationsForAllGames)
names(permutedTransitionStats.AllGames) = paste(
  rep(c("m2m", "f2m", "m2f", "f2f"),each=3),names(permutedTransitionStats.AllGames),sep=".")

########################
# Stats for each game

set.seed(238)
print("Running stats ...")
permutationResults = NULL
for(folder in unique(allGames$folder)){
  print(folder)
  dx = allGames[allGames$folder == folder,]
  trueTransitionProbs = getTransitions(dx)
  trueTransitionProbsFlat = as.vector(trueTransitionProbs)
  names(trueTransitionProbsFlat) = c("m2m", "f2m", "m2f", "f2f")
  
  trueTransitionRaw = getTransitions(dx,raw = T)
  trueTransitionRawFlat = as.vector(trueTransitionRaw)
  names(trueTransitionRawFlat) = c("m2m", "f2m", "m2f", "f2f")
  
  if(any(is.nan(trueTransitionProbs))){
    print(paste("No data for ",folder))
  } else{
    trueTransitionString = transitionStrings[transitionStrings$folder==folder,]$ts
    permutedTransitionStats = getPermutedStats(trueTransitionString,trueTransitionProbs,numberOfPermutationsForEachGame)
    names(permutedTransitionStats) = paste(rep(c("m2m", "f2m", "m2f", "f2f"),each=3),names(permutedTransitionStats),sep=".")
    
    res = data.frame(folder=dx$folder[1],
                     series = dx$series[1],
                     game = dx$game[1],
                     shortName = dx$shortName[1])

    tt = matrix(trueTransitionProbsFlat,nrow=1)
    colnames(tt) = names(trueTransitionProbsFlat)
    res = cbind(res,tt)
    
    ttr = matrix(trueTransitionRawFlat,nrow=1)
    colnames(ttr) = paste0(names(trueTransitionRawFlat),".raw")
    res = cbind(res,ttr)

    pt = matrix(permutedTransitionStats,nrow=1)
    colnames(pt) = names(permutedTransitionStats)
    res = cbind(res,pt)
  
    permutationResults = rbind(permutationResults,res)
  }
  
}

permutationResults$diffExpEmp.m2m = permutationResults$m2m - permutationResults$m2m.mean
permutationResults$diffExpEmp.f2f = permutationResults$f2f - permutationResults$f2f.mean

write.csv(permutationResults, "../results/transitionsPermutationTest.csv",row.names = F)

# Individual example: 
folder = "../data/StardewValley/StardewValley"
dx = allGames[allGames$folder == folder,]
trueTransitionProbs = getTransitions(dx)
trueTransitionProbsFlat = as.vector(trueTransitionProbs)
names(trueTransitionProbsFlat) = c("m2m", "f2m", "m2f", "f2f")
ts = transitionStrings[transitionStrings$folder==folder,]$ts
lines = strsplit(ts,"")[[1]]
transProbsPerm = replicate(1000, permuteTransitionString(lines))

par(mfrow=c(2,2))
for(g1 in c("m","f")){
  for(g2 in c("m","f")){
    hist(transProbsPerm[g1,g2,],xlim=c(0,1),main=paste(g1,"to",g2))
    abline(v=trueTransitionProbs[g1,g2],col="red")
  }
}
par(mfrow=c(1,1))
########
# Plot difference from expected

permutationResults$shortName2 = permutationResults$shortName
permutationResults$shortName2 = gsub("KingdomHearts","KH",permutationResults$shortName2)
permutationResults$shortName2 = gsub("KingsQuest","KQ",permutationResults$shortName2)
permutationResults$shortName2 = gsub("_Remake","-R",permutationResults$shortName2)
permutationResults$shortName2 = gsub("_B","",permutationResults$shortName2)
permutationResults$shortName2 = gsub("_DS","",permutationResults$shortName2)
permutationResults$shortName2[permutationResults$shortName2=="TheSecretOfMonkeyIsland"] = "MI1"
permutationResults$shortName2[permutationResults$shortName2=="MonkeyIsland2"] = "MI2"
permutationResults$shortName2[permutationResults$shortName2=="TheCurseOfMonkeyIsland"] = "MI3"
permutationResults$shortName2[permutationResults$shortName2=="SuperMarioRPG"] = "SMario"
permutationResults$shortName2[permutationResults$shortName2=="StardewValley"] = "Stardew"
permutationResults$shortName2[permutationResults$shortName2=="FFX_B"] = "FFX"

pdf('../results/graphs/transitions/Transitions_DiffFromExpected.pdf', width=6,height=6)
  ggplot(permutationResults,aes(x=diffExpEmp.f2f*100,y=diffExpEmp.m2m*100)) + 
    geom_point() +
    coord_cartesian(ylim=c(-32,32),xlim=c(-32,32))+
    ylab("Male-Male transitions:\n(% difference from expected)") +
    geom_hline(yintercept = 0) + geom_vline(xintercept = 0) + 
    xlab("Female-Female transitions:\n(% difference from expected)") +
    geom_text_repel(aes(label=shortName2),color="dark gray",force = 10)
dev.off()

  
  ggplot(permutationResults,aes(x=f2f.z,y=m2m.z)) + 
    annotate("rect", xmin = -1000, xmax = 1000, ymin = -2, ymax = 2, alpha = .1) +
    annotate("rect", xmin = -2, xmax = 2, ymin = -1000, ymax = 1000, alpha = .1) +
    geom_point() +
    coord_cartesian(ylim=c(-30,30),xlim=c(-30,30))+
    ylab("Male-Male transitions:\n(z-score difference from expected)") +
    geom_hline(yintercept = 0) + geom_vline(xintercept = 0) + 
    xlab("Female-Female transitions:\n(z-score difference from expected)") +
    geom_text_repel(aes(label=shortName2),color="dark gray",force = 10)  
  
  
xs = c(-20,-10,0,10,20)
ls = log(100+xs)
pdf("../results/graphs/transitions/Transitions_DiffFromExpected_ZScores.pdf",width=6.5,height=6)
  ggplot(permutationResults,aes(x=log(100+f2f.z),y=log(100+m2m.z))) + 
    annotate("rect", xmin = -1000, xmax = 1000, ymin = log(100-2), ymax = log(102), alpha = .1) +
    annotate("rect", xmin = log(100-2), xmax = log(102), ymin = -1000, ymax = 1000, alpha = .1) +
    geom_point() +
    coord_cartesian(ylim=c(4.25,4.9),xlim=c(4.25,4.9))+
    ylab("Male-Male transitions:\n(z-score difference from expected)") +
 #   geom_hline(yintercept = 0) + geom_vline(xintercept = 0) + 
    xlab("Female-Female transitions:\n(z-score difference from expected)") +
    geom_text_repel(aes(label=shortName2),color="dark gray",force = 10) + 
    scale_x_continuous(breaks=ls,labels=xs,
       sec.axis = sec_axis(~.*1,
                           breaks = ls,
                           labels=c("Fewer female-female transitions\nthan expected","",
                                    "As expected","",
                                    "More female-female transitions\nthan expected")))+
  scale_y_continuous(breaks=ls,labels=xs) +
    theme(panel.grid.minor = element_blank())
dev.off()

# In general, transitions within genders is lower than expected,
# while transitions between genders is higher than expected
# e.g. HZD: true f2f is 0.33. Expected is 0.55.
hist(permutationResults$f2f.z)
mean(permutationResults$f2f.z)

hist(permutationResults$m2m.z)
mean(permutationResults$m2m.z)

hist(permutationResults$f2m.z)
mean(permutationResults$f2m.z)

hist(permutationResults$m2f.z)
mean(permutationResults$m2f.z)

# number of games with within lower than expected f2f
table(permutationResults$f2f.z < 0 & permutationResults$f2f.p<0.05)
table(permutationResults$m2m.z < 0 & permutationResults$m2m.p<0.05)
# 22 games had significantly lower f-f transitions than expected by chance, 
# and 22 games had significantly lower m-m transitions than expected by chance.
binom.test(table(permutationResults$f2f.z < permutationResults$m2m.z))

table(permutationResults$diffExpEmp.f2f <  permutationResults$diffExpEmp.m2m)


# KH 3 has about as much f2f and f2m as you'd expect,
# but has more m2m and less m2f
# i.e. men are biased to speak to other men

# Some imbalances:
table(permutationResults$m2m.z < 0 & permutationResults$m2m.p<0.05, 
      permutationResults$f2f.z < 0 & permutationResults$f2f.p<0.05)

permutationResults[(permutationResults$m2m.z <0 & permutationResults$m2m.p<0.05) &
                     (permutationResults$f2f.z >0 & permutationResults$f2f.p<0.05),]
permutationResults[(permutationResults$m2m.z >0 & permutationResults$m2m.p<0.05) &
                     (permutationResults$f2f.z <0 & permutationResults$f2f.p<0.05),]


#########
plot(permutationResults$f2f,permutationResults$m2f)
text(permutationResults$f2f,permutationResults$m2f,permutationResults$game,cex=0.3)

plot(permutationResults$m2f,permutationResults$m2f.mean)
text(permutationResults$m2f,permutationResults$m2f.mean,permutationResults$game,cex=0.3)
abline(0,1)

plot(permutationResults$f2f.z,permutationResults$m2f.z)
text(permutationResults$f2f.z,permutationResults$m2f.z,permutationResults$game,cex=0.3)

plot(permutationResults$f2m.z,permutationResults$m2m.z)
text(permutationResults$f2m.z,permutationResults$m2m.z,permutationResults$game,cex=0.3)


plot(permutationResults$m2m,permutationResults$m2m.mean)
text(permutationResults$m2m,permutationResults$m2m.mean,permutationResults$game,cex=0.3)
abline(0,1)

#transitionPlot(trueTransitions.AllGames.Raw, 
#               overlap_add_width = 0.3, type_of_arrow = "simple", 
#               min_lwd = unit(2, "mm"), max_lwd = unit(14, "mm"),
#               fill_start_box = brewer.pal(n = 2, name = "Pastel1"))

transitions <- trueTransitions.AllGames.Raw %>%
  getRefClass("Transition")$new(
      label=c("Previous\nSpeaker", "Next\nSpeaker"),
      skip_shadows = TRUE,
      min_lwd = unit(0.1, "mm"), max_lwd = unit(14, "mm"),
      box_label_cex = 2,
      fill_clr = list(c("#f9726d","#31c0c3"),c("#f9726d","#31c0c3")))

pdf("../results/graphs/transitions/Transitions.pdf")
transitions$render()
grid::grid.text(label=paste0(round(100*trueTransitions.AllGames),"%"),
                x=c(0.35,0.35,0.35,0.35),
                y=c(0.6,0.2, 0.4,0.05),
                gp=gpar(fontsize=20, col="grey"))
dev.off()


# For Individual Games
plotTransition = function(transProp, transRaw, outFileName,ys){
  transitions.ff10 <- transRaw %>%
    getRefClass("Transition")$new(
      label=c("Previous\nSpeaker", "Next\nSpeaker"),
      skip_shadows = TRUE,
      min_lwd = unit(0.01, "mm"), max_lwd = unit(14, "mm"),
      box_label_cex = 2,
      fill_clr = list(c("#f9726d","#31c0c3"),c("#f9726d","#31c0c3")))
  
  pdf(outFileName)
  transitions.ff10$render()
  grid::grid.text(label=paste0(round(100*transProp),"%"),
                  x=c(0.35,0.35,0.35,0.35),
                  y=ys,
                  gp=gpar(fontsize=20, col="grey"))
  dev.off()
  
}

makeTransitionGraphForOneGame = function(game,outFileName,ys=c(0.7,0.3, 0.45,0.1)){
  dx = permutationResults[permutationResults$game==game,]
  ff10t = matrix(c(dx$m2m,dx$m2f,dx$f2m,dx$f2f),ncol=2,byrow = T)
  rownames(ff10t) = c("m","f")
  colnames(ff10t) = c("m","f")
  ff10t.raw = matrix(c(dx$m2m.raw,dx$m2f.raw,dx$f2m.raw,dx$f2f.raw),ncol=2,byrow = T)
  rownames(ff10t.raw) = c("m","f")
  colnames(ff10t.raw) = c("m","f")
  
  plotTransition(ff10t,ff10t.raw,outFileName,ys)

  # Expected
  expectedProp = matrix(c(dx[['m2m.mean']], dx[['m2f.mean']],
                          dx[['f2m.mean']], dx[['f2f.mean']]),nrow=2,byrow = T)
  rownames(expectedProp) = c("m","f")
  colnames(expectedProp) = c("m","f")
  
  totalLinesPerGender = rowSums(ff10t.raw)
  expectedRaw = round(expectedProp * totalLinesPerGender)
  outFileName2 = gsub("\\.pdf","_Expected.pdf",outFileName)
  plotTransition(expectedProp,expectedRaw,outFileName2,ys)

}

makeTransitionGraphForOneGame("Final Fantasy X-2", "../results/graphs/transitions/Transitions_FinalFantasyX-2.pdf")

makeTransitionGraphForOneGame("Horizon Zero Dawn", "../results/graphs/transitions/Transitions_HZD.pdf")
makeTransitionGraphForOneGame("King's Quest VI", "../results/graphs/transitions/Transitions_KQ6.pdf")
makeTransitionGraphForOneGame("King's Quest VII: The Princeless Bride", "../results/graphs/transitions/Transitions_KQ7.pdf")
makeTransitionGraphForOneGame("Kingdom Hearts III", "../results/graphs/transitions/Transitions_KH3.pdf")
makeTransitionGraphForOneGame("Final Fantasy V", "../results/graphs/transitions/Transitions_FF5.pdf")
makeTransitionGraphForOneGame("Stardew Valley", "../results/graphs/transitions/Transitions_SDV.pdf")

makeTransitionGraphForOneGame("Final Fantasy XV", "../results/graphs/transitions/Transitions_FF15.pdf",ys=c(0.55,0.12, 0.35,0.02))


# Expected proportions under permutation
#  (all games)

expectedProp = matrix(c(permutedTransitionStats.AllGames['m2m.mean'], permutedTransitionStats.AllGames['m2f.mean'],
permutedTransitionStats.AllGames['f2m.mean'], permutedTransitionStats.AllGames['f2f.mean']),nrow=2,byrow = T)
rownames(expectedProp) = c("m","f")
colnames(expectedProp) = c("m","f")

totalLinesPerGender = rowSums(trueTransitions.AllGames.Raw)
expectedRaw = round(expectedProp * totalLinesPerGender)

expectedTrans <- expectedRaw %>%
  getRefClass("Transition")$new(
    label=c("Previous\nSpeaker", "Next\nSpeaker"),
    skip_shadows = TRUE,
    min_lwd = unit(0.01, "mm"), max_lwd = unit(14, "mm"),
    box_label_cex = 2,
    fill_clr = list(c("#f9726d","#31c0c3"),c("#f9726d","#31c0c3")))

pdf("../results/graphs/transitions/Transitions_ExpectedAllGames.pdf")
expectedTrans$render()
grid::grid.text(label=paste0(round(100*expectedProp),"%"),
                x=c(0.35,0.35,0.35,0.35),
                y=c(0.6,0.2, 0.4,0.05),
                gp=gpar(fontsize=20, col="grey"))
dev.off()

