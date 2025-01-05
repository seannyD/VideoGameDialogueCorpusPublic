try(setwd("~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project_public/analysis/violence/"))

library(dplyr)
source("../_CorpusHelperFunctions.R")

# Note the norms for male and female participants is also listed.
norms = read.csv("../../../violence/BRM-emot-submit.csv",stringsAsFactors = F)

baseFolder = "../../data/ALL/byCharGroup/"
files = list.files(baseFolder,"*.csv")

d = data.frame()
for(file in files){
  dx = read.csv(paste0(baseFolder,file),stringsAsFactors = F)
  d = rbind(d,dx)
}


heal = d[d$word %in% c("heal","healed","healing","heals","healer"),]
heal = tapply(heal$freq,heal$group,sum)
healM = heal["male"]
totalM = sum(d[d$group=="male",]$freq)
healF = heal["female"]
totalF = sum(d[d$group=="female",]$freq)

healMPer1000 = 1000 * (healM/totalM)
healFPer1000 = 1000 * (healF/totalF)
(healFPer1000-healMPer1000)/healMPer1000
logLikelihood.test(healF,healM,totalF,totalM)

# TODO: total words is wrong here - way too high?
d = d[d$group %in% c("male","female"),]
totalWords = tapply(d$freq,d$group,sum)

d2 = d %>% group_by(word,group) %>% summarise(
  freq = sum(freq)
)

# per million
d2$relFreq = 1000000*(d2$freq/totalWords["male"])
d2$relFreq[d2$group=="female"] = 1000000*(d2$freq[d2$group=="female"]/totalWords["female"])

d2$valence = norms[match(d2$word,norms$Word),]$V.Mean.Sum
d2$dominance = norms[match(d2$word,norms$Word),]$D.Mean.Sum

d2 = d2[!is.na(d2$valence),]
# Multiply by frequency to get mean score for dialogue?
d3 = d2 %>% group_by(group) %>% summarise(
  valence.score = sum(freq*valence)/sum(freq),
  dominance.score = sum(freq*dominance)/sum(freq)
)

plot(log10(d2$freq),
     d2$dominance,
     col=c(male="red",female="green"))


###
# Use norm data to find words that are percieved as more violent
#  by women than by men.
# (Dominance: low value is bad word
violenceVocabulary = norms[norms$V.Mean.Sum < quantile(norms$V.Mean.Sum,0.1) & 
                             norms$A.Mean.Sum > quantile(norms$A.Mean.Sum,0.9) & 
                             norms$D.Mean.Sum < quantile(norms$D.Mean.Sum,0.1),]$Word
write.csv(violenceVocabulary,"../../../violence/violentWords.csv")

dv = d[d$word %in% violenceVocabulary,]
violenceWordsByGender = tapply(dv$freq,dv$group,sum)

# Freq per thousand words
perThousandWords = round(1000*(violenceWordsByGender/totalWords),3)
perThousandWords
diff(perThousandWords)/perThousandWords[2]

res = logLikelihood.test(violenceWordsByGender[1],
                   violenceWordsByGender[2],
                   totalWords[1],
                   totalWords[2])

# Difference in valence between genders
norms$V.GDiff = norms$V.Mean.M - norms$V.Mean.F # pos = women find less valent
norms$A.GDiff = norms$A.Mean.M - norms$A.Mean.F # neg = women find more arousing
norms$D.GDiff = norms$D.Mean.M - norms$D.Mean.F # pos = women find worse dominant
wordsWomenFindWorseThanMen = norms[
  norms$V.GDiff > quantile(norms$V.GDiff,0.95),]

wordsWomenFindWorseThanMen$violent = wordsWomenFindWorseThanMen$Word %in% violenceVocabulary

wordsWomenFindWorseThanMen$Word

wordsWomenFindWorseThanMen[, c("Word", "V.Mean.M", "V.Mean.F","V.GDiff","A.GDiff")]

write.csv(wordsWomenFindWorseThanMen,"../../../violence/wordsWomenFindWorseThanMen.csv")

# Load edited words to filter out non-violent words
violentGenderedWords = read.csv("../../../violence/wordsWomenFindWorseThanMen_edited.csv",stringsAsFactors = F)
violentGenderedWords = violentGenderedWords[!is.na(violentGenderedWords$violentWord),]
violentGenderedWords = violentGenderedWords[violentGenderedWords$violentWord==1,]

V.GDiff.Vocabulary = norms[norms$V.GDiff > quantile(norms$V.GDiff,0.95),]$Word
dvdiff = d[d$word %in% V.GDiff.Vocabulary,]
dvdiffWordsByGender = tapply(dvdiff$freq,dvdiff$group,sum)

dVG = d[d$word %in% violentGenderedWords$Word,]
dVGFreq = tapply(dVG$freq,dVG$word,sum)
violentGenderedWords$freq = dVGFreq[violentGenderedWords$Word]
violentGenderedWords$freqPerThousandWords = 1000*(violentGenderedWords$freq/sum(totalWords))

# Freq per thousand words
perThousandWords = round(1000*(dvdiffWordsByGender/totalWords),3)
perThousandWords
diff(perThousandWords)/perThousandWords[2]

res = logLikelihood.test(dvdiffWordsByGender[1],
                         dvdiffWordsByGender[2],
                         totalWords[1],
                         totalWords[2])

###############
# Collocations
library(quanteda)
library(quanteda.textstats)
d = loadJSONScripts("../../data/")
d$binaryGender = NA
d$binaryGender[d$Group_female] = "F"
d$binaryGender[d$Group_male] = "M"

d = d[!d$character %in% c("ACTION","GOTO","STATUS","LOCATION","CHOICE"),]

corp = corpus(d, text_field = "dialogue")
toks = tokens(corp, remove_punct = TRUE)
toks = tokens_tolower(toks)

colloc_wife = collocation_mutual_information(toks,target_word = "wife")
head(colloc_wife,n=30)

colloc_husband = collocation_mutual_information(toks[d$Group_male],target_word = "husband")
head(colloc_husband,n=30)

tx = table(d$binaryGender,grepl("son of a bitch",tolower(d$dialogue)))
prop.table(tx,1)*1000

tx = table(d$binaryGender,grepl("was killed",tolower(d$dialogue)))
prop.table(tx,1)*1000
