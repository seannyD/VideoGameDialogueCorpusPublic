try(setwd("~/Documents/Cardiff/VideoGameScripts/project/analysis/"))

# Read the data
d = read.csv("../data/ChronoTrigger/ChronoTrigger/compareTranslations.csv",stringsAsFactors = F,encoding = "UTF-8")

# Plot the data
# (could add plot titles etc.)
plot(d$eng_word,d$jap_char)

# Measure the correlation between two measures
cor.test(d$eng_word,d$jap_char)

# Use a linear model to plot a line through the data
m1 = lm(d$jap_char~d$eng_word)
summary(m1)
plot(d$eng_word,d$jap_char)
abline(m1,col=2)

# Measure how far each point is from the line
# (the absolute value of the residual)
d$diff = resid(m1)

# Look at shorter types
shorts = d[d$eng_word<50,]
View(head(shorts[order(shorts$diff),]))
View(tail(shorts[order(shorts$diff),]))

# You could also use a linear model to test whether the 
# gender of the character predicts the difference
# in translation. You could do this by adding an 
# interaction effect between the length measure and gender