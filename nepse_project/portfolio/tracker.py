import pandas as pd
from data import nepse_api

class Portfolio:
    def __init__(self):
        self.holdings = {}

    def add_stock(self, symbol, quantity, avg_price):
        if symbol in self.holdings:
            current = self.holdings[symbol]
            total_qty = current['quantity'] + quantity
            total_cost = current['quantity'] * current['avg_price'] + quantity * avg_price
            avg_price_new = total_cost / total_qty
            self.holdings[symbol] = {'quantity': total_qty, 'avg_price': avg_price_new}
        else:
            self.holdings[symbol] = {'quantity': quantity, 'avg_price': avg_price}

    def remove_stock(self, symbol, quantity):
        if symbol in self.holdings:
            current = self.holdings[symbol]
            new_qty = current['quantity'] - quantity
            if new_qty <= 0:
                del self.holdings[symbol]
            else:
                self.holdings[symbol]['quantity'] = new_qty

    def get_portfolio_value(self):
        total_value = 0
        for symbol, info in self.holdings.items():
            live_data = nepse_api.get_live_price(symbol)
            if live_data and 'last_price' in live_data:
                total_value += info['quantity'] * float(live_data['last_price'])
        return total_value

    def get_unrealized_pnl(self):
        total_cost = 0
        total_value = 0
        for symbol, info in self.holdings.items():
            total_cost += info['quantity'] * info['avg_price']
            live_data = nepse_api.get_live_price(symbol)
            if live_data and 'last_price' in live_data:
                total_value += info['quantity'] * float(live_data['last_price'])
        return total_value - total_cost

    def summary(self):
        summary_list = []
        for symbol, info in self.holdings.items():
            live_data = nepse_api.get_live_price(symbol)
            last_price = float(live_data['last_price']) if live_data and 'last_price' in live_data else None
            pnl = None
            if last_price is not None:
                pnl = (last_price - info['avg_price']) * info['quantity']
            summary_list.append({
                'symbol': symbol,
                'quantity': info['quantity'],
                'avg_price': info['avg_price'],
                'last_price': last_price,
                'unrealized_pnl': pnl
            })
        return summary_list