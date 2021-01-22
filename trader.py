import json
from websocket import create_connection
import requests
import os
from dotenv import load_dotenv
import threading
import ast
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import uuid
from tqdm import tqdm


load_dotenv()

AV_KEY = os.getenv("ALPHA_VANTAGE_KEY")
AV_BASE_URL = f"https://www.alphavantage.co/query?apikey={AV_KEY}"

TIINGO_KEY = os.getenv("TIINGO_KEY")
TIINGO_WEBSOCKET_URL = "wss://api.tiingo.com/iex"
TIINGO_REST_URL = f"https://api.tiingo.com/iex/?token={TIINGO_KEY}&tickers="


class Stock:
    '''
    Used to hold and gather data about given ticker
    '''

    def __init__(self, ticker):
        self.ticker = ticker

        # Get latest stock prices
        self.update()

    def __request_builder(self, args_map):
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
        request_url = self.__request_builder(request_args)
        print(request_url)

        data = requests.get(request_url).json()
        return data

    def price_daily(self, num_days=100):
        '''
        Return num_days of daily prices in dataframe.
        '''
        if num_days > 100:
            size = "full"
        else:
            size = "compact"

        request_args = {
            "function": "TIME_SERIES_DAILY_ADJUSTED", "outputsize": size}
        request_url = self.__request_builder(request_args)
        res = requests.get(request_url).json()
        date = []
        colnames = list(range(0, 7))
        df = pd.DataFrame(columns=colnames)
        print("Parsing data into a dataframe...")
        trimmed_data = dict(
            list(res['Time Series (Daily)'].items())[:num_days])
        for i in tqdm(trimmed_data.keys()):
            date.append(i)
            row = pd.DataFrame.from_dict(
                trimmed_data[i], orient='index').reset_index().T[1:]
            df = pd.concat([df, row], ignore_index=True)
        df.columns = ["open", "high", "low", "close",
                      "adjusted close", "volume", "dividend amount", "split cf"]
        df['date'] = date
        return df

    def update(self):
        '''
        Get current ticker prices and update instance
        '''
        req_url = TIINGO_REST_URL + self.ticker
        headers = {
            'Content-Type': 'application/json'
        }
        res = ((requests.get(req_url, headers)).json())[0]
        self.high = res.get("high")
        self.low = res.get("low")
        self.last_price = res.get("last")
        self.last_size = res.get("lastSize")
        self.bid_price = res.get("bidPrice")
        self.bid_size = res.get("bidSize")
        self.ask_price = res.get("askPrice")
        self.ask_price = res.get("askSize")
        return res

    def moving_avg(self, window, age=20):
        '''
        Compute moving average given WINDOW.
        Window: 5,10,30,60min. 1,2,5,10,20day.

        Output array of moving averages from now to AGE samples back.
        '''
        id = str(uuid.uuid4())

        return

    def moving_avg_crossover(self):
        long_term_data = self.price_daily(100)

        # long_term_data.plot.scatter(x="date", y="close")
        plt.plot(long_term_data["date"],
                 long_term_data["close"])
        plt.show()
        return


x = Stock("aapl")
x.update()
x.moving_avg_crossover()


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
        ws = create_connection(TIINGO_BASE_URL)
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
            # If opening connection, assign self.sub_id for future reference
            if self.sub_id is None:
                try:
                    sub_id = response.get(
                        "data").get("subscriptionId")
                    self.sub_id = sub_id
                    self.thread_lock.release()
                    print("WebSocket Connected")
                except:
                    print("Can't parse subscription id")
            else:
                try:
                    # Parse price updates and append to self.tickers[ticker]
                    if response.get("messageType") == "A":
                        data = response.get("data")
                        if data[0] == "Q":
                            trade_price = data[7]
                            trade_size = data[8]
                        else:
                            trade_price = data[9]
                            trade_size = data[10]
                        ticker = data[3]
                        timestamp = data[1]

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
        ws = create_connection(TIINGO_BASE_URL)
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
        print(f"Added {ticker}")
        self.tickers[ticker] = Stock(ticker)
        self.thread_lock.release()

    def remove_ticker(self, ticker):
        '''
        Remove ticker from websocket.

        No error if given ticker is not being tracked by websocket.
        '''
        ws = create_connection(TIINGO_BASE_URL)
        payload = {
            'eventName': 'unsubscribe',
            'authorization': TIINGO_KEY,
            'eventData': {
                'subscriptionId': self.sub_id,
                'tickers': [ticker]
            }
        }
        ws.send(json.dumps(payload))
        print(f"Removed {ticker}")


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


# monitor(["spy", "avgo", "c", "dis", "gpro", "nvda", "pfe", "pltr", "gme"])
