# get_mexc.py
from dotenv import load_dotenv
import os
from mexc_sdk import Spot

def get_mexc_price(symbol):

    load_dotenv()


    mexc_api_key = os.getenv('MEXC_API_KEY')
    mexc_api_secret = os.getenv('MEXC_API_SECRET')


    spot = Spot(api_key=mexc_api_key, api_secret=mexc_api_secret)


    ticker = spot.ticker_price(symbol=symbol)

    return ticker.get('price')


def get_mexc_fees():

    maker_fee = 0.0008  # Maker 0.08%
    taker_fee = 0.001  # Taker 0.1%
    return maker_fee, taker_fee
