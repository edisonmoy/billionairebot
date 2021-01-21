import websocket, json
import requests
import os
from dotenv import load_dotenv



load_dotenv()

AP_KEY = os.getenv("ALPACA_KEY")
APS_KEY = os.getenv("ALPACA_SECRET_KEY")

def open(ws):
    print("opened")
    auth_data = {
        "action": "authenticate",
        "data": {"key_id": AP_KEY, "secret_key": APS_KEY}
    }

    ws.send(json.dumps(auth_data))

    listen_message = {"data": {"streams": ["AM.PLTR"]}}

    ws.send(json.dumps(listen_message))


def response(ws, message):
    print("success")
    print(message)

def close(ws):
    print("closed")

socket = "wss://data.alpaca.markets/stream"

ws = websocket.WebSocketApp(socket, on_open=open, on_message=response, on_close=close)
ws.run_forever()