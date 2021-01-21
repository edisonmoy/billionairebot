import requests
import os
from dotenv import load_dotenv

load_dotenv()

AV_KEY = os.getenv("ALPHA_VANTAGE_KEY")
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


a = StockData("MSFT")
print(a.price_five_min())
