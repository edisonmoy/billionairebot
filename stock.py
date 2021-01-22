import websocket, json
import requests
import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
from alpaca_trade_api import StreamConn



load_dotenv()
SOCKET = "wss://data.alpaca.markets/stream"
AP_KEY = os.getenv("ALPACA_PAPER_KEY")
APS_KEY = os.getenv("ALPACA_PAPER_SECRET_KEY")
AP_PAPER_URL = "https://paper-api.alpaca.markets"

class Account:
    # Getting the account info
    def __init__(self):
        self.acc_api = tradeapi.REST(AP_KEY, APS_KEY, AP_PAPER_URL)
        self.acc = self.acc_api.get_account()
        if self.acc.trading_blocked:
            print("not able to trade")
    
    #checking how much we have in our account
    def check_balance(self):
        print("${} available to trade.".format(self.acc.buying_power))

    #daily profit
    def check_profit(self):
        change = float(self.acc.equity) - float(self.acc.last_equity)
        print(f'Today\'s portfolio balance change: ${change}')
    



    
class Trading:
    def __init__(self):
        self.api = tradeapi.REST(AP_KEY, APS_KEY, AP_PAPER_URL)
    
    def trade(self,ticker, num_of_shares, buy_or_sell, t):
        self.api.submit_order(
            symbol= ticker,
            qty = num_of_shares,
            side = buy_or_sell,
            type = t,
            time_in_force = "gtc"
        )
    #dummy function to test 
    def get_nasdaq_stocks(self):
        nasdaq = [i for i in self.api.list_assets(status="active") if i.exchange == "NASDAQ"]
        print(nasdaq)    
    
    #checking if the stock is tradable or not
    def tradable(self, ticker):
        asset = self.api.get_asset(ticker)
        if asset.tradable:
            print("yes we can trade")
        else:
            print("can't trade")

#testing streaming data

def open(ws):
    print("opened")
    ws_stream_conn = {
        "action": "authenticate",
        "data": {"key_id": AP_KEY, "secret_key": APS_KEY}
    }

    ws.send(json.dumps(ws_stream_conn))

    listen_message = {"action": "listen", "data": {"streams": ["T.PLTR"]}}

    ws.send(json.dumps(listen_message))


def response(ws, message):
    print("success")
    print(message)

def close(ws):
    print("closed")



# ws = websocket.WebSocketApp(SOCKET, on_open=open, on_message=response, on_close=close)
# ws.run_forever()
account = Trading()
account.trade("GME", 1000, "buy", "market")