import pandas as pd

def EMA(series, span):
    return series.ewm(span=span, adjust=False).mean()

def RSI(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def MACD(series, span_short=12, span_long=26, span_signal=9):
    ema_short = EMA(series, span_short)
    ema_long = EMA(series, span_long)
    macd_line = ema_short - ema_long
    signal_line = EMA(macd_line, span_signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram