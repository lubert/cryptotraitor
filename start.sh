#!/bin/sh
# Scrape the JSON
/usr/local/bin/phantomjs pjscrape.js ltc_scraper.js 2>&1 | tee test.log
# Run the python parser
python parser.py
