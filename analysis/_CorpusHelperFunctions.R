# Functions to load corpus data

library(rjson)

walkJSON = function(obj,minorKeys){
  # Recursively walk the json structure.
  #  (but this causes memory problems for games with a lot of branches)
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

loadJSONScripts = function(searchPath = "../data/", onlyLoadMainCorpusSources=TRUE, minorKeysToKeep="all"){
  # onlyLoadMainCorpusSources - load only sources in the main corpus
  #   (where 'alternativeMeasure' is not 'TRUE')
  #
  # minorKeysToKeep - by default, the function will load all minor keys
  #  if they aren't all needed, you can specify a vector names of minor keys to keep
  #   e.g. loadJSONScripts("../data/", minorKeysToKeep=c("_ID"))
  #   or keep none: loadJSONScripts("../data/", minorKeysToKeep=c())
  
  gameFolders = list.dirs(path = searchPath, full.names = TRUE, recursive = TRUE)
  gameFolders = gameFolders[!grepl("/raw",gameFolders)]
  
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
      if(gameIsPartOfTheMainCorpus | (!onlyLoadMainCorpusSources)){
        print(paste("Loading",folder,"..."))
        # Yes, so add it to our big data frame  
        txt = fromJSON(file=file.path(folder,"data.json"))["text"]
        # We used to use a recursive walk
        # but this breaks for some games with a lot of branches.
        #dialogueData = walkJSON(txt[[1]],minorKeys)
        
        # So instead, unlist the keys and values
        x = unlist(txt[[1]])
        # We take advantage of serial unlisting and the fact
        # that all minor keys startwith "_"
        dx = data.frame(key = names(x), val = x)
        dx$key = gsub("CHOICE\\.","",dx$key)
        # Find a complete list of minor keys
        minorKeys = minorKeysToKeep
        if(!is.null(minorKeys)){
          if(minorKeys=="all"){
            minorKeys = unique(dx$key)
            minorKeys = minorKeys[grepl("^_",minorKeys)]
          }
        }
        # ID increases each time we find a main key
        dx$id = cumsum(!grepl("^_",dx$key))
        # Group lines by the ID numbers
        dx2 = tapply(1:nrow(dx),dx$id,function(i){
          lx = dx[i,]
          line = data.frame("character" = lx$key[1], "dialogue"= lx$val[1])
          if(!is.null(minorKeys) & length(minorKeys)>0){
            line[1,minorKeys] = lx[match(minorKeys,lx$key ),]$val
          }
          return(line[1,])
        })
        dialogueData = do.call(rbind,dx2)
        
        
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
  # rename minor keys so that referencing is easier
  mkNames = grepl("^_",names(allData))
  names(allData)[mkNames] = paste0("k",names(allData)[mkNames])
  return(allData)
}


logLikelihood.G2 = function(a,b,c,d){
  c = as.double(c)
  d = as.double(d)
  E1 = c*(a+b) / (c+d)
  E2 = d*(a+b) / (c+d)
  G2PartA = (a*log(a/E1))
  if(a==0){
    G2PartA = 0
  }
  G2PartB = (b*log(b/E2))
  if(b==0){
    G2PartB = 0
  }
  G2 = 2*(G2PartA + G2PartB) 
  return(G2)
}

logLikelihood.test = 
  function(freqInCorpus1, freqInCorpus2,
           sizeOfCorpus1, sizeOfCorpus2,
           silent=F){
    G2 = logLikelihood.G2(freqInCorpus1,
                          freqInCorpus2,
                          sizeOfCorpus1,
                          sizeOfCorpus2)
    c1Rel = freqInCorpus1/sizeOfCorpus1
    c2Rel = freqInCorpus2/sizeOfCorpus2
    p.value = pchisq(G2, df=1, lower.tail=FALSE)
    if(c2Rel>c1Rel){G2=-G2}
    pres = paste("= ",round(p.value,3))
    if(p.value<0.0001){pres = "< 0.001"}
    if(!silent){
      print(paste("Log Likelihood =",
                  round(G2,2), ", p ", pres))
    }
    return(c(G2, p.value))
  }

collocation_mutual_information = function(myTokens, target_word, window=c(4,4),minFreq=4){
  # Keep only words that appear in a 'window' around 
  # the target (e.g. within 3 words before or 3 words after).
  toks_target <- tokens_keep(myTokens, pattern = target_word, window = window)
  # Get the frequency of each word in the windowed data
  tx = table(unlist(toks_target))
  colloc = data.frame(
    feature = names(tx),
    frequency = as.vector(tx))
  
  # Work out frequency of all words in whole subcorpus
  # (not just appearing next to target)
  totalFreq = table(unlist(myTokens))
  # Match to colloc 
  colloc$freqInWholeCorpus = totalFreq[colloc$feature]
  # Frequency of the target word
  targetFrequency = totalFreq[target_word]
  if(is.na(targetFrequency)){
    print("Warning: Target word does not appear")
  }
  # Total size of corpus
  numTokensTotal = sum(totalFreq)
  # Work out pointwise mutual information
  colloc$mutualInformation = log((colloc$frequency/numTokensTotal) /
                                   ((colloc$freqInWholeCorpus/numTokensTotal) * (targetFrequency/numTokensTotal)))
  # print results, ordered by mutual information
  colloc = colloc[order(colloc$mutualInformation,decreasing = T),]
  #colloc = colloc[,!names(colloc) %in% c("rank",'group','docfreq')]
  colloc = colloc[colloc$frequency>=minFreq,]
  colloc = colloc[colloc$feature!=target_word,]
  return(colloc)
}
