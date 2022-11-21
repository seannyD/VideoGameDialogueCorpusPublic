(cd processing

python3 getChoiceVariation.py

python3 dialogueTransitions.py)

(cd analysis

R -f compareToBaselines.R

R -f visualiseData.R

Rscript -e 'library(rmarkdown); rmarkdown::render("Analyse_WordsPerGender.Rmd")'

Rscript -e 'library(rmarkdown); rmarkdown::render("Analyse_MajorVsMinorCharacters.Rmd")'

Rscript -e 'library(rmarkdown); rmarkdown::render("Analyse_PlayerChoices.Rmd")'

Rscript -e 'library(rmarkdown); rmarkdown::render("Analyse_Transitions.Rmd")'

Rscript -e 'library(rmarkdown); rmarkdown::render("Analyse_Frequency.Rmd")')

(cd analysis/survey

Rscript -e 'library(rmarkdown); rmarkdown::render("analyseSurvey.Rmd")')

(cd analysis/Appendices

Rscript -e 'library(rmarkdown); rmarkdown::render("Analyse_Oblivion_Emotions.Rmd")'

Rscript -e 'library(rmarkdown); rmarkdown::render("Analyse_ChronoTriggerTranslations.Rmd")')

(cd analysis/reliability

Rscript -e 'library(rmarkdown); rmarkdown::render("Reliability.Rmd")')

