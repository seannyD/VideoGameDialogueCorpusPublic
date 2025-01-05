setwd("~/OneDrive - Cardiff University/Research/Cardiff/VideoGameScripts/project_public/analysis/violence/")

library(openxlsx)
library(stringr)
source("../_CorpusHelperFunctions.R")

d = read.csv("../../results/doNotShare/PostDefeat.csv",stringsAsFactors = F)
d = d[d$folder!="",]


folders = unique(d$folder)
folders = folders[folders!=""]

nrow(d)
length(unique(d$context))


femaleTotal = 0
maleTotal = 0
for(folder in folders){
  freq = read.csv(paste0("../",folder,"stats.csv"))
  femaleTotal = femaleTotal + freq[freq$group=="female",]$words
  maleTotal = maleTotal + freq[freq$group=="male",]$words
}
  

femalePostDefeat = 6632
malePostDefeat = 15967

femalePostDefeat.prop = femalePostDefeat/ (femalePostDefeat+malePostDefeat)
total.prop = femaleTotal / (femaleTotal+maleTotal)

femalePostDefeat.prop
total.prop

m = matrix(c(
    femalePostDefeat,
    malePostDefeat,
    femaleTotal - femalePostDefeat,
    maleTotal - malePostDefeat),nrow = 2)

chisq.test(m)

d$line.clean = gsub("\\!+","!",d$line)
d$line.clean = gsub("\\?+","?",d$line.clean)

maleSymbols = table(unlist(strsplit(d[d$charGender=="male",]$line.clean,"")))
femaleSymbols = table(unlist(strsplit(d[d$charGender=="female",]$line.clean,"")))

numFemaleLines = sum(d$charGender=="female")
numMaleLines = sum(d$charGender=="male")

printchisq = function(x){
  cx = chisq.test(x)
  px = cx$p.value
  if(px < 0.001){
    px = "< 0.001"
  } else{
    px = round(px,3)
  }
  effectSize = paste("Female prob: ", 1000*(x[1,1]/x[2,1]),"\n",
                     "Male prob:   ", 1000*(x[1,2]/x[2,2]))
  stat = paste("Chisq = ",round(cx$statistic,3),", p = ",px)
  cat(paste(effectSize,"\n",stat,"\n"))
}

chiTest2 = function(x){
  dx = c(femaleSymbols[x],sum(femaleSymbols[names(femaleSymbols)!=x]),
    maleSymbols[x],sum(maleSymbols[names(maleSymbols)!=x]))
  dx = matrix(dx,nrow = 2)
  printchisq(dx)
  # chisq with num lines
  dx2 = dx
  dx2[2,1] = numFemaleLines
  dx2[2,2] = numMaleLines
  
  printchisq(dx2)
}

chiTest2("!")

chiTest2("?")

# thanks
thank = table(grepl("thank",tolower(d$line)),d$charGender)
thank = thank[,c("female","male")]
chisq.test(thank)
prop.table(thank,2)
prop.table(thank,2)[2,1]/prop.table(thank,2)[2,2]

# Only a flesh wound
w = read.xlsx("../../../violence/OnlyAFleshWound_TVTropes.xlsx")
w = w[!is.na(w$Case),]
w$Exclude[is.na(w$Exclude)] = 'n'
w = w[w$Exclude!='y',]
w$Reversal[is.na(w$Reversal)] = 'n'
w$Reversal[w$Reversal=="Y"] = 'n'

w$Gender[is.na(w$Gender)] = 'x'

w = w[w$Gender %in% c("m",'f'),]
table(w$Gender[w$Reversal=="n"])

binom.test(table(w$Gender[w$Reversal=="n"]))

table(w$Gender,w$Reversal)
prop.table(table(w$Gender,w$Reversal),1)

fisher.test(table(w$Gender,w$Reversal))

library(syuzhet)
d$sentiment.syuzhet = get_sentiment(d$line)
dx = d[!is.na(d$charGender) & d$charGender %in% c("male","female"),]
t.test(dx$sentiment.syuzhet~dx$charGender)

