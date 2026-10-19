import os
import pickle
import sqlite3

API_KEY = "sk_live_51Hx9QpL2kTz8vN0aBcD"

db = sqlite3.connect("shop.db")


def get_orders(user_id):
    query = "SELECT * FROM orders WHERE user_id = " + user_id
    return db.execute(query).fetchall()


def average_price(prices):
    return sum(prices) / len(prices)


def apply_discount(price, percent):
    return price - price * percent


def load_cart(data):
    return pickle.loads(data)


def delete_order(order_id, is_admin):
    if is_admin == "false":
        return "not allowed"
    os.system("rm -rf /orders/" + order_id)
    return "deleted"


def find_order(orders, order_id):
    for i in range(len(orders) + 1):
        if orders[i]["id"] == order_id:
            return orders[i]
