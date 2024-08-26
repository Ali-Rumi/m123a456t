from binance.um_futures import UMFutures
from binance.error import ClientError
import math

# API credentials
api_key = 'FOfIYCxqYfKRHBCcT4j9xJjkMa1IL7tkMpvSqOcPrlllIpvt59YjVkpgyoZbr7rS'
api_secret = 'KOsx97evpt2etVZxpZzq1VKlzPOekTR67WASawHz04rmfesUoPNCZJ1f3QT9bdPU'

# Initialize the UMFutures client
client = UMFutures(key=api_key, secret=api_secret)

# Trading parameters
symbol = 'MATICUSDT'
usdt_amount = 2.5
leverage = 20
take_profit_percent = 0.4
stop_loss_percent = 0.4

def get_symbol_info(symbol):
    exchange_info = client.exchange_info()
    for s in exchange_info['symbols']:
        if s['symbol'] == symbol:
            return s
    raise ValueError(f"Symbol {symbol} not found")

def round_step_size(quantity, step_size):
    precision = int(round(-math.log(step_size, 10), 0))
    return round(quantity, precision)

def place_short_trade():
    try:
        # Get symbol information
        symbol_info = get_symbol_info(symbol)
        quantity_precision = next(filter(lambda f: f['filterType'] == 'LOT_SIZE', symbol_info['filters']))['stepSize']
        price_precision = next(filter(lambda f: f['filterType'] == 'PRICE_FILTER', symbol_info['filters']))['tickSize']

        # Set leverage
        client.change_leverage(symbol=symbol, leverage=leverage)

        # Get current market price
        ticker = client.ticker_price(symbol)
        entry_price = float(ticker['price'])

        # Calculate quantity based on USDT amount and leverage
        quantity = (usdt_amount * leverage) / entry_price
        rounded_quantity = round_step_size(quantity, float(quantity_precision))

        # Calculate take profit and stop loss prices
        take_profit_price = round_step_size(entry_price * (1 - take_profit_percent / 100), float(price_precision))
        stop_loss_price = round_step_size(entry_price * (1 + stop_loss_percent / 100), float(price_precision))

        # Place market order to open short position
        order = client.new_order(
            symbol=symbol,
            side="SELL",
            type="MARKET",
            quantity=rounded_quantity
        )

        # Place take profit order
        tp_order = client.new_order(
            symbol=symbol,
            side="BUY",
            type="TAKE_PROFIT_MARKET",
            timeInForce="GTC",
            quantity=rounded_quantity,
            stopPrice=take_profit_price,
            workingType="MARK_PRICE"
        )

        # Place stop loss order
        sl_order = client.new_order(
            symbol=symbol,
            side="BUY",
            type="STOP_MARKET",
            timeInForce="GTC",
            quantity=rounded_quantity,
            stopPrice=stop_loss_price,
            workingType="MARK_PRICE"
        )

        print(f"Short position opened for {symbol}")
        print(f"Entry Price: {entry_price}")
        print(f"Quantity: {rounded_quantity}")
        print(f"Take Profit Price: {take_profit_price}")
        print(f"Stop Loss Price: {stop_loss_price}")

    except ClientError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    place_short_trade()
    
