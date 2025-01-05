setwd("~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project_public/analysis/")

library(jsonlite)
library(igraph)
library(ggplot2)

d = read_json("../data/BaldursGate/BaldursGate3/data.json")
d = d[["text"]]

meta = read_json("../data/BaldursGate/BaldursGate3/meta.json")
gender = meta[["characterGroups"]]

maleChars = unlist(gender["male"])
femaleChars = unlist(gender["female"])
allChars = as.vector(c(femaleChars,maleChars))

allLines = data.frame(
  id = rep(ids,sapply(children,length)),
  charName = rep(charNames, sapply(children,length)))

charNames = sapply(d,function(X){names(X)[1]})
d2 = d[charNames %in% allChars]

ids = sapply(d2,function(X){X$`_id`})
charNames = sapply(d2,function(X){names(X)[1]})
children = sapply(d2,function(X){unlist(X$`_children`)})

dx = data.frame(
  id = rep(ids,sapply(children,length)),
  charName = rep(charNames, sapply(children,length)),
  children = unlist(children))

dx$childName = d[match(dx$children,d$id)]

tx = table(dx$charName)
outSummary = data.frame(
  charName = names(tx),
  totalOut = as.vector(tx))

numLinesPerChar = table(sapply(d2,function(X){names(X)[1]}))
outSummary$numLines = numLinesPerChar[outSummary$charName]

outSummary$averageOutDegree = outSummary$totalOut/outSummary$numLines
outSummary = outSummary[order(outSummary$averageOutDegree),]

outSummary$male = outSummary$charName %in% as.vector(maleChars)

indegree = unlist(sapply(d,function(X){unlist(X$`_children`)}))
indegreeName = allLines[match(indegree,allLines$id),]$charName
indegreeName = indegreeName[!is.na(indegreeName)]
indegreeSum = table(indegreeName)
outSummary$totalIn = indegreeSum[outSummary$charName]
outSummary$averageInDegree = outSummary$totalIn/outSummary$numLines



outSummary = outSummary[outSummary$averageOutDegree>=0.9,]
outSummary = outSummary[!outSummary$charName %in% c("Narrator","Owlbear Cub","Gale's Projection"),]

boxplot(outSummary$averageOutDegree~ outSummary$male)
t.test(outSummary$averageOutDegree~ outSummary$male)

boxplot(outSummary$averageInDegree ~ outSummary$male)
t.test(outSummary$averageInDegree ~ outSummary$male)


plot(as.vector(outSummary$averageInDegree[1:40]), 
     as.vector(outSummary$averageOutDegree[1:40]))

outSummary$gender = c("female","male")[1+outSummary$male]
ggplot(outSummary, aes(x=gender,y=averageOutDegree)) +
  geom_violin() +
  geom_boxplot(width=0.3)

trueDiff = diff(tapply(outSummary$averageOutDegree,outSummary$male,mean))
perm = function(X){
  diff(tapply(sample(outSummary$averageOutDegree),
              outSummary$male,mean))
}
permDiff = replicate(10000,perm())
sum(permDiff>trueDiff)/10000

gx1 = c(allLines$id,dx$charName)
gx2 = c(allLines$charName,dx$children)

library(igraph)
g = graph_from_edgelist(cbind(gx1,gx2))
deg = degree(g)
deg = deg[allChars]

outSummary$gDegree = deg[outSummary$charName]
t.test(outSummary$gDegree ~ outSummary$male)

betw = betweenness(g)

cent = eigen_centrality(g,directed = TRUE)
outSummary$gCentrality = cent$vector[outSummary$charName]
boxplot(outSummary$gCentrality ~ outSummary$male)
t.test(outSummary$gCentrality ~ outSummary$male)


os2 = outSummary[outSummary$charName %in% 
                   c("Astarion",'Shadowheart',"Lae'zel",
        "Karlach","Gale","Wyll","Minthara",
        "Jaheira","Halsin","Minsc"),]
boxplot(os2$gDegree ~ os2$male)
t.test(os2$averageOutDegree ~ os2$male)
