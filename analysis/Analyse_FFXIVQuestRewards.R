library(sjPlot)
try(setwd("~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project/analysis/"))
d = read.csv("../data/FinalFantasy/FFXIV/XPByQuest.csv",stringsAsFactors = F)

d$propFemale = d$femaleWords / (d$maleWords+d$femaleWords)

cor.test(d$propFemale,1+d$XP)
cor.test(d$propFemale,1+d$Gil)

d$XPCat = cut(d$XP, c(-Inf,20000,40000,60000,150000,Inf))
boxplot(d$propFemale~d$XPCat)

d$propFemaleCat = cut(d$propFemale,seq(from=0,to=1,length.out=5),include.lowest = T)
boxplot(d$Gil~d$propFemaleCat)


d2 = d[d$propFemale %in% c(0,1),]
boxplot(d2$XP~ d2$propFemale)
t.test(d2$XP~ d2$propFemale)

boxplot(d2$Gil~ d2$propFemale)
t.test(d2$Gil~ d2$propFemale)


charProp = read.csv("../data/FinalFantasy/FFXIV/charProperties.csv",stringsAsFactors = F)
s = read.csv("../data/FinalFantasy/FFXIV/stats_by_character.csv",stringsAsFactors = F)

s$bodyType = charProp[match(s$charName,charProp$Name),]$Body.Type

s$bust = charProp[match(s$charName,charProp$Name),]$Bust.Size
s$bust[s$bust==""] = NA
s$bust = factor(s$bust,levels=c("0%","25%","50%","75%","100%"),ordered = T)
boxplot(log(s$words)~s$bust)

m0Bust = lm(log10(words+1)~bust,data=s[!is.na(s$bodyType) & s$bodyType!="Child",])

plot_model(m0Bust, "pred")

s$muscle = charProp[match(s$charName,charProp$Name),]$"Muscle.Tone"
s$muscle[s$muscle==""] = NA
s$muscle = factor(s$muscle,levels=c("0%","25%","50%","75%","100%"),ordered = T)
boxplot(log(s$words)~s$muscle)
m0Muscle = lm(log10(words+1)~muscle,data=s[!is.na(s$bodyType) & s$bodyType!="Child",])


plot_model(m0Muscle,"pred")
