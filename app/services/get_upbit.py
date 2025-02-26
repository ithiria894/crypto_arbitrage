# upbit.py
import requests

def get_upbit_price(symbol):

    url = "https://api.upbit.com/v1/ticker"
    params = {"markets": symbol}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]['trade_price']
    return None

def get_upbit_fees():

    maker_fee = 0.0005  # Maker 0.05%
    taker_fee = 0.0007  # Taker 0.07%
    return maker_fee, taker_fee