#!/bin/bash

file=scrape_output.json
minsize=3
retries=5

# Change dir to script path
cd $(dirname $(realpath $0))

n=0
until [ $n -ge $retries ]
do
    # Scrape the JSON
    /usr/local/bin/phantomjs pjscrape.js btce_scraper.js 2>&1 | tee scraper.log

    # Check JSON and retry if empty
    size=$(wc -c <"$file")
    if [ $size -ge $minsize ]; then
        break
    else
        n=$[$n+1]
        sleep 5
    fi
done

# Run the python parser
/usr/bin/python parser.py
