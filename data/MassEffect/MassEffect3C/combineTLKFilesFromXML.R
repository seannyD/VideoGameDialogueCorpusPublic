library(stringr)
setwd("~/OneDrive - Cardiff University/Data/ME3XML/")

lang = "ESN"
for(lang in c("ESN","FRA","ITA","JPN","POL","RUS","DEU")){
  print(lang)
  files = list.files(".",paste0(lang,".xml"))
  dx = data.frame()
  for(file in files){
    ls = readLines(file)
    sx = as.data.frame(str_split_fixed(ls,'">', 2))
    names(sx) = c("id","txt")
    sx = sx[grepl("String id",sx$id),]
    sx$id = gsub(' +<String id="','',sx$id)
    sx$id = gsub('"',"",sx$id)
    sx$txt = gsub("</String>","",sx$txt)
    dx = rbind(dx,sx)
  }
  names(dx) = c("TLK StringRef","Line")
  write.csv(dx, paste0("ME3DialogueDump_",lang,".csv"))
}