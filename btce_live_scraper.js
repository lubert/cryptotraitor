var page = require('webpage').create();

page.open('https://cryptotrader.org/strategies', function(status) {
  page.onCallback = function(msg) {
    switch (msg.method) {
    case 'success':
      console.log(msg.data);
      phantom.exit();
      break;
    case 'error':
    default:
      phantom.exit();
    }
  };

  page.onResourceRequested = function(requestData, request) {
    if ((/http:\/\/.+?\.css/gi).test(requestData['url']) || requestData['Content-Type'] == 'text/css') {
      console.log('The url of the request is matching. Aborting: ' + requestData['url']);
      request.abort();
    }
  };

  page.evaluate(function() {
    function waitFor(config) {
      config._start = config._start || new Date();
      
      if (config.timeout && new Date - config._start > config.timeout) {
        if (config.error) config.error();
        if (config.debug) console.log('timedout ' + (new Date - config._start) + 'ms');
        return;
      }

      if (config.check()) {
        if (config.debug) console.log('success ' + (new Date - config._start) + 'ms');
        config.success();
        return;
      }

      setTimeout(waitFor, config.interval || 0, config);
    }

    waitFor({
      check: function() {
        return $('.strategies-list').is(':visible');
      },
      success: function() {
        var name = 'Thanasis Royal Investor';
        var link = $('a:contains("' + name + '")');
        link.click();

        waitFor({
          check: function() {
            return $('#traders table tr').length > 1;
          },
          success: function() {
            $('#traders .btn-trader-detail').click();

            waitFor({
              check: function() {
                return $('#trader-detail-tab').is(':visible');
              },
              success: function() {
                window.callPhantom({
                  method: 'success',
                  data: window.location.href
                });
              },
              error: function() {
                window.callPhantom({method: 'error'});                
              }
            });
          },
          error: function() {
            window.callPhantom({method: 'error'});
          }
        });
      },
      error: function() {
        window.callPhantom({method: 'error'});
      }
    });
  });
});
