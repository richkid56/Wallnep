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
if indices:
    indices_df = pd.DataFrame(indices)
    st.dataframe(indices_df)
else:
    st.write("Failed to fetch indices data.")

# Floorsheet
st.header("Recent Trades (Floorsheet)")
floorsheet = nepse_api.get_floorsheet()
if floorsheet:
    floorsheet_df = pd.DataFrame(floorsheet).head(20)
    st.dataframe(floorsheet_df)
else:
    st.write("Failed to fetch floorsheet data.")

# Screener
st.header("Stock Screener")
screener_results = screener.screen_stocks()
if screener_results:
    st.subheader("Top Gainers")
    st.dataframe(screener_results["Top Gainers"])
    st.subheader("Top Losers")
    st.dataframe(screener_results["Top Losers"])
    st.subheader("Volume Movers")
    st.dataframe(screener_results["Volume Movers"])
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
summary_df = pd.DataFrame(summary)
st.dataframe(summary_df)

# Check quantity owned for any symbol
st.header("Check Your Holdings")
check_symbol = st.text_input("Enter stock symbol to check your quantity", key="check_qty")

if check_symbol:
    owned_qty = port.get_quantity(check_symbol.upper())
    st.write(f"You currently own {owned_qty} shares of {check_symbol.upper()}")

# Budget to quantity calculator
st.header("Calculate Quantity Based on Budget")
budget_symbol = st.text_input("Enter stock symbol for budget calculation", key="budget_sym")
budget_amount = st.number_input("Enter your budget amount (Rs.)", min_value=0.0, format="%.2f", key="budget_amt")

if budget_symbol and budget_amount > 0:
    live_data = nepse_api.get_live_price(budget_symbol.upper())
    if live_data and 'last_price' in live_data:
        price = float(live_data['last_price'])
        possible_qty = int(budget_amount // price)
        st.write(f"With Rs. {budget_amount:.2f}, you can buy approximately {possible_qty} shares of {budget_symbol.upper()} at Rs. {price:.2f} per share.")
    else:
        st.write("Failed to fetch live price for the symbol.")

# Signal checking for selected stock
st.header("Stock Signal Checker")
stock_for_signal = st.text_input("Enter stock symbol for signals", key="signal_check")

if stock_for_signal:
    live_data = nepse_api.get_live_price(stock_for_signal.upper())
    if live_data and 'last_price' in live_data:
        df = pd.DataFrame({"close": [float(live_data['last_price'])]*50})
        df = signals.generate_signals(df)
        st.line_chart(df[['rsi', 'macd', 'macd_signal', 'ema_short', 'ema_long']])
        latest = df.iloc[-1]
        if latest['buy_signal']:
            st.success("Buy Signal")
            message = f"📈 BUY ALERT:\n{stock_for_signal.upper()} at Rs. {live_data['last_price']}\nRSI: {latest['rsi']:.2f}"
            send_telegram_message(message)
        elif latest['sell_signal']:
            st.error("Sell Signal")
            message = f"📉 SELL ALERT:\n{stock_for_signal.upper()} at Rs. {live_data['last_price']}\nRSI: {latest['rsi']:.2f}"
            send_telegram_message(message)
        else:
            st.info("No clear signal")
    else:
        st.write("Failed to fetch live price for the symbol.")
