setwd("~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project/data/StarWarsKOTOR/StarWarsKOTOR/")

d = read.csv("raw/dataset_20200716.csv")

d = d[d$speaker=="Conversation owner",]
d = d[!duplicated(d$source_dlg),]
d = d[!grepl("[A-Z][A-Z][A-Z]",d$text),]
d = d[!grepl("^\\[",d$text),]

d$charName = ""
d$gender = ""

write.csv(d[,c('charName',"gender","source_dlg","text","comment")],
          "ConversationOwnersToCode.csv")
