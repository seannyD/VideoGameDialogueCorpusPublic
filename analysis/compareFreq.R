library(quanteda)
library(quanteda.textstats)
library(stringr)
setwd("~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project/analysis/")


logLikelihood.G2 = function(a,b,c,d){
  c = as.double(c)
  d = as.double(d)
  E1 = c*(a+b) / (c+d)
  E2 = d*(a+b) / (c+d)
  G2 = 2*((a*log(a/E1)) + (b*log(b/E2))) 
  return(G2)
}

logLikelihood.test = function(freqInCorpus1, freqInCorpus2, sizeOfCorpus1, sizeOfCorpus2){
  # A single test is done like this:
  # logLikelihood.test(2554, 3468, 110000, 140000)
  G2 = logLikelihood.G2(freqInCorpus1,freqInCorpus2,sizeOfCorpus1,sizeOfCorpus2)
  p.value = pchisq(G2, df=2, lower.tail=FALSE)
  #print(paste("Log Likelihood =",G2, ", p = ",p.value))
  return(data.frame(G2 = G2, p = p.value))
}

textM = readLines("../data/ALL/male.txt")
dM = data.frame(
  text = textM,
  group="male",stringsAsFactors = F
)
corpM = corpus(dM)
tokensM = tokens(corpM, remove_punct = TRUE)
maleTotal = sum(ntoken(tokensM))

textF = readLines("../data/ALL/female.txt")
dF = data.frame(
  text = textF,
  group="female",stringsAsFactors = F
)
corpF = corpus(dF)
tokensF = tokens(corpF, remove_punct = TRUE)
femaleTotal = sum(ntoken(tokensF))

d = rbind(dM,dF)
corpAll = corpus(d)
tokensAll = tokens(corpAll, remove_punct = TRUE)


# Keyness
dfmat <- dfm(tokensAll)
k = textstat_keyness(dfmat,target = dfmat$group=="male", measure = "lr",sort = F)
k$maleFreqPerMillion = (k$n_target/maleTotal) * 1000000
k$femaleFreqPerMillion = (k$n_reference/femaleTotal) * 1000000

top = k[order(k$G2,decreasing = T),][1:30,]
bottom = k[order(k$G2,decreasing = F),][1:30,]


write.csv(rbind(top,bottom),"../results/keyness.csv")


# words = c("i","me","my","you","who","what","why","where","when")
# 
# corp = corpus(d)
# toks <- tokens(corp, remove_punct = TRUE)   
# dfmat <- dfm(toks)
# dfmat <- dfm_select(dfmat,pattern=words)
# k = textstat_keyness(dfmat,target = dfmat$group=="male", measure = "lr",sort = F)
# k$maleFreqPerMillion = (k$n_target/maleTotal) * 1000000
# k$femaleFreqPerMillion = (k$n_reference/femaleTotal) * 1000000
# 
# write.csv(k,"../results/keyness_tx.csv")


# Politeness

pol = read.csv("../results/politeness.csv",stringsAsFactors = F)

politeness = NULL

for(feature in unique(pol$feature)){
  nF = pol[pol$group=="female" & pol$feature==feature,]$count
  nM = pol[pol$group=="male" & pol$feature==feature,]$count
  propF = 1000000 * (nF/femaleTotal)
  propM = 1000000 * (nM/maleTotal)
  ll = logLikelihood.test(nM,nF,maleTotal, femaleTotal)
  politeness = rbind(politeness, data.frame(
    feature=feature, nFemale = nF,nMale = nM,
    nFemalePerMillionWords = propF,
    nMalePerMillionWords = propM,
    G2 = ll[1],
    p = ll[2]
  ))
}


# Hedging

hedges = c(
  "Actually",
  "Generally",
  "Likely",
  "Only",
  "Really",
  "Surely",
  "Apparently",
  "Guess",
  "Maybe",
  "Partially",
  "Relatively",
  "Thing",
  "Arguably",
  "Necessarily",
  "Possibility",
  "Possibly",
  "Roughly",
  "Typically",
  "Broadly",
  "Just",
  "Normally",
  "Probably",
  "Seemingly",
  "Usually",
  "Frequently",
  "Quite"
)

