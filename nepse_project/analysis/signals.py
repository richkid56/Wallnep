import pandas as pd
from analysis.indicators import RSI, MACD, EMA

RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

EMA_SHORT_SPAN = 12
EMA_LONG_SPAN = 26

def generate_signals(df):
    """
    Input: df with 'close' price column
    Output: df with 'buy_signal' and 'sell_signal' columns
    """
    close = df['close']

    df['rsi'] = RSI(close)
    macd_line, signal_line, _ = MACD(close)
    df['macd'] = macd_line
    df['macd_signal'] = signal_line

    df['ema_short'] = EMA(close, EMA_SHORT_SPAN)
    df['ema_long'] = EMA(close, EMA_LONG_SPAN)

    df['buy_signal'] = ((df['rsi'] < RSI_OVERSOLD) &
                        (df['macd'] > df['macd_signal']) &
                        (df['ema_short'] > df['ema_long']))

    df['sell_signal'] = ((df['rsi'] > RSI_OVERBOUGHT) &
                         (df['macd'] < df['macd_signal']) &
                         (df['ema_short'] < df['ema_long']))

    return df