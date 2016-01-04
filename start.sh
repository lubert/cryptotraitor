#!/bin/bash

minsize=3
retries=5

# Change dir to script path
cd $(dirname $(realpath $0))

n=0
file=live_url.conf
until [ $n -ge $retries ]
do
    # Scrape the JSON
    /usr/local/bin/phantomjs btce_live_scraper.js 2>&1 | tee live_url.conf

    # Check JSON and retry if empty
    size=$(wc -c <"$file")
    if [ $size -ge $minsize ]; then
        break
    else
        n=$[$n+1]
        sleep 5
    fi
done

n=0
file=scrape_output.json
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
