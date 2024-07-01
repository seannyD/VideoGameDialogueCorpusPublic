setwd("~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project_public/analysis/")

library(quanteda)
library(quanteda.textstats)
library(quanteda.textplots)
library(jsonlite) # Load first so that rjson overrides
library(rjson)
source("_CorpusHelperFunctions.R")

# Lemmatisation
#if (!require("pacman")) install.packages("pacman")
#pacman::p_load(textstem, dplyr)
#library(textstem)

#install.koRpus.lang("en")
library(koRpus)

combineFreqMatrices = function(m1,m2){
  all1 = unique(c(rownames(m1),rownames(m2)))
  all2 = unique(c(colnames(m1),colnames(m2)))
  m1 = m1[all1,all2]
  m1[is.na(m1)] = 0
  m2 = m2[all1,all2]
  m2[is.na(m2)] = 0
  return(m1+m2)
}

stats = read.csv("../results/generalStats.csv",stringsAsFactors = F)
# Remove alternative measures
stats = stats[stats$alternativeMeasure!="True",]
stats = stats[!is.na(stats$words),]
d = NULL
freqMatrix = matrix()
folders = unique(stats$folder)
for(folder in folders){
  tropeFile = paste0(folder,"tropeData.csv")
  if(file.exists(tropeFile)){
    dx = read.csv(tropeFile,stringsAsFactors = F,encoding = "UTF-8",fileEncoding = "UTF-8")
    meta = fromJSON(file=paste0(folder,"meta.json"))
    gender = data.frame()
    for(g in names(meta$characterGroups)){
      gender = rbind(gender,
        data.frame(
          name = unlist(meta$characterGroups[g]),
          group = g))
    }
    dx$group = gender[match(dx$VGDCName,gender$name),]$group
    d = rbind(d,dx)
    
    # Add dialogue
    dialogue = loadJSONScripts(folder)
    dialogue = dialogue[dialogue$Group_male | dialogue$Group_female,]
    dialogue = dialogue[dialogue$character %in% unique(dx$VGDCName),]
    
    # group dialogue by character
    dialogue = data.frame(
      folder = folder,
      game = meta$game,
      character = tapply(dialogue$character,dialogue$character,head,n=1),
      dialogue = tapply(dialogue$dialogue, dialogue$character, paste, collapse=".\n"))
    
    # group character dialogue by trope (a character's dialogue possibly 
    #  belongs to more than one trope)
    tropeDialogue = tapply(dx$VGDCName,dx$tropeName,
          function(charNames){
            paste(dialogue[dialogue$character %in% charNames,]$dialogue,
                  collapse=".\n")
          })
    tropeDialogue = tropeDialogue[nchar(tropeDialogue)>0]
    
    # TODO: currently, lemmas is calculated per game, 
    #  but the frequency matrix is calculated outside this loop.
    #  So need to combine frequency tables 
    # (also: grouping by trope first means we're repeating some
    #  lemmatisation on the same text several times)
    lemmas = list()
    for(i in 1:length(tropeDialogue)){
      cat(tropeDialogue[i],file="tmp.txt")
      tagged.text = treetag("tmp.txt",
                            treetagger="manual",
                            lang="en",
                            TT.options=list(
                              path="/Users/seanroberts/Documents/TreeTagger",
                              preset="en"
                            ))
      lx = tagged.text@tokens$lemma
      useToken = lx=="<unknown>" | grepl("^@",lx)
      lx[useToken] = tagged.text@tokens$token[useToken]
      lx = tolower(lx)
      lx = gsub("\\.","",lx)
      lx = table(lx)
      lx = lx[!names(lx) %in% c(".",",",";","?","","'","!")]
      lx = lx[!grepl("[0-9]",names(lx))]
      lemmas[[i]] = lx
      names(lemmas[[i]]) = names(tropeDialogue)[i]
    }
    allWords = unique(unlist(sapply(lemmas,names)))
    fm = sapply(lemmas,function(X){
      X[allWords]
    })
    fm = fm[!is.na(rownames(fm)),]
    fm[is.na(fm)]=0
    freqMatrix = combineFreqMatrices(freqMatrix,fm)
  }
}



#######
head(sort(table(d$tropeName),decreasing = T),n=30)

head(sort(table(d[d$group=="male",]$tropeName),decreasing = T),n=30)
head(sort(table(d[d$group=="female",]$tropeName),decreasing = T),n=30)

# See 'oh crap'
gx = table(d$tropeName,d$group)
gx = data.frame(trope = rownames(gx),
                male = gx[,"male"],
                female = gx[,"female"],row.names = NULL)
gx = gx[rowSums(gx[,c("male","female")])>=10,]
gx$p = NA
for(i in 1:nrow(gx)){
  # Chi square test of trope present/absent vs male/female
  m = rbind(gx[i,c("male","female")], colSums(gx[-i,c("male","female")]))
  chi = chisq.test(m)
  gx$p[i]=chi$p.value
}
gx$p.adjust = p.adjust(gx$p,n=sum(!is.na(gx$p.adjust)))

gx = gx[order(gx$p),]

head(gx,30)


###
