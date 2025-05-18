import streamlit as st
import pandas as pd
import requests
import math
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

# Stock Signal Checker with budget input
st.header("Stock Signal Checker")
stock_for_signal = st.text_input("Enter stock symbol for signals")
budget = st.number_input("Enter your budget for buying (NPR)", min_value=0.0, format="%.2f", step=100)

if stock_for_signal:
    live_data = nepse_api.get_live_price(stock_for_signal.upper())
    if live_data and 'last_price' in live_data:
        df = pd.DataFrame({"close": [float(live_data['last_price'])]*50})
        df = signals.generate_signals(df)
        st.line_chart(df[['rsi', 'macd', 'macd_signal', 'ema_short', 'ema_long']])
        latest = df.iloc[-1]

        rsi = latest['rsi']
        current_price = float(live_data['last_price'])
        owned_quantity = port.get_quantity(stock_for_signal.upper())

        if rsi < 30:
            st.success("Buy Signal")
            quantity_to_buy = math.floor(budget / current_price) if budget > 0 else 0
            message = (
                f"📈 BUY ALERT\n"
                f"Stock: {stock_for_signal.upper()}\n"
                f"Price: Rs. {current_price}\n"
                f"RSI: {rsi:.2f} (Oversold)\n\n"
                f"Based on your budget of Rs. {budget:.2f}, you can buy approximately {quantity_to_buy} shares.\n\n"
                "What does this mean?\n"
                "- RSI below 30 means the stock is oversold.\n"
                "- It might be undervalued right now.\n\n"
                "What should you do?\n"
                "- Consider buying this stock now.\n"
                "- Watch price closely for confirmation.\n"
                "- Don’t invest more than you can afford to lose."
            )
            send_telegram_message(message)

        elif rsi > 70:
            st.error("Sell Signal")
            message = (
                f"📉 SELL ALERT\n"
                f"Stock: {stock_for_signal.upper()}\n"
                f"Price: Rs. {current_price}\n"
                f"RSI: {rsi:.2f} (Overbought)\n\n"
                f"You currently own {owned_quantity} shares.\n\n"
                "What does this mean?\n"
                "- RSI above 70 means the stock is overbought.\n"
                "- The price might drop soon.\n\n"
                "What should you do?\n"
                "- Consider selling or taking profit.\n"
                "- Keep an eye on market news.\n"
                "- Avoid panic selling; wait for clear drop if unsure."
            )
            send_telegram_message(message)

        else:
            st.info("Hold Signal")
            message = (
                f"ℹ️ HOLD\n"
                f"Stock: {stock_for_signal.upper()}\n"
                f"Price: Rs. {current_price}\n"
                f"RSI: {rsi:.2f} (Neutral)\n\n"
                "What does this mean?\n"
                "- RSI between 30 and 70 means no strong signal.\n"
                "- The stock price is stable or uncertain.\n\n"
                "What should you do?\n"
                "- Wait for clearer signal before buying or selling.\n"
                "- Monitor stock trends regularly.\n"
                "- Patience is key in stock trading."
            )
            send_telegram_message(message)

    else:
        st.write("Failed to fetch live price for the symbol.")
