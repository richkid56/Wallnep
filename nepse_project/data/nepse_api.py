# data/nepse_api.py
import asyncio
from nepse_api import Nepse  # Correct import

nepse = Nepse()

def get_indices():
    try:
        return asyncio.run(nepse.get_indices())
    except Exception as e:
        print("Error fetching indices:", e)
        return None

def get_stocks():
    try:
        return asyncio.run(nepse.get_stocks())
    except Exception as e:
        print("Error fetching stocks:", e)
        return None

def get_live_price(symbol):
    try:
        return asyncio.run(nepse.get_live_price(symbol))
    except Exception as e:
        print(f"Error fetching live price for {symbol}:", e)
        return None

def get_floorsheet():
    try:
        return asyncio.run(nepse.get_floorsheet())
    except Exception as e:
        print("Error fetching floorsheet:", e)
        return None
