# Functions to load corpus data

library(rjson)

walkJSON = function(obj,minorKeys){
  noAttr = is.null(attributes(obj))
  isChoice = "CHOICE" %in% names(obj)
  if(noAttr | isChoice){
    ox = sapply(obj,walkJSON,minorKeys=minorKeys,simplify = F)
    #print("---")
    #print(ox)
    ox = do.call("rbind",ox)
    return(ox)
  } else{
    #print(obj)
    nx = names(obj)
    nx = nx[!grepl("^_",nx)]
    charName = nx[1]
    dlg = as.vector(unlist(obj[charName]))
    dx = data.frame(
      character = c(charName,NA),
      dialogue = c(dlg,NA))
    dx[,minorKeys] = obj[minorKeys]
    dx[,minorKeys[!minorKeys %in% names(dx)]] = NA
    return(dx)
  }
}

loadJSONScripts = function(searchPath = "../data/"){
  gameFolders = list.dirs(path = searchPath, full.names = TRUE, recursive = TRUE)
  
  allData = data.frame(character = NA, dialogue = NA)
  for(folder in gameFolders){
    if("data.json" %in% list.files(folder)){
      # Read the meta data
      meta = fromJSON(file=file.path(folder,"meta.json"))
      # work out if the data is part of the main corpus
      gameIsPartOfTheMainCorpus = TRUE
      if("alternativeMeasure" %in% attributes(meta)$names){
        gameIsPartOfTheMainCorpus = !meta$alternativeMeasure
      }
      if(gameIsPartOfTheMainCorpus){
        print(paste("Loading",folder,"..."))
        # Yes, so add it to our big data frame  
        txt = fromJSON(file=file.path(folder,"data.json"))["text"]
        # Get list of minor keys
        nx = names(unlist(txt))
        nx = gsub("CHOICE\\.","",nx)
        nx = gsub("text\\.","",nx)
        minorKeys = unique(nx[grepl("^_",nx)])
        # Load the data by recursively walking the structure
        dialogueData = walkJSON(txt[[1]],minorKeys)
        dialogueData = dialogueData[!is.na(dialogueData$character),]
        dialogueData$folder = folder
        dialogueData$game = meta$game
        dialogueData$series = meta$series
        dialogueData$year = meta$year
        # characters can belong to multiple groups, 
        #  so have columns for each group
        #  showing if they are members or not
        charGroupData = as.data.frame(sapply(
          names(meta$characterGroups),function(X){
              dialogueData$character %in% meta$characterGroups[[X]]}))
        names(charGroupData) = paste0("Group_",names(charGroupData))
        dialogueData = cbind(dialogueData, charGroupData)
        # Add group data: Check columns exist, then rbind
        inAllDataButNotDD = setdiff(names(allData),names(dialogueData))
        inDDButNotAllData = setdiff(names(dialogueData),names(allData))
        allData[,inDDButNotAllData] = NA
        dialogueData[,inAllDataButNotDD] = NA
        dialogueData = dialogueData[,names(allData)]
        allData = rbind(allData,dialogueData)
      }
    }
  }
  # Take out dummy NA
  allData = allData[2:nrow(allData),]
  return(allData)
}

