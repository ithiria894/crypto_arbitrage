import requests

def get_binance_us_price(symbol):
    url = "https://api.binance.us/api/v3/ticker/price"
    params = {"symbol": symbol}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data['price']
    return None

def get_binanceus_fees():

    maker_fee = 0.00075  # Maker 0.075%
    taker_fee = 0.001  # Taker 0.1%
    return maker_fee, taker_fee




