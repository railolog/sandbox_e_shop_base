import sqlite3
from test import spph
from time import *
import datetime


class DB:
    def __init__(self, type):
        d = {'users': 'users.db', 'goods': 'goods.db', 'orders': 'orders.db'}
        conn = sqlite3.connect(d[type], check_same_thread=False)
        self.conn = conn

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()


class UsersModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             user_name VARCHAR(50),
                             password_hash VARCHAR(128),
                             is_admin VARCHAR(10)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, password_hash, is_admin=False):
        cursor = self.connection.cursor()
        password_hash = spph(password_hash)
        cursor.execute('''INSERT INTO users
                          (user_name, password_hash, is_admin)
                          VALUES (?,?,?)''', (user_name, password_hash,
                                              str(is_admin)))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (str(user_id)))
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows

    def exists(self, user_name, password_hash):
        cursor = self.connection.cursor()
        password_hash = spph(password_hash)
        cursor.execute("SELECT * FROM users WHERE user_name = ? AND password_hash = ?",
                       (user_name, password_hash))
        row = cursor.fetchone()
        return (True, row[0], row[3]) if row else (False,)


class GoodsModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS goods
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             type VARCHAR(50),
                             name VARCHAR(128),
                             description VARCHAR(512),
                             price INTEGER,
                             date INTEGER
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, type, name, description, price):
        cursor = self.connection.cursor()
        cursor.execute(
                        '''INSERT INTO goods
                           (type, name, description, price, date)
                           VALUES (?,?,?,?,?)''', (type, name, description,
                                                   price, time())
                      )
        cursor.close()
        self.connection.commit()

    def get(self, id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM goods WHERE id = ?", (int(id), ))
        good = cursor.fetchone()
        return good

    def get_by_type(self, type):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM goods WHERE type = ?", (type,))
        goods = cursor.fetchall()
        return goods

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM goods")
        goods = cursor.fetchall()
        return goods

    def delete(self, goods_id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM goods WHERE id = ?", (goods_id,))
        cursor.close()
        self.connection.commit()


class OrdersModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS orders
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             goods_id INTEGER,
                             user_id INTEGER,
                             status VARCHAR(128),
                             price INTEGER,
                             count INTEGER,
                             cost INTEGER,
                             date VARCHAR(128)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, goods_id, user_id, price, count):
        cursor = self.connection.cursor()
        args = (int(goods_id), int(user_id), 'Формируется к отправке',
                int(price), int(count), int(price) * int(count),
                str(datetime.datetime.now()).split('.')[0])
        cursor.execute(
                        '''INSERT INTO orders
                           (goods_id, user_id, status, price, count, cost, date)
                           VALUES (?,?,?,?,?,?,?)''', args
                      )
        cursor.close()
        self.connection.commit()

    def change_status(self, id, new_stat):
        cursor = self.connection.cursor()
        cursor.execute("UPDATE orders SET status = ? WHERE id = ?",
                       (new_stat, int(id)))

    def get(self, id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (int(id),))
        orders = cursor.fetchone()
        return orders

    def get_by_user(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM orders WHERE user_id = ?",
                       (int(user_id),))
        orders = cursor.fetchall()
        return orders

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM orders")
        orders = cursor.fetchall()
        return orders

    def delete(self, id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM orders WHERE id = ?", (int(id),))
        cursor.close()
        self.connection.commit()
