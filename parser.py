import json
import time
import logging
import sys
import btceapi
import btcebot
import orderbot
import smtplib
from datetime import datetime, timedelta
from dateutil import parser

# Globals
JSON_FILE = 'scrape_output.json'
ORDERS_FILE = 'orders.log'
KEY_FILE = 'keys.txt'
EMAIL_KEY_FILE = 'email_keys.txt'
LIVE_TRADING = True

# Init logging
def init_logging():
    logging.basicConfig(filename='parser.log',level=logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(console)
    sys.excepthook = excepthook

# Enable logging of exceptions
def excepthook(*args):
    logging.getLogger().error('Uncaught exception:', exc_info=args)

# Load JSON
def load_json(file_name, flag='r'):
    logging.debug("Loading '" + file_name + "'...")
    file = open(file_name, flag)
    return json.load(file)

# Write JSON
def write_json(data, file_name):
    logging.debug("Saving '" + file_name + "'...")
    file = open(file_name, 'w')
    json.dump(data, file)
    file.close()
    
# Check columns to match expected
def check_data(data):
    logging.debug("Checking array size...")
    assert len(data) > 1, "Unexpected array length: %r" % len(data)
    logging.debug("Checking column names...")
    col_array = data[0]
    assert col_array[0] == "Type", "Expected 'Type': %r" % col_array[0]
    assert col_array[1] == "Amount", "Expected 'Amount': %r" % col_array[1]
    assert col_array[2] == "Price", "Expected 'Price': %r" % col_array[2]
    assert col_array[3] == "At", "Expected 'At': %r" % col_array[3]

def onBotError(msg, tracebackText):
    tstr = time.strftime("%Y/%m/%d %H:%M:%S")
    print "%s - %s" % (tstr, msg)
    open("error.log", "a").write(
        "%s - %s\n%s\n%s\n" % (tstr, msg, tracebackText, "-"*80))

def sendemail(subject, message):
    # Credentials
    file = open(EMAIL_KEY_FILE, 'r')
    from_addr = username = file.readline().strip()
    password = file.readline().strip()
    to_addr = file.readline().strip()
    file.close()

    header  = 'From: %s\n' % from_addr
    header += 'To: %s\n' % to_addr
    header += 'Subject: %s\n\n' % subject
    message = header + message
 
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username,password)
    problems = server.sendmail(from_addr, to_addr, message)
    server.quit()
    if problems:
        logging.debug("Error: " + str(problems))
        return False
    else:
        logging.debug("Email sent!")
        return True

def createOrder(action):
    # Load keys and create an API object from the first one
    handler = btceapi.KeyHandler(KEY_FILE)
    key = handler.getKeys()[0]
    if LIVE_TRADING:
        logging.debug("**LIVE TRADING**")
    else:
        logging.debug("**SIMULATED TRADING**")
    logging.debug("Trading with key %s" % key)
    api = btceapi.TradeAPI(key, handler)

    # Create a trader that handles LTC/USD trades in the given range.
    trader = orderbot.CryptoTrader(api, "ltc_usd", action, logging.debug, LIVE_TRADING)

    # Create a bot and add the trader to it.
    bot = btcebot.Bot()
    bot.addTrader(trader)

    # Add an error handler so we can print info about any failures
    bot.addErrorHandler(onBotError)  

    # Update every 10 seconds
    bot.setCollectionInterval(10)
    bot.start()
    print "Running; press Ctrl-C to stop"

    if action == "SELL":
        curr = "ltc"
    elif action == "BUY":
        curr = "usd"

    try:
        while 1:
            bal = trader.getBal(curr)
            logging.debug("Balance is %s " % bal + curr.upper())
            if bal < btceapi.min_orders['ltc_usd']:
                logging.debug(action + " complete!")
                sendemail('Cryptotraitor order - ' + action, 'LTC: ' + str(trader.getBal('ltc'))
                          + '\nUSD: ' + str(trader.getBal('usd')))
                bot.stop()
                break
            time.sleep(10)
            
    except KeyboardInterrupt:
        print "Stopping..."
    finally:    
        bot.stop()

def main():
    init_logging()
    logging.debug("Starting at: " + datetime.now().strftime("%c"))

    data = load_json(JSON_FILE)
    check_data(data)
    
    last_order = data[-1]
    action = last_order[0]
    price = last_order[2]
    time = parser.parse(last_order[3])
    now = datetime.now()

    logging.debug("Now: " + now.strftime("%Y/%m/%d %H:%M:%S"))
    logging.debug("Last order time: " + time.strftime("%Y/%m/%d %H:%M:%S"))
    logging.debug("Last order action: " + action + " @ " + price)
    
    # Test send an email
    if (now - time) <= timedelta(hours = 2):
        logging.debug("Ready to " + action)
        createOrder(action)
    else:
        logging.debug('Order stale, exiting...')
    
if __name__ == "__main__":
    main()
