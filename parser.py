import json
import time
import logging
import sys
from datetime import datetime
from dateutil import parser

# Globals
JSON_FILE = 'scrape_output.json'
ORDERS_FILE = 'orders.log'

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

def main():
    init_logging()
    logging.debug("Starting at: " + datetime.now().strftime("%c"))

    data = load_json(JSON_FILE)
    check_data(data)
    
    try:
        orders = load_json(ORDERS_FILE, 'w+')
    except ValueError: 
        logging.debug("Orders is empty.")
        orders = []
    
if __name__ == "__main__":
    main()
