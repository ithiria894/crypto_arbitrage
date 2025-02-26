from get_mexc import get_mexc_price, get_mexc_fees
from get_bitget import get_bitget_price, get_bitget_fees
from get_upbit import get_upbit_price, get_upbit_fees
from get_binanceus import get_binance_us_price, get_binanceus_fees

# Function to get prices from all exchanges

def get_prices(symbol):
    mexc_price = float(get_mexc_price(symbol))
    bitget_price = float(get_bitget_price(symbol))
    upbit_price = float(get_upbit_price(f"USDT-{symbol.split('USDT')[0]}"))  
    binanceus_price = float(get_binance_us_price(symbol))
    
    return {
        "MEXC": mexc_price,
        "Bitget": bitget_price,
        "Upbit": upbit_price,
        "BinanceUS": binanceus_price
    }

def get_price_for_exchange(symbol: str, exchange: str):
    """针对单个交易所获取价格"""
    formatted_symbol = format_symbol_for_exchange(symbol, exchange)
    try:
        if exchange == "MEXC":
            return float(get_mexc_price(formatted_symbol))
        elif exchange == "Bitget":
            return float(get_bitget_price(formatted_symbol))
        elif exchange == "Upbit":
            return float(get_upbit_price(formatted_symbol))
        elif exchange == "BinanceUS":
            return float(get_binance_us_price(formatted_symbol))
    except:
        return None
    
def format_symbol_for_exchange(symbol: str, exchange: str) -> str:
    """处理各交易所的符号格式差异"""
    if exchange == "Upbit":
        return f"USDT-{symbol.replace('USDT', '')}"
    return symbol


# Function to get fees from all exchanges
def get_fees():
    mexc_mk, mexc_tk = get_mexc_fees()
    bitget_mk, bitget_tk = get_bitget_fees()
    upbit_mk, upbit_tk = get_upbit_fees()
    binanceus_mk, binanceus_tk = get_binanceus_fees()

    return {
        "MEXC": mexc_tk,
        "Bitget": bitget_tk,
        "Upbit": upbit_tk,
        "BinanceUS": binanceus_tk
    }

# Function to calculate profit from arbitrage
def calculate_profit(capital, prices, fees):
    # Finding the maximum and minimum prices and the corresponding exchanges

    prices = {ex: float(price) for ex, price in prices.items()}
    
    max_price_exchange = max(prices, key=prices.get)
    min_price_exchange = min(prices, key=prices.get)

    max_price = prices[max_price_exchange]
    min_price = prices[min_price_exchange]

    # Getting the taker fee for buying from the minimum price exchange and selling at the maximum price exchange
    buy_fee = fees[min_price_exchange]
    sell_fee = fees[max_price_exchange]

    # Calculating the amount of asset that can be bought with the capital at the minimum price
    buy_amount = capital / min_price

    # Calculating the total amount received after selling at the maximum price and applying both buy and sell fees
    final_amount = buy_amount * max_price * (1 - sell_fee) * (1 - buy_fee)

    # Calculating the profit
    profit = final_amount - capital

    # Calculating the percentage profit
    percentage_profit = (profit / capital) * 100

    return max_price_exchange, max_price, min_price_exchange, min_price, profit, percentage_profit

# Function to print results
def print_results(max_price_exchange, max_price, min_price_exchange, min_price, capital, profit, percentage_profit):
    print(f"Max price exchange: {max_price_exchange} - Price: {max_price}")
    print(f"Min price exchange: {min_price_exchange} - Price: {min_price}")
    print(f"Initial capital: ${capital}")
    print(f"Profit from arbitrage: ${profit}")
    print(f"Percentage profit: {percentage_profit:.2f}%")

def main(symbol="TRUMPUSDT", capital=10000):
    prices = get_prices(symbol)

    # Fetching prices and fees
    prices = get_prices()
    fees = get_fees()

    # Calculating profit and percentage profit
    max_price_exchange, max_price, min_price_exchange, min_price, profit, percentage_profit = calculate_profit(capital, prices, fees)

    # Printing the results
    print_results(max_price_exchange, max_price, min_price_exchange, min_price, capital, profit, percentage_profit)

if __name__ == "__main__":
    main()
