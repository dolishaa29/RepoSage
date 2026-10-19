import os
import sqlite3

PASSWORD = os.getenv("PASSWORD")


def get_user(name):
    db = sqlite3.connect("app.db")
    query = f"SELECT * FROM users WHERE name = '{name}'"
    return db.execute(query).fetchall()


def divide(a, b):
    return a / b


def read_config(path):
    f = open(path)
    return eval(f.read())