dfmat <- dfm(tokensAll)
dfmat <- dfm_select(dfmat,pattern=hedges)
freq.hedges = textstat_keyness(dfmat,target = dfmat$group=="male", measure = "lr",sort = F, correction = "none")
ll = logLikelihood.test(freq.hedges$n_target,freq.hedges$n_reference,maleTotal,femaleTotal)
freq.hedges$G2 = ll$G2
freq.hedges$p = ll$p
freq.hedges$maleFreqPerMillion = (freq.hedges$n_target/maleTotal) * 1000000
freq.hedges$femaleFreqPerMillion = (freq.hedges$n_reference/femaleTotal) * 1000000

hedgePhrases = c(
  "I think",
  "Kind of",
  "Of course",
  "Sort of",
  "You know")

getPhraseFrequency = function(w,group){
  corp = corpus(d[d$group==group,])
  # We don't want punctuation between phrase parts
  toks = tokens(corp, remove_punct = FALSE)
  k = kwic(toks, pattern = phrase(c(w)))
  length(k$post)
}

for(w in hedgePhrases){
  freqF = getPhraseFrequency(w,"female")
  freqM = getPhraseFrequency(w,"male")
  ll = logLikelihood.test(freqM, freqF, maleTotal, femaleTotal)
  freq.hedges = rbind(freq.hedges, data.frame(
    feature = w,
    G2 = ll[1],
    p = ll[2],
    n_target = freqM,
    n_reference = freqF,
    maleFreqPerMillion = (freqM/maleTotal) * 1000000,
    femaleFreqPerMillion = (freqF/femaleTotal) * 1000000
  ))
}

freq.hedges$sig = freq.hedges$p<0.05
freq.hedges[freq.hedges$sig,]

names(freq.hedges)[names(freq.hedges)=="n_target"] = "freqMale"
names(freq.hedges)[names(freq.hedges)=="n_reference"] = "freqFemale"

sum(freq.hedges$freqMale)/maleTotal * 1000000
sum(freq.hedges$freqFemale)/femaleTotal * 1000000

logLikelihood.test(sum(freq.hedges$freqMale),
                   sum(freq.hedges$freqFemale),
                   maleTotal,femaleTotal)


# Swearing

swears = read.csv("https://gist.githubusercontent.com/tjrobinson/2366772/raw/97329ead3d5ab06160c3c7ac1d3bcefa4f66b164/profanity.csv",
                  stringsAsFactors = F,header = F)
swears = swears[,1]
swears = swears[!swears %in% c("snatch")]
nx = c("hell","dago","ass")
swears[!swears %in% nx]= paste0(swears[!swears %in% nx],"*")

# Specific to games in the corpus
swears = c(swears,"vermin","scum")

# Bedarek
bednarekSwears = c("god",
  "hell",  "damn", "crap", "screw",
  "fuck", "fucktard", "fuckwad", "fucks", "fucking", "butt-fuck", 
  "butt-fucking", "fuck-up", "fuckable", "fucked", "pencil-fucked", 
  "fucked-up", "ass-fucked", "fucker", 
  "motherfucker", "motherfuckers", "motherfucking",
  "bullshit", "dipshit", "shit", "shit-faced", "shit-ass", 
  "shitheads", "shits", "shittiest", "shitting", "shitty",
  "damned", "fricking","freaking","frigging", "gosh", "heck", "jeez", "shucks")

swears = c(swears,bednarekSwears)
swears = dictionary(list(swears=swears))

dfmat_swears = dfm(tokensAll)
dfmat_swears = dfm_select(dfmat_swears, pattern=swears)
dfmat_swears <- dfm(toks_swears)
tstat_freq_swears <- textstat_frequency(dfmat_swears, groups = d$group)


swearFreq = tapply(tstat_freq_swears$frequency,tstat_freq_swears$group,sum)
swearFreqPerMillion = (swearFreq / c(femaleTotal,maleTotal)) * 1000000

logLikelihood.test(swearFreq["male"],
                   swearFreq["female"],
                   maleTotal,femaleTotal)




