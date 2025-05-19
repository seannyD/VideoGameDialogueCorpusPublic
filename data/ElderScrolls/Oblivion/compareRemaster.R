library(stringr)
try(setwd("~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project_public/data/ElderScrolls/Oblivion/"))

orig = read.delim("raw/dialogueExport.txt",quote="",header = F)
names(orig) = c("name","race","faction","gender","quest","topic","id","version","filename","fullfilename","X1","X2","dialogue","emotion","X3","X4")

orig$id = tolower(orig$id)

orig$fullfilename2 = tolower(orig$fullfilename)
orig$fullfilename2 = gsub(".+oblivion.esm","",orig$fullfilename2)
orig$fullfilename2 = gsub("\\\\","/",orig$fullfilename2)

remaster = readLines("raw/remaster/OblivionRemastered_FileList.txt")
remaster = remaster[!grepl("/knights/",remaster)]
remaster = remaster[!grepl("/Shiv",remaster)]

remaster = gsub(".+/oblivion.esm","",remaster)
remaster = remaster[grepl("\\.mp3",remaster)]

dbits = strsplit(remaster,"/")
d_remaster = data.frame(
  fullfilename = remaster,
  race = sapply(dbits,function(X){X[2]}),
  gender = sapply(dbits,function(X){X[3]}),
  id = gsub("_","",str_extract(remaster, "_00[0-9a-z]+_")))

sum(remaster %in% orig$fullfilename2)

new = remaster[!remaster %in% orig$fullfilename2]
bits = strsplit(new,"/")
new = data.frame(
  fullfilename = new,
  race = sapply(bits,function(X){X[2]}),
  gender = sapply(bits,function(X){X[3]}),
  id = gsub("_","",str_extract(new, "_00[0-9a-z]+_")))

new = new[!new$id %in% orig$id,]

new = new[!grepl("holiday_",new$fullfilename),]

# Unfinished quests

uf = c("/ms17","/ms05","/ms11","/fgd06","/ms19","/ms25")
for(x in uf){
  new = new[!grepl(x,new$fullfilename),]
}



table(new$gender)
prop.table(table(new$gender))


x = orig[grepl("bedrental_bed",orig$fullfilename2),]
x2 = d_remaster[grepl("bedrental_bed",d_remaster$fullfilename),]

table(x$race,x$gender)
table(x2$race,x2$gender)

#x = orig[grepl("greet",orig$fullfilename2),]
#x2 = d_remaster[grepl("greet",d_remaster$fullfilename),]
x = orig
x2 = d_remaster
p = prop.table(table(x$race,x$gender),1)
p2 = prop.table(table(x2$race,x2$gender),1)

rownames(p) = gsub(" ","",tolower(rownames(p)))
rownames(p2) = gsub(" ","",tolower(rownames(p2)))
p = p[rownames(p2),]

dx = data.frame(
  prop = c(as.vector(p),as.vector(p2)),
  gender = rep(rep(c("F","M"),each=nrow(p)),2),
  race = rep(rep(rownames(p),2),2),
  game = rep(c("Original","Remaster"),each=length(p)))

library(ggplot2)
dx$prop2 = dx$prop
dx[dx$gender=="F",]$prop2 = - dx[dx$gender=="F",]$prop2
dx$race = factor(dx$race)
dx$game = factor(dx$game,levels = c("Remaster","Original"))

ggplot(dx,aes(y=race,x=prop2,fill=game)) + 
  geom_bar(stat="identity",position = "dodge") +
  geom_vline(xintercept = 0) +
  coord_cartesian(xlim=c(-1,1))

dxf = dx[dx$gender=="F",]
ggplot(dxf,aes(x=race,y=prop,fill=game)) + 
  geom_bar(stat="identity",position="dodge") +
  coord_flip() +
  ylab("Proportion of female dialogue") +
  xlab("Group") +
  geom_hline(yintercept = 0.5)

dxf2 = dxf[dxf$game=="Original",]
dxf2$propRemaster = dxf[dxf$game=="Remaster",]$prop
dxf2$cx = dxf2$prop-dxf2$propRemaster
dxf2$change = c("green",'red')[1+((dxf2$prop-dxf2$propRemaster)>0)]
dxf2$prop = dxf2$prop*100
dxf2$propRemaster = dxf2$propRemaster*100
dxf2$race = factor(dxf2$race,levels=dxf2[order(dxf2$cx,decreasing = T),]$race)

gx = ggplot(dxf2,aes(x=race,y=prop,color=game,
                xend=race,yend=propRemaster)) + 
  geom_hline(yintercept = 50) +
  geom_point(data=dxf2,mapping=aes(x=race,y=propRemaster),color="red") +
  geom_segment(arrow = arrow(length = unit(0.03, "npc")),
               color=dxf2$change) + 
  geom_point(stat="identity") +
  coord_flip()+
  ylab("Percentage of female dialogue lines") +
  xlab("Group")+
  scale_color_manual(name="Game",
                      values=c("Original"='black',"Remake"='red'),
                      labels = c("Original","Remake")) +
  scale_y_continuous(breaks= c(0,10,20,30,40,50,60),
                     labels =c("0%","10%","20%","30%","40%","50%","60%") ) +
  theme(legend.position = "top") 
  
pdf("~/Downloads/OblivionChange.pdf",width=5,height=3)  
gx
dev.off()

  
  

