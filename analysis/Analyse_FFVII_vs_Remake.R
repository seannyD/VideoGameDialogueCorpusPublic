library(ggplot2)
library(dplyr)
library(tidyr)
try(setwd("~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project_public/analysis/"))

# Load two stats files
ffvii = read.csv("../data/FinalFantasy/FFVII/stats_by_character.csv",stringsAsFactors = F)
ffviiRemake = read.csv("../data/FinalFantasy/FFVII_Remake/stats_by_character.csv",stringsAsFactors = F)

# Combine them
stats = rbind(ffvii,ffviiRemake)

# Final Fantasy VII characters
sx = stats

# Characters to look at 
chosenCharacters = c("Aerith","Tifa","Jessie","Marlene","Cloud","Barret","Biggs","Red XIII")
sx = sx[sx$charName %in% chosenCharacters,]
sx$charName = factor(sx$charName,levels=chosenCharacters)

# Work out the number of words a character says,
# as a proportion of the total for all selected characters
# (so within a game, this measure adds to 1 for the selected characters)
sx = sx %>% group_by(game) %>%
  mutate(prop = words / sum(words)) 

# Work out change in proportion
change = tapply(sx$prop,sx$charName,function(X){
  #x = round(((X[2] - X[1]) /X[1])*100)
  x = round(((X[2]-X[1])/X[1])*100)
  paste0(c("","+")[1+(x>0)],x,"%")
  #paste(round(X[1]/X[2] * 100),"%")
})
changeD = data.frame(
  x2 = 1:length(change),
  y2 = tapply(sx$prop,sx$charName,max),
  change = change,
  game = "Final Fantasy VII"
)

# Plot data
pdf("../results/graphs/FFVII_Character_Comparison.pdf",
    width=6,height=4)
sx %>% ggplot(aes(x=charName,fill=game,y=prop)) +
  geom_bar(stat="identity", position = 'dodge') +
  theme(legend.position = "top",
        panel.grid.major.x = element_blank()) + 
  geom_vline(xintercept = seq(1.5,7.5,1),color="white")+
  scale_fill_brewer(palette="Dark2") +
  geom_text(data=changeD,aes(x=x2,y=y2,label=change),vjust=-0.2) +
  coord_cartesian(ylim=c(0,0.55)) +
  geom_label(label="Female",x=2.5,y=0.5,color="white",fill="black") +
  geom_label(label="Male",x=6.5,y=0.5,color="white",fill="black") +
  geom_vline(xintercept = 4.5,size=2)

dev.off()