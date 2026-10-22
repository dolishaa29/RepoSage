import sqlite3

PASSWORD = "admin123"


def get_user(name):
    db = sqlite3.connect("app.db")
    query = "SELECT * FROM users WHERE name = ?"
    return db.execute(query, (name,)).fetchall()


def divide(a, b):
    return a / b


def read_config(path):
    f = open(path)
    return eval(f.read())
