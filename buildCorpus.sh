echo "SCRAPING ..."

# Run the scraper for each game in a sub-process
(cd data
for seriesDir in ./*/
do
	if [[ ($seriesDir != "./Test/") &&  ($seriesDir != "./ALL/") ]]; then
    	(cd "${seriesDir}"
    	for gameDir in ./*/
    	do
    		(cd "${gameDir}"
    		echo ${gameDir}
    		echo "mkdir -p raw"
    		echo "python3 scraper.py")
    	done)
    fi
done)

echo "PARSING ..."

(cd processing
echo "python3 parseRawData.py"
echo "python3 getStatistics.py")