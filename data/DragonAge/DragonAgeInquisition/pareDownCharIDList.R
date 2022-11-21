library(rjson)
d = fromJSON(file="~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project/data/DragonAge/DragonAgeInquisition_B/data.json")

nx = unique(names(unlist(d,use.names = T)))
nx = unique(gsub(".+\\.","",nx))
nx = gsub("OWNER","",nx)

idToChar = read.csv("~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project/data/DragonAge/DragonAgeInquisition_B/charIDToScreenName.csv",stringsAsFactors = F)

idToChar = idToChar[idToChar$ID %in% nx,]

cat(
  paste(paste0('"',idToChar$ID,'"',":",'"',idToChar$Name,'",'),collapse = "\n"),
  file = "~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project/data/DragonAge/DragonAgeInquisition_B/charIDToScreenName_Slim.json"
)
