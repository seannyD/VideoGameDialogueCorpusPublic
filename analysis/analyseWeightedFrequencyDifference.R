library(ggplot2)
library(sjPlot)
library(party)

setwd("~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project_public/analysis/")

d = read.csv("../results/doNotShare/WeightedFreq.csv",stringsAsFactors = F)

d = d[d$freq>30,]

cor.test(d$freq,d$freqWeighted)

d$freqLog = log10(1+d$freq)
d$freqWeightedLog = log10(1+d$freqWeighted)

# Difference: smaller numbers = lower difference
d$diff = d$freq - d$freqWeighted
d$diffLog = d$freqLog - d$freqWeightedLog

d$diffProp = d$freqWeighted/d$freq
d$diffLogProp = d$freqWeightedLog/d$freqLog



# Note the norms for male and female participants is also listed.
norms = read.csv("../../violence/BRM-emot-submit.csv",stringsAsFactors = F)

d$Valence = norms[match(d$word,norms$Word),]$V.Mean.Sum
d$Arousal = norms[match(d$word,norms$Word),]$A.Mean.Sum
d$Dominance = norms[match(d$word,norms$Word),]$D.Mean.Sum

mAll = lm(diffProp~Valence + Arousal + Dominance, data = d)
summary(mAll)

#cx = cforest(diffProp~Valence + Arousal + Dominance, data = d)
#varimp(cx)


cor.test(d$diffProp,d$Valence)


boxplot(d$Valence~cut(d$diffProp,5))
boxplot(d$diffProp~cut(d$Valence,breaks = 1:9),)

ggplot(d[!is.na(d$Valence),], aes(x=cut(Valence,breaks = 1:9),y=diffProp)) +
  geom_boxplot(outliers = F)

m0 = lm(diffProp~1, data = d[!is.na(d$Valence),])
m1 = lm(diffProp~Valence , data = d)
m2 = lm(diffProp~Valence + I(Valence^2), data = d)
m3 = lm(diffProp~Valence + I(Valence^2) + I(Valence^3), data = d)

anova(m0,m1,m2,m3)
anova(m0,m3)

# Player choice adjusted frequency (PCAF)
# The average PCAF was 45%, sd = 21%. 


summary(m3)
pm = plot_model(m3,"pred",terms="Valence [all]")
pm+ geom_point(aes(x=Valence,y=diffProp),data = d,alpha=0.1) +
  pm$layers[[1]] + pm$layers[[2]] +
  coord_cartesian(ylim=c(0.25,0.75))

# Use a binomial model
mX = glm(diffProp ~ Valence+ I(Valence^2) + I(Valence^3) , data = d, family = binomial,weights = d$freq)
summary(mX)
px = plot_model(mX,"pred",terms="Valence [all]")
px + geom_point(aes(x=Valence,y=diffProp),data = d,alpha=0.1) +
  px$layers[[1]] + px$layers[[2]] +
  coord_cartesian(ylim=c(0.25,0.75))


library(mgcv)

gamAll = gam(diffLog~
             s(Valence,k = 4) +
             s(Arousal,k = 4) +
             s(Dominance,k=4),data = d)
summary(gamAll)

# High valence words are more likely to have a lower difference
#  i.e. less dependent on player choices
gam0 = gam(diffProp~s(Valence,k = 4),data = d,family = binomial)
summary(gam0)
plot.gam(gam0)
pGam = plot_model(gam0,"pred")

pGam + geom_point(aes(x=Valence,y=diffProp),data = d,alpha=0.1) +
  pGam$layers[[1]] + pGam$layers[[2]] +
  coord_cartesian(ylim=c(0.25,0.75)) +
  ylab("Weighted Frequency Difference")


d[!is.na(d$Valence) & d$Valence==min(d$Valence,na.rm = T),]

dx = d[!is.na(d$Valence),]
head(dx[order(dx$Valence),c("word","freq","freqWeighted","diffProp")],20)
head(dx[order(dx$Valence,decreasing = T),c("word","freq","freqWeighted","diffProp")],20)



head(dx[order(dx$diffProp),c("word","freq","freqWeighted","diffProp")],20)
head(dx[order(dx$diffProp,decreasing = T),c("word","freq","freqWeighted","diffProp")],20)

head(dx[dx$diffProp>0.95,])

cor.test(d$diffLog, d$Valence)
