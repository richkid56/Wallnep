import requests

BASE_URL = "https://nepse-data-api.herokuapp.com/api/v1"

def get_indices():
    url = f"{BASE_URL}/indices"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("Error fetching indices:", e)
    return None

def get_floorsheet():
    url = f"{BASE_URL}/floorsheet"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("Error fetching floorsheet:", e)
    return None

def get_stocks():
    url = f"{BASE_URL}/stocks"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("Error fetching stocks:", e)
    return None

def get_live_price(symbol):
    # The API doesn’t provide single live price endpoint, so filter from all stocks
    stocks_data = get_stocks()
    if stocks_data and "data" in stocks_data:
        for stock in stocks_data["data"]:
            if stock.get("symbol", "").upper() == symbol.upper():
                return {
                    "data": {
                        "last_price": stock.get("close", None)
                    }
                }
    return None
