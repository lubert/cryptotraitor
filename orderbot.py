#!/usr/bin/python

import decimal
import time

import btceapi
import btcebot

class CryptoTrader(btcebot.TraderBase):
    def __init__(self, api, pair, action, live_trades = False):
        btcebot.TraderBase.__init__(self, (pair,))
        self.api = api
        self.action = action
        self.pair = pair
        self.live_trades = live_trades
        
        self.current_lowest_ask = None
        self.current_highest_bid = None
        
        # Apparently the API adds the fees to the amount you submit,
        # so dial back the order just enough to make up for the 
        # 0.2% trade fee.
        self.fee_adjustment = decimal.Decimal("0.998")
        
    def _attemptBuy(self, price, amount):
        conn = btceapi.BTCEConnection()
        info = self.api.getInfo(conn)
        curr1, curr2 = self.pair.split("_")

        # Limit order to what we can afford to buy.
        available = getattr(info, "balance_" + curr2)
        max_buy = available / price
        buy_amount = min(max_buy, amount) * self.fee_adjustment
        if buy_amount >= btceapi.min_orders[self.pair]:
            print "attempting to buy %s %s at %s for %s %s" % (buy_amount, 
                curr1.upper(), price, buy_amount*price, curr2.upper())
            if self.live_trades:
                r = self.api.trade(self.pair, "buy", price, buy_amount, conn)
                print "\tReceived %s %s" % (r.received, curr1.upper())
                # If the order didn't fill completely, cancel the remaining order
                if r.order_id != 0:
                    print "\tCanceling unfilled portion of order"
                    self.api.cancelOrder(r.order_id, conn)

    def _attemptSell(self, price, amount):
        conn = btceapi.BTCEConnection()
        info = self.api.getInfo(conn)
        curr1, curr2 = self.pair.split("_")
        
        # Limit order to what we have available to sell.
        available = getattr(info, "balance_" + curr1)
        sell_amount = min(available, amount) * self.fee_adjustment
        if sell_amount >= btceapi.min_orders[self.pair]:
            print "attempting to sell %s %s at %s for %s %s" % (sell_amount,
                curr1.upper(), price, sell_amount*price, curr2.upper())
            if self.live_trades:
                r = self.api.trade(self.pair, "sell", price, sell_amount, conn)
                print "\tReceived %s %s" % (r.received, curr2.upper())
                # If the order didn't fill completely, cancel the remaining order
                if r.order_id != 0:
                    print "\tCanceling unfilled portion of order"
                    self.api.cancelOrder(r.order_id, conn)

    def getBal(self, curr):
        conn = btceapi.BTCEConnection()
        info = self.api.getInfo(conn)
        return getattr(info, "balance_" + curr)
            
    # This overrides the onNewDepth method in the TraderBase class, so the 
    # framework will automatically pick it up and send updates to it.
    def onNewDepth(self, t, pair, asks, bids):
        ask_price, ask_amount = asks[0]
        bid_price, bid_amount = bids[0]
        if self.action == "BUY":
            self._attemptBuy(ask_price, ask_amount)
        elif self.action == "SELL":
            self._attemptSell(bid_price, bid_amount)
