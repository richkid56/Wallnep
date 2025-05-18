import streamlit as st
import pandas as pd
import requests
from data import nepse_api
from analysis import screener, signals
from portfolio import tracker

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

# Show indices
st.header("Market Indices")
indices = nepse_api.get_indices()
if indices and isinstance(indices, dict) and 'data' in indices:
    # Depending on API structure, adjust this
    indices_df = pd.DataFrame(indices['data'])
    st.dataframe(indices_df)
else:
    st.write("Failed to fetch indices data.")

# Floorsheet
st.header("Recent Trades (Floorsheet)")
floorsheet = nepse_api.get_floorsheet()
if floorsheet and isinstance(floorsheet, dict) and 'data' in floorsheet:
    floorsheet_df = pd.DataFrame(floorsheet['data']).head(20)
    st.dataframe(floorsheet_df)
else:
    st.write("Failed to fetch floorsheet data.")

# Screener
st.header("Stock Screener")
stocks = nepse_api.get_stocks()
if stocks and isinstance(stocks, dict) and 'data' in stocks:
    stocks_df = pd.DataFrame(stocks['data'])
    # Example screener filters: top gainers, top losers, volume movers
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
    st.write("Failed to fetch stock data for screener.")

# Portfolio
st.header("My Portfolio")
port = tracker.Portfolio()

with st.form(key='portfolio_form'):
    symbol = st.text_input("Stock Symbol (e.g., NABIL)")
    quantity = st.number_input("Quantity", min_value=1, step=1)
    avg_price = st.number_input("Average Price", min_value=0.0, format="%.2f")
    submit = st.form_submit_button("Add/Update Stock")

if submit and symbol:
    port.add_stock(symbol.upper(), quantity, avg_price)
    st.success(f"Added/Updated {symbol.upper()} in portfolio.")

summary = port.summary()
if summary:
    summary_df = pd.DataFrame(summary)
    st.dataframe(summary_df)
else:
    st.write("Portfolio is empty.")

# Signal checking for selected stock
st.header("Stock Signal Checker")
stock_for_signal = st.text_input("Enter stock symbol for signals")

if stock_for_signal:
    live_data = nepse_api.get_live_price(stock_for_signal.upper())
    if live_data and isinstance(live_data, dict) and 'data' in live_data and 'last_price' in live_data['data']:
        last_price = float(live_data['data']['last_price'])
        df = pd.DataFrame({"close": [last_price]*50})  # Dummy historical data for demo
        df = signals.generate_signals(df)
        st.line_chart(df[['rsi', 'macd', 'macd_signal', 'ema_short', 'ema_long']])
        latest = df.iloc[-1]
        if latest['buy_signal']:
            st.success("Buy Signal")
            message = f"📈 BUY ALERT:\n{stock_for_signal.upper()} at Rs. {last_price}\nRSI: {latest['rsi']:.2f}"
            send_telegram_message(message)
        elif latest['sell_signal']:
            st.error("Sell Signal")
            message = f"📉 SELL ALERT:\n{stock_for_signal.upper()} at Rs. {last_price}\nRSI: {latest['rsi']:.2f}"
            send_telegram_message(message)
        else:
            st.info("No clear signal")
    else:
        st.write("Failed to fetch live price for the symbol.")
