pjs.config({ 
    log: 'stdout',
    format: 'json',
    writer: 'file',
    outFile: 'scrape_output.json'
});

pjs.addSuite({
    url: "https://cryptotrader.org/traders/ZmguD4XzNospfqfJc",
    ready: function() {
	return $('#orders table tr').length > 0;
    },
    scraper: function() {
	return $('#orders table tr').map(function() {
	    if ($('th', $(this)).length) {
		var type = 'th'
	    } else {
		var type = 'td'
	    }
	    return [
		$(type, this).map(function() {
		    return $(this).text().trim();
		}).get()
	    ];
	}).get();
    }
});

