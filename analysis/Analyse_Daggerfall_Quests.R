# Load the rjson library
library("rjson")

try(setwd("~/Documents/Cardiff/VideoGameScripts/project/analysis/"))

########################
# Load data            #
########################

# Load data
d = fromJSON(file="../data/ElderScrolls/Daggerfall/data.json")
m = fromJSON(file="../data/ElderScrolls/Daggerfall/meta.json")
# Name, gender, offer, accept, refuse
quests = data.frame(name=NA,gender=NA,offer=NA,accept=NA,refuse=NA,stringsAsFactors = F)

# Find quests
x = c()
getNext = FALSE
offer = ""
for(lx in d[["text"]]){
  if("_Type" %in% names(lx)){
    getNext = TRUE
    offer = lx[[1]]
  }
  else{
    if(getNext){
        getNext = FALSE
        choice = lx[["CHOICE"]]
        accept = ""
        if(length(choice[[1]])>1){
          charNameX = names(lx[[1]][[1]][[2]][1])
          if(nchar(charNameX)>0){
            charName = charNameX
          }
          accept = choice[[1]][[2]][[1]]
        }
        refuse = ""
        if(length(choice[[1]])>1){
          charNameX = names(lx[[1]][[1]][[2]][1])
          if(nchar(charNameX)>0){
            charName = charNameX
          }
          refuse = choice[[2]][[2]][[1]]
        }
        gender = "random"
        if(charName %in% m$characterGroups$female){
          gender = "female"
        }
        if(charName %in% m$characterGroups$male){
          gender = "male"
        }
        
        quests= rbind(quests, data.frame(name=charName, gender=gender, offer=offer,accept=accept, refuse=refuse))
    }
  }
}


