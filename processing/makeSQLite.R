try(setwd("~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project_public/processing/"))

library(Hmisc)
library(quanteda)
library(quanteda.textstats)
library(dplyr)
library(dbplyr)
library(RSQLite)
library(stringr)

source("../analysis/_CorpusHelperFunctions.R")

escapeHTML = function(d,columns){
  d = d %>% mutate_at(columns,
                      stringr::str_replace_all, 
                      pattern = "<", replacement = "&lt;")
  d = d %>% mutate_at(columns,
                      stringr::str_replace_all, 
                      pattern = ">", replacement = "&gt;")
  return(d)
}




d = loadJSONScripts("../data/MonkeyIsland/")
d = d[!d$character %in% c("ACTION","GOTO","STATUS","LOCATION","CHOICE"),]
d = escapeHTML(d,c("dialogue","character"))

# List of games
d$gameID = as.integer(factor(d$folder))
games = d[,c("gameID", "game","series","year","folder")]
games = games[!duplicated(games),]
names(games)[names(games)=="gameID"] = "pk"

# List of characters
# TODO: This doesn't respect characters named the same across games?
d$charID = as.integer(factor(paste(d$folder,d$character)))
characters = d[,c("charID","character","Group_male","Group_female")]
characters = characters[!duplicated(characters),]
names(characters)[names(characters)=="charID"] = "pk"

corp = corpus(d, text_field = "dialogue")
toks = tokens(corp, remove_punct = FALSE)
#toks = tokens_tolower(toks)

tokLengths = sapply(toks,length)
d2 = data.frame(
  gameID = rep(d$gameID,tokLengths),
  character = rep(d$charID,tokLengths),
  lineID = as.integer(rep(1:length(toks),tokLengths)),
  word = unlist(toks)
)

shiftWords = function(dx,n){
  x = tapply(dx$word,dx$lineID,function(X){
    Hmisc::Lag(X,n)})
  x[x==" "] = ""
  return(x)
}

windows = -4:4
windows = windows[windows!=0]
for(i in windows){
  prefix = "m"
  if(i>0){prefix = "p"}
  d2[,paste0(prefix,abs(i))] = unlist(shiftWords(d2,i))
}

d2 = as_tibble(d2)
games = as_tibble(games)
characters = as_tibble(characters)

my_db_file <- "../web/VGDC.sql"

con <- DBI::dbConnect(RSQLite::SQLite(), my_db_file)
# TODO: add 'types'?
copy_to(con, d2, "words",overwrite = T,temporary=FALSE)
copy_to(con, games, "games",overwrite = T,temporary=FALSE)
copy_to(con, characters, "chars",overwrite = T,temporary=FALSE)
DBI::dbDisconnect(con)



#SELECT lineID,word FROM words WHERE lineID in
#(SELECT DISTINCT lineID 
#  FROM words 
#  WHERE words.word="well")


#SELECT lineID,GROUP_CONCAT(word," ") FROM words WHERE lineID in
#(SELECT DISTINCT lineID 
# FROM words 
# WHERE words.word="Guybrush" AND words.m1="Threepwood")
#GROUP BY lineID

# Lagging directly in SQLite
#SELECT * FROM
#(SELECT  lineID, word,
#  LAG (word, -1, "") OVER (PARTITION BY lineID) wordM1
#  FROM words )
#WHERE word="Guybrush" and wordM1="Threepwood"


SELECT wordM1, count(wordM1)  as 'freq'  from 
(SELECT word,
  LAG (word, 1, "") OVER (PARTITION BY lineID) wordM1,
  LAG (word, 2, "") OVER (PARTITION BY lineID) wordM2
  FROM words )
WHERE word="Guybrush"
GROUP BY wordM1
ORDER BY freq DESC



# Union after calculating frequency
SELECT wordM1, count(wordM1)  as 'freq'  from 
(SELECT word,
  LAG (word, 1, "") OVER (PARTITION BY lineID) wordM1
  FROM words )
WHERE word="Guybrush"
GROUP BY wordM1

UNION

SELECT wordM1, count(wordM1)  as 'freq'  from 
(SELECT word,
  LAG (word, 2, "") OVER (PARTITION BY lineID) wordM1
  FROM words )
WHERE word="Guybrush"
GROUP BY wordM1

UNION

SELECT wordM1, count(wordM1)  as 'freq'  from 
(SELECT word,
  LAG (word, 3, "") OVER (PARTITION BY lineID) wordM1
  FROM words )
WHERE word="Guybrush"
GROUP BY wordM1

ORDER BY freq DESC

