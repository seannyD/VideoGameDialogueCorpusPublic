out = ""

d = NULL
numEdits = 0
folders = list.dirs("../data", recursive = T)
folders = folders[sapply(folders,function(X){
  "stats_by_character.csv" %in% list.files(X)
})]

numEdits = 0
for(folder in folders){
  js = fromJSON(file = paste0(folder,"/meta.json"))
  alternativeMeasure = FALSE
  if(!is.null(js$alternativeMeasure)){
    alternativeMeasure = js$alternativeMeasure
  }
  if(!alternativeMeasure){
    numEdits =  numEdits + length(unlist(js$aliases))
  }
  # 
  # for(x in names(js$characterGroups)){
  #   dx = data.frame(char = unlist(js$characterGroups[x]))
  #   if(nrow(dx)>0){
  #     dx$group = x
  #     d = rbind(d,dx)
  #   }
  # }
  # out = paste(out,"\n\n",folder,"\n")
  # if(!alternativeMeasure){
  #  if(!is.null(js$mainPlayerCharacters)){
  #    if(length(js$mainPlayerCharacters)>0){
  #     out  = paste(out,paste(js$mainPlayerCharacters,collapse=","))
  #    } else{
  #      out = paste(out,"NONE")
  #    }
  #  }else{
  #    out = paste(out,"NONE")
  #  }
  # }
}