import os
import requests
import pandas as pd
import numpy as np
import talib
import telegram
import datetime

# Initialize Telegram Client with environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Function to fetch market data from CoinGecko
def fetch_market_data(symbol, days):
    url = f'https://api.coingecko.com/api/v3/coins/{symbol}/market_chart?vs_currency=usd&days={days}&interval=minute'
    response = requests.get(url)
    data = response.json()
    prices = data['prices']
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

# Function to generate trading signals based on simple moving average cross strategy
def generate_signals(df):
    df['SMA_50'] = talib.SMA(df['price'], timeperiod=50)
    df['SMA_200'] = talib.SMA(df['price'], timeperiod=200)
    df['signal'] = np.where(df['SMA_50'] > df['SMA_200'], 'buy', 'sell')
    return df

# Function to send signals to Telegram
def send_telegram_message(message):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

# Main function to check for signals and send to Telegram
def main():
    interval_days = 1  # Analyze data from the last day
    symbols = ['bitcoin', 'ethereum', 'binancecoin', 'cardano', 'solana']  # List of symbols to analyze

    for symbol in symbols:
        df = fetch_market_data(symbol, interval_days)
        signals_df = generate_signals(df)
        latest_signal = signals_df.iloc[-1]['signal']
        last_close = df.iloc[-1]['price']

        if latest_signal == 'buy':
            stop_loss = last_close * 0.99
            take_profit = last_close * 1.02
            message = f"Buy Signal for {symbol}\nPrice: {last_close}\nStop Loss: {stop_loss}\nTake Profit: {take_profit}\nTime: {datetime.datetime.now()}"
            send_telegram_message(message)
        elif latest_signal == 'sell':
            stop_loss = last_close * 1.01
            take_profit = last_close * 0.98
            message = f"Sell Signal for {symbol}\nPrice: {last_close}\nStop Loss: {stop_loss}\nTake Profit: {take_profit}\nTime: {datetime.datetime.now()}"
            send_telegram_message(message)

if __name__ == "__main__":
    main()
