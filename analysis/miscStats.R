setwd("~/Documents/Cardiff/VideoGameScripts/project/analysis/")
library(readr)
library(stringr)


# R function for calculating LL, by Andrew Hardie, Lancaster University.
# (with apologies for the inevitable R-n00b blunders)
# http://corpora.lancs.ac.uk/sigtest/process.php?action=seeR
loglikelihood.test = function(O)
{
  DNAME <- deparse(substitute(O))
  
  E = suppressWarnings(chisq.test(O)$expected)
  
  sum = 0;
  
  for(i in 1:length(O[,1]))
  {
    for(j in 1:length(O[1,]))
    {
      if (O[i,j] == 0 || E[i,j] == 0)
        next
      sum = sum + (O[i,j] * log(O[i,j]/E[i,j]))
    }
  }
  STAT = sum * 2;
  
  DF = (length(O[1,]) - 1) * (length(O[,1]) - 1)
  
  P = 1 - pchisq(STAT, df=DF)
  
  names(DF) = "df"
  names(STAT) = "Log-likelihood"
  
  obj =  list(statistic=STAT, parameter=DF, p.value=P, method="Log-Likelihood test", 
              data.name=DNAME, observed=O, expected=E)
  
  attr(obj, "class") <- "htest"
  
  return (obj)
}



femaleDialogue <- read_file("../data/ALL/female.txt")
maleDialogue <- read_file("../data/ALL/male.txt")

d = read.csv("../results/generalStats.csv",stringsAsFactors = F)
d = d[d$alternativeMeasure!="True",]
d = d[d$group %in% c("male","female"),]

totalMaleWords = sum(d[d$group=="male",]$words,na.rm=T)
totalFemaleWords = sum(d[d$group=="female",]$words,na.rm=T)

doKeyness = function(word){
  fMale = str_count(maleDialogue, word)
  fFemale = str_count(femaleDialogue, word)
  mat = matrix(c(fMale,fFemale, totalMaleWords, totalFemaleWords), nrow=2,byrow = T)
  print(mat)
  loglikelihood.test(mat)
}

doKeyness("[Hh]elp( me)?\\!")
