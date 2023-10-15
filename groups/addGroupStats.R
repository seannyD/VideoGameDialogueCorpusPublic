# Set working directory
try(setwd("~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project_public/groups/"))

# List of files starting with "group_"
listOfGroupFiles = list.files(".","group_.*.csv")

# For each group file ...
for(groupFile in listOfGroupFiles){
  # Load group data
  d = read.csv(groupFile,stringsAsFactors = F, encoding = "UTF-8",fileEncoding = "UTF-8")
  # Add extra columns for stats
  d[,c("stat_lines","stat_words","stat_sentences","stat_syllables")] = NA
  
  # For each game data folder
  foldersListed = unique(d$folder)
  for(folder in foldersListed){
    # Load the char stats for that game
    charStats = read.csv(paste0(folder,"stats_by_character.csv"),stringsAsFactors = F, encoding = "UTF-8",fileEncoding = "UTF-8")

    # Add or overwrite extra columns
    #   Get list of characters in group file
    groupCharNames = d[d$folder==folder,]$character
    #   Find corresponding stats for each character
    groupCharStats = charStats[match(groupCharNames,charStats$charName),c("lines","words","sentences","syllables")]
    #   Add stats to the main data frame
    d[d$folder==folder,c("stat_lines","stat_words","stat_sentences","stat_syllables")] = groupCharStats
  }
  
  # Write file back to origin
  write.csv(d, file=groupFile, row.names = F, fileEncoding = "UTF-8")
}
