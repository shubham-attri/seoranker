"""
This page contains functions and classes related to database operations
"""

import sqlite3


def connect_db():
    conn = sqlite3.connect('scraped.db')
    c = conn.cursor()
    return c, conn

def create_table(c):
    c.execute('''CREATE TABLE IF NOT EXISTS scraped
                 (url text PRIMARY KEY, markdown text, h1 text)''')
