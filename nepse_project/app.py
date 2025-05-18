import streamlit as st
import pandas as pd
import requests
from data import nepse_api

# Telegram setup
TELEGRAM_TOKEN = "8163503683:AAEyo-rQN_6L2iYbxqix_ki0nebuLyvYbmQ"
TELEGRAM_CHAT_ID = "7902946050"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram error:", e)

st.set_page_config(page_title="NEPSE Live Dashboard", layout="wide")
st.title("NEPSE Live Market Dashboard")

# Market Indices
st.header("Market Indices")
indices = nepse_api.get_indices()
if indices and 'data' in indices:
    indices_df = pd.DataFrame(indices['data'])
    st.dataframe(indices_df)
else:
    st.write("Failed to fetch indices data.")

# Floorsheet
st.header("Recent Trades (Floorsheet)")
floorsheet = nepse_api.get_floorsheet()
if floorsheet and 'data' in floorsheet:
    floorsheet_df = pd.DataFrame(floorsheet['data']).head(20)
    st.dataframe(floorsheet_df)
else:
    st.write("Failed to fetch floorsheet data.")

# Stock Screener
st.header("Stock Screener")
stocks = nepse_api.get_stocks()
if stocks and 'data' in stocks:
    stocks_df = pd.DataFrame(stocks['data'])
    # Sort top gainers, losers, volume movers
    top_gainers = stocks_df.sort_values(by='percent_change', ascending=False).head(10)
    top_losers = stocks_df.sort_values(by='percent_change').head(10)
    volume_movers = stocks_df.sort_values(by='volume', ascending=False).head(10)

    st.subheader("Top Gainers")
    st.dataframe(top_gainers)

    st.subheader("Top Losers")
    st.dataframe(top_losers)

    st.subheader("Volume Movers")
    st.dataframe(volume_movers)
else:
    st.write("Failed to fetch stock data.")

# Live Price Checker and Basic Alert
st.header("Live Price Checker")
stock_symbol = st.text_input("Enter Stock Symbol (e.g., NABIL)").upper()

if stock_symbol:
    live_data = nepse_api.get_live_price(stock_symbol)
    if live_data and 'data' in live_data and 'last_price' in live_data['data']:
        last_price = float(live_data['data']['last_price'])
        st.write(f"Current price of {stock_symbol}: Rs. {last_price}")
        
        # Example: Simple alert if price is above some threshold (adjust as needed)
        # You can build your own conditions here for buy/sell signals
        if last_price > 1000:  # example threshold
            message = f"🚨 Alert: {stock_symbol} price is Rs. {last_price}"
            send_telegram_message(message)
            st.success("Telegram alert sent!")
    else:
        st.write("Failed to fetch live price for the symbol.")
