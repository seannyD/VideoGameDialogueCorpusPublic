setwd("~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project_public/analysis/")

library(quanteda)
library(quanteda.textstats)
library(quanteda.textplots)
library(jsonlite) # Load first so that rjson overrides
library(rjson)

logLikelihood.G2 = function(a,b,c,d){
  c = as.double(c)
  d = as.double(d)
  E1 = c*(a+b) / (c+d)
  E2 = d*(a+b) / (c+d)
  G2PartA = (a*log(a/E1))
  G2PartA[a==0] = 0
  G2PartB = (b*log(b/E2))
  G2PartB[b==0] = 0
  G2 = 2*(G2PartA + G2PartB) 
  return(G2)
}


d = read.csv("../results/tropes/tropeWordFreq.csv",stringsAsFactors = F)

allres = data.frame()
for(i in 1:nrow(d)){
  target = d[i,2:ncol(d)]
  ref = d[-i,2:ncol(d)]
  ref = colSums(ref)
  
  targetTotalFreq = sum(target[1,])
  refTotalFreq = sum(ref)
  
  # If there's no words, don't process
  if(targetTotalFreq>0){
    # Don't bother calculating cases where the target frequency is zero
    ref = ref[target[1,]>0]
    target = target[,target[1,]>0]
    
    # TODO: work out p value?
    llx = logLikelihood.G2(target,ref,targetTotalFreq,refTotalFreq)
    res = data.frame(trope = d$.TROPE[i],
                     word = names(ref),
                     loglikelihood = unlist(llx),
                     #p = llx[2,],
                     totalTropeDialogue = targetTotalFreq)
    res = res[abs(res$loglikelihood)>3,]
    allres = rbind(allres,res)
    
  }
}

allres = allres[order(abs(allres$loglikelihood),decreasing = T),]
write.csv(allres, file="../results/tropes/tropeKeywords.csv",
          row.names = F,fileEncoding = "UTF-8")


