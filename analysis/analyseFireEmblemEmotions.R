try(setwd("~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project_public/analysis/"))

d = read.csv("../data/FireEmblem/FireEmblemThreeHouses/characterEmotions.csv",stringsAsFactors = F)

femaleFreq = 
  tapply(d[d$gender=="female",]$frequency,
       d[d$gender=="female",]$emotion,sum)

maleFreq = 
  tapply(d[d$gender=="male",]$frequency,
         d[d$gender=="male",]$emotion,sum)

emotions = c("angry","happy","neutral","sad","shock","shy")

emotionFreq = cbind("female" = femaleFreq[emotions],
                    "male" = maleFreq[emotions])

emotionFreq
emotionFreqProp = round(prop.table(emotionFreq,2)*100,2)
emotionFreqProp = cbind(emotionFreqProp,
                        emotionFreqProp[,1]/emotionFreqProp[,2])
emotionFreqProp

chisq.test(emotionFreq)

# Not just effect of shyness:
chisq.test(emotionFreq[1:5,])
