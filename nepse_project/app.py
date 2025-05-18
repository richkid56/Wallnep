import streamlit as st
import pandas as pd
from data import nepse_api
from analysis import screener, signals
from portfolio import tracker

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

# Signal checking for selected stock
st.header("Stock Signal Checker")
stock_for_signal = st.text_input("Enter stock symbol for signals")

if stock_for_signal:
    live_data = nepse_api.get_live_price(stock_for_signal.upper())
    if live_data and 'last_price' in live_data:
        # Prepare DataFrame with historical close prices
        # For demo, just replicate last price multiple times
        df = pd.DataFrame({"close": [float(live_data['last_price'])]*50})
        df = signals.generate_signals(df)
        st.line_chart(df[['rsi', 'macd', 'macd_signal', 'ema_short', 'ema_long']])
        latest = df.iloc[-1]
        if latest['buy_signal']:
            st.success("Buy Signal")
        elif latest['sell_signal']:
            st.error("Sell Signal")
        else:
            st.info("No clear signal")
    else:
        st.write("Failed to fetch live price for the symbol.")