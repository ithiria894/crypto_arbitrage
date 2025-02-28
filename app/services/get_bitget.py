# get_bitget.py
import requests

def get_bitget_price(symbol="SNEKUSDT"):
    """
    
    return sample:
    {
        "symbol": "BTCUSDT",
        "lastPr": "34413.1",
        "high24h": "37775.65",
        "low24h": "34413.1",
        "open": "35134.2",
        "quoteVolume": "0",
        "baseVolume": "0",
        "usdtVolume": "0",
        "bidPr": "0",
        "askPr": "0"
    }
    """
    url = f"https://api.bitget.com/api/v2/spot/market/tickers?symbol={symbol}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        result = response.json()
        if result.get("code") == "00000" and "data" in result and len(result["data"]) > 0:
            ticker = result["data"][0]
            # Print the last price
            # Print the last price

            # print(f"Symbol: {ticker.get('symbol')}")
            # print(f"Symbol: {ticker.get('symbol')}")
            # print(f"Last Price: {ticker.get('lastPr')}")
            # print(f"Last Price: {ticker.get('lastPr')}")
            return ticker.get('lastPr')
        else:
            print("Bitget Spot API error:", result.get("msg"))
            return None
    except Exception as e:
        print("Error occurred while fetching Bitget spot market data:", e)
        return None
    
def get_bitget_fees():

    maker_fee = 0.0006  # Maker 0.06%
    taker_fee = 0.0008  # Taker 0.08%
    return maker_fee, taker_fee