#library(udpipe)
#dlF <- udpipe_download_model(language = "french-sequoia")
#ux = udpipe(d$line)
#sent = txt_sentiment(d$line)


#######
# FFXIV
f = read.csv("../../data/FinalFantasy/FFXIV/charProperties.csv",stringsAsFactors = F)
f$Bust.Size = factor(f$Bust.Size,levels=c("0%","25%","50%","75%","100%"),ordered = T)
f$Muscle.Tone = factor(f$Muscle.Tone,levels=c("0%","25%","50%","75%","100%"),ordered = T)

table(f$Gender)

nrow(f)

table(f$Gender,f$weapons!="")
prop.table(table(f$Gender,f$weapons!=""),1)
fisher.test(table(f$Gender,f$weapons!=""))

# female NPCs are % less likely to carry a weapon
fProp = sum(f[f$Gender=="Female",]$weapons!="")/sum(f$Gender=="Female")
mProp = sum(f[f$Gender=="Male",]$weapons!="")/sum(f$Gender=="Male")
(mProp-fProp)/mProp

f$numWeapons = 1
f[f$weapons=="",]$numWeapons = 0
f[grepl(" / ",f$weapons),]$numWeapons = 2
table(f$Gender,f$numWeapons)
prop.table(table(f$Gender,f$numWeapons),1)
fisher.test(table(f$Gender,f$numWeapons==2))

# Bust size
f2 = f[f$Gender=="Female" & f$Body.Type!="Child",]
table(f2$Bust.Size,f2$weapons!="")
prop.table(table(f2$Bust.Size,f2$weapons!=""),1)

#table(f$Bust.Size,f$numWeapons)
#prop.table(table(f$Bust.Size,f$numWeapons),1)

library(ggplot2)
x = data.frame(
  Bust.Size = sort(unique(f2$Bust.Size)),
  propWithWeapons = prop.table(table(f2$Bust.Size,f2$weapons!=""),1)[,2]*100
)
ggplot(x, aes(x=Bust.Size,y=propWithWeapons)) +
  geom_bar(stat="identity") +
  ylab("Percentage of\nfemale NPCs\ncarrying weapons") +
  xlab("NPC character model bust size") +
  theme(axis.title.y = element_text(angle=0,vjust = 0.5))

cor.test(as.numeric(f$weapons!=""),as.numeric(f$Bust.Size),method = 's')
cor.test(as.numeric(f$weapons!=""),as.numeric(f$Bust.Size),method = 'k')

summary(glm(f$weapons!=""~f$Bust.Size,family="binomial"))

# Muscles
f3 = f[f$Gender=="Male" & f$Body.Type!="Child",]
prop.table(table(f3$Muscle.Tone,f3$weapons!=""),1)
cor.test(as.numeric(f3$weapons!=""),
         as.numeric(f3$Muscle.Tone),
         method = 's')

summary(glm(f$weapons!=""~f$Muscle.Tone, data =f3,family="binomial"))
x = data.frame(
  Muscle.Tone = sort(unique(f3$Muscle.Tone)),
  propWithWeapons = prop.table(table(f3$Muscle.Tone,f3$weapons!=""),1)[,2]*100
)
xf = data.frame(
  Muscle.Tone = sort(unique(f2$Muscle.Tone)),
  propWithWeapons = prop.table(table(f2$Muscle.Tone,f2$weapons!=""),1)[,2]*100
)
ggplot(x, aes(x=Muscle.Tone,y=propWithWeapons)) +
  geom_bar(stat="identity") +
  ylab("Percentage of\nmale NPCs\ncarrying weapons") +
  xlab("NPC character model muscle tone") +
  theme(axis.title.y = element_text(angle=0,vjust = 0.5))

ggplot(xf, aes(x=Muscle.Tone,y=propWithWeapons)) +
  geom_bar(stat="identity") +
  ylab("Percentage of\nfemale NPCs\ncarrying weapons") +
  xlab("NPC character model muscle tone") +
  theme(axis.title.y = element_text(angle=0,vjust = 0.5))

