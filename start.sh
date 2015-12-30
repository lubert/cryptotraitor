#!/bin/bash
cd $(dirname $(realpath $0))
# Scrape the JSON
/usr/local/bin/phantomjs pjscrape.js btce_scraper.js 2>&1 | tee scraper.log
# Run the python parser
/usr/bin/python parser.py
