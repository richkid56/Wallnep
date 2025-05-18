import pandas as pd
from data import nepse_api

def top_gainers(data, n=10):
    df = pd.DataFrame(data)
    df['change'] = pd.to_numeric(df['change'], errors='coerce')
    return df.sort_values(by='change', ascending=False).head(n)

def top_losers(data, n=10):
    df = pd.DataFrame(data)
    df['change'] = pd.to_numeric(df['change'], errors='coerce')
    return df.sort_values(by='change').head(n)

def volume_spike(data, volume_threshold):
    df = pd.DataFrame(data)
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
    return df[df['volume'] > volume_threshold]

def screen_stocks():
    data = nepse_api.get_all_stocks()
    if data:
        gainers = top_gainers(data)
        losers = top_losers(data)
        volume_movers = volume_spike(data, volume_threshold=10000)
        return {
            "Top Gainers": gainers,
            "Top Losers": losers,
            "Volume Movers": volume_movers
        }
    return {}