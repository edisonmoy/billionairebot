import json
from websocket import create_connection
import requests
import os
from dotenv import load_dotenv
import threading
import ast
import time


load_dotenv()

AV_KEY = os.getenv("ALPHA_VANTAGE_KEY")
TIINGO_KEY = os.getenv("TIINGO_KEY")
AV_BASE_URL = f"https://www.alphavantage.co/query?apikey={AV_KEY}"


class StockData:
    def __init__(self, ticker):
        self.ticker = ticker

    def request_builder(self, args_map):
        '''
        Returns request URL given arguments in dict
        '''
        request_url = AV_BASE_URL + "&symbol="+self.ticker
        for key in args_map:
            request_url += f'&{key}={args_map[key]}'
        return request_url

    def intraday_price(self, interval):
        '''
        Return price data from given interval.
        Interval: 1, 5, 15, 30, 60min
        '''
        request_args = {"function": "TIME_SERIES_INTRADAY",
                        "interval": interval}
        request_url = self.request_builder(request_args)
        print(request_url)

        data = requests.get(request_url).json()
        return data

    def price_one_min(self):
        '''
        Return price data from 1 minute interval.
        '''
        return self.intraday_price("1min")

    def price_five_min(self):
        '''
        Return price data from 5 minute interval.
        '''
        return self.intraday_price("5min")

    def price_daily(self, size="compact"):
        '''
        Return price data from daily interval.
        Size: compact provides 100 days (default) or full for 20yrs.
        '''
        request_args = {
            "function": "TIME_SERIES_DAILY_ADJUSTED", "outputsize": size}
        request_url = self.request_builder(request_args)
        print(request_url)
        data = requests.get(request_url).json()
        return data


class StockSocket:
    '''
    Websocket used to strean stock data as it becomes available in real time. Can
    add any number of tickers to socket stream.
    '''

    def __init__(self):
        self.sub_id = None
        self.thread_lock = threading.Lock()
        self.tickers = {}

        # Create websocket connection
        try:
            x = threading.Thread(target=self.__create_websocket)
            x.start()
        except:
            print("Can't start thread")

    def __create_websocket(self):
        '''
        Initiate websocket connection.

        Lock is used to ensure websocket is open and self.sub_id is assigned
        before changing tickers.
        '''
        self.thread_lock.acquire()

        # Connect to socket and send payload
        ws = create_connection("wss://api.tiingo.com/iex")
        payload = {
            'eventName': 'subscribe',
            'authorization': TIINGO_KEY,
            'eventData': {
                'thresholdLevel': 5,
                'tickers': ['spy']

            }
        }
        ws.send(json.dumps(payload))

        # Print data until thread is killed
        while True:
            response = json.loads(ws.recv())
            print(response)
            # If opening connection, assign self.sub_idfor future reference
            if self.sub_id is None:
                try:
                    sub_id = response.get(
                        "data").get("subscriptionId")
                    self.sub_id = sub_id
                    self.thread_lock.release()
                except:
                    print("Can't parse subscription id")
            else:
                try:
                    if response.get("messageType") == "A":
                        print(response.get("data"))
                except:
                    print("Can't parse response")

    def add_ticker(self, ticker):
        '''
        Add ticker to websocket.

        Lock is used to ensure websocket is open and self.sub_id is assigned 
        before adding tickers.
        '''
        self.thread_lock.acquire()

        # Connect to socket and send payload
        ws = create_connection("wss://api.tiingo.com/iex")
        payload = {
            'eventName': 'subscribe',
            'authorization': TIINGO_KEY,
            'eventData': {
                'subscriptionId': self.sub_id,
                'thresholdLevel': 5,
                'tickers': [ticker]
            }
        }
        ws.send(json.dumps(payload))
        print(ws.recv())
        self.thread_lock.release()

    def remove_ticker(self, ticker):
        '''
        Remove ticker from websocket.

        No error if given ticker is not being tracked by websocket.
        '''
        ws = create_connection("wss://api.tiingo.com/iex")
        payload = {
            'eventName': 'unsubscribe',
            'authorization': TIINGO_KEY,
            'eventData': {
                'subscriptionId': self.sub_id,
                'tickers': [ticker]
            }
        }
        ws.send(json.dumps(payload))
        print(ws.recv())


def monitor(tickers):
    '''
    Monitor ticker list from websocket
    '''

    stock_socket = StockSocket()

    # Add tickers to connection
    for ticker in tickers:
        try:
            stock_socket.add_ticker(ticker)
        except:
            print("Cannot add " + ticker)

    time.sleep(3)
    stock_socket.remove_ticker('aapl')


monitor(["spy", "gme"])