# Eyes

fisher.test(table(f[f$Gender=="Male"& f$Body.Type=="Adult",]$Iris.Size,
                 f[f$Gender=="Male"& f$Body.Type=="Adult",]$weapons==""),1)
tx = table(f[f$Gender=="Female" & f$Body.Type=="Adult",]$Iris.Size,
      f[f$Gender=="Female" & f$Body.Type=="Adult",]$weapons=="")
prop.table(tx,1)
fisher.test(tx)



library(party)
ct = ctree(as.factor(Muscle.Tone) ~ as.factor(Gender) + 
             as.factor(Race) + numWeapons + as.factor(Body.Type),
           data = f[!is.na(f$Muscle.Tone),])
plot(ct)

ct = ctree( numWeapons ~ as.factor(Gender) + 
             as.factor(Race) + 
              as.factor(Muscle.Tone),
           data = f[!is.na(f$Muscle.Tone),])
plot(ct)

# HEALING

extraHealingItems = c("Common Makai Sun Guide's Oilskin",
                      "Common Makai Moon Guide's Gown",
                      "Hakuko Dogi",
                      "Republican Medicus's Chiton",
                      "Wolf Robe",
                      "Blessed Gown",
                      "Pilgrim's Robe",
                      "Royal Vest",
                      "Robe of the Divine Harvest",
                      "Weathered Daystar Robe",
                      "Daystar Robe",
                      "Arachne Robe",
                      "Ishgardian Chaplain's Alb",
                      "Woad Skydruid's Fur",
                      "Halonic Priest's Alb",
                      "Sharlayan Preceptor's Coat",
                      "Valerian Shaman's Chasuble",
                      "Robe of the White Griffin",
                      "Plague Doctor's Coat",
                      "Prophet's Chestwrap",
                      "Makai Sun Guide's Oilskin",
                      "Makai Moon Guide's Gown",
                      "Shire Preceptor's Coat",
                      "Augmented Shire Preceptor's Coat",
                      "Ruby Cotton Chasuble",
                      "Valerian Priest's Top",
                      "Ivalician Astrologer's Tunic",
                      "Bonewicca Soother's Chestpiece",
                      "Ivalician Chemist's Robe",
                      "Ivalician Mystic's Coat",
                      "Common Makai Sun Guide's Slops",
                      "Common Makai Moon Guide's Quartertights",
                      "Hakuko Tsutsu-hakama",
                      "Republican Medicus's Loincloth",
                      "Wolf Tights",
                      "Blessed Slops",
                      "Pilgrim's Slops",
                      "Royal Breeches",
                      "Tonban of the Divine Harvest",
                      "Weathered Daystar Breeches",
                      "Daystar Breeches",
                      "Ishgardian Chaplain's Breeches",
                      "Woad Skydruid's Breeches",
                      "Halonic Priest's Breeches",
                      "Sharlayan Preceptor's Longkilt",
                      "Valerian Shaman's Smalls",
                      "Chausses of the White Griffin",
                      "Plague Doctor's Trousers",
                      "Prophet's Culottes",
                      "Makai Sun Guide's Slops",
                      "Makai Moon Guide's Quartertights",
                      "Shire Preceptor's Hose",
                      "Augmented Shire Preceptor's Hose",
                      "Ruby Cotton Smalls",
                      "Valerian Priest's Bottoms",
                      "Ivalician Astrologer's Slops",
                      "Bonewicca Soother's Trousers",
                      "Ivalician Chemist's Bottoms",
                      "Ivalician Mystic's Bottoms",
                      "Common Makai Sun Guide's Circlet",
                      "Common Makai Moon Guide's Circlet",
                      "Hakuko Men",
                      "Republican Medicus's Laurel Wreath",
                      "Wolf Hat",
                      "Blessed Monocle",
                      "Pilgrim's Eyepatch",
                      "Royal Crown",
                      "Circlet of the Divine Harvest",
                      "Gold Spectacles",
                      "Weathered Daystar Circlet",
                      "Daystar Circlet",
                      "Ishgardian Chaplain's Klobuk",
                      "Woad Skydruid's Hood",
                      "Halonic Priest's Klobuk",
                      "Sharlayan Preceptor's Hat",
                      "Valerian Shaman's Temple Chain",
                      "Hood of the White Griffin",
                      "Plague Doctor's Mask",
                      "Prophet's Mask",
                      "Makai Sun Guide's Circlet",
                      "Shire Preceptor's Hat",
                      "Augmented Shire Preceptor's Hat",
                      "Koppranickel Temple Chain",
                      "Valerian Priest's Hat",
                      "Ivalician Astrologer's Eyeglasses",
                      "Bonewicca Soother's Mask",
                      "Ivalician Chemist's Monocle",
                      "Ivalician Mystic's Hat",
                      "Wolf Satchel Belt",
                      "Wolf Satchel Belt",
                      "Blessed Belt",
                      "Pilgrim's Sash",
                      "Royal Sash",
                      "Belt of the Divine Harvest",
                      "Weathered Daystar Belt",
                      "Daystar Belt",
                      "Ishgardian Chaplain's Corset",
                      "Woad Skydruid's Belt",
                      "Halonic Priest's Corset",
                      "Sharlayan Preceptor's Belt",
                      "Valerian Shaman's Sash",
                      "Belt of the White Griffin",
                      "Plague Doctor's Belt",
                      "Prophet's Belt",
                      "The Belt of the Makai Guide",
                      "Shire Preceptor's Belt",
                      "Augmented Shire Preceptor's Belt",
                      "Valerian Priest's Belt",
                      "Ivalician Astrologer's Belt",
                      "Bonewicca Soother's Belt",
                      "Ivalician Chemist's Belt",
                      "Ivalician Mystic's Belt",
                      "Wolf Satchel Belt",
                      "Wolf Satchel Belt",
                      "Blessed Belt",
                      "Pilgrim's Sash",
                      "Royal Sash",
                      "Belt of the Divine Harvest",
                      "Weathered Daystar Belt",
                      "Daystar Belt",
                      "Ishgardian Chaplain's Corset",
                      "Woad Skydruid's Belt",
                      "Halonic Priest's Corset",
                      "Sharlayan Preceptor's Belt",
                      "Valerian Shaman's Sash",
                      "Belt of the White Griffin",
                      "Plague Doctor's Belt",
                      "Prophet's Belt",
                      "The Belt of the Makai Guide",
                      "Shire Preceptor's Belt",
                      "Augmented Shire Preceptor's Belt",
                      "Valerian Priest's Belt",
                      "Ivalician Astrologer's Belt",
                      "Bonewicca Soother's Belt",
                      "Ivalician Chemist's Belt",
                      "Ivalician Mystic's Belt")

findAny = function(extraDescription){
  any(sapply(extraHealingItems,function(n){grepl(extraDescription,n,ignore.case = T)}))
}
numAny = function(extraDescription){
  sum(sapply(extraHealingItems,function(n){grepl(n,extraDescription,ignore.case = T)}))
}

f$extras.healing = grepl("healing",tolower(f$extras)) | sapply(f$extras,findAny)
f$extras.healing.num = str_count(tolower(f$extras), "of healing") + sapply(f$extras,numAny)
table(f$Gender,f$extras.healing)
prop.table(table(f$Gender,f$extras.healing),1)
fisher.test(table(f$Gender,f$extras.healing))

f$extras.healing.explicit = grepl("healing",tolower(f$extras)) 
table(f$Gender,f$extras.healing.explicit)
prop.table(table(f$Gender,f$extras.healing.explicit),1)
fisher.test(table(f$Gender,f$extras.healing.explicit))

fProp2 = sum(f[f$Gender=="Female",]$extras.healing)/sum(f$Gender=="Female")
mProp2 = sum(f[f$Gender=="Male",]$extras.healing)/sum(f$Gender=="Male")
(fProp2-mProp2)/fProp2

#sort(table(str_extract(f$extras, "of .+?(/|^)")))

