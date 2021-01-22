import websocket, json
import requests
import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
from alpaca_trade_api import StreamConn



load_dotenv()
SOCKET = "wss://data.alpaca.markets/stream"
AP_KEY = os.getenv("ALPACA_KEY")
APS_KEY = os.getenv("ALPACA_SECRET_KEY")
AP_PAPER_URL = "https://paper-api.alpaca.markets"

class Trading:
    def __init__(self):
        self.api = tradeapi.REST('<key_id>', '<secret_key>', AP_PAPER_URL)
    
    def trade(self):
        print('hello')


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



ws = websocket.WebSocketApp(SOCKET, on_open=open, on_message=response, on_close=close)
ws.run_forever()

# tradingbot = Trading()
# tradingbot.trade()