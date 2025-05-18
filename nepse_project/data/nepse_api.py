import requests

BASE_URL = "https://nepse-data-api.onrender.com"

def get_live_price(symbol):
    url = f"{BASE_URL}/price/{symbol}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def get_all_stocks():
    url = f"{BASE_URL}/stocks"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def get_indices():
    url = f"{BASE_URL}/indices"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def get_floorsheet():
    url = f"{BASE_URL}/floorsheet"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None