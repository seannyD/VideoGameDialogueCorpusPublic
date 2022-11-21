library(jsonlite)
try(setwd("~/Documents/Cardiff/VideoGameScripts/project/data/MassEffect/MassEffect3B/"))

d = read_json("data.json")[["text"]]
d = unlist(d)
d = d[grepl("CHECK",names(d))]
names(d) = gsub("CHOICE\\.","",names(d))

#d[grepl("This is [A-Z][a-z]",d)]
#d[grepl("[A-Z][a-z]+ here\\.",d)]

nx = sapply(unique(names(d)),function(X){
  X = unlist(head(d[names(d)==X],n = 2))
  if(length(X)==1){
    X = c(X,"")
  }
  return(X)
})

n1 = sapply(unique(names(d)),function(X){
  head(d[names(d)==X],n = 1)
})

n2 = sapply(unique(names(d)),function(X){
  dx = d[names(d)==X]
  if(length(dx)>1){
    return(dx[2])
  } else{
    return("")
  }
}) 

n3 = sapply(unique(names(d)),function(X){
  dx = d[names(d)==X]
  if(length(dx)>2){
    return(dx[3])
  } else{
    return("")
  }
}) 


out  = data.frame(
  checkName = unique(names(d)),
  charName = "",
  gender = "",
  numLines = sapply(unique(names(d)),function(X){
    sum(X==names(d))
  }),
  line1 = n1,
  line2 = n2,
  line3 = n3,
  stringsAsFactors = F
)


#filledIn  = read.csv("~/Downloads/checkChars.csv",stringsAsFactors = F)
#sum(filledIn$checkName %in% out$charName)
#filledIn[filledIn$checkName %in% out$charName,]

write.csv(out,"checkChars.csv",row.names = F)
