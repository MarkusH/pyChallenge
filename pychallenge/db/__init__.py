# -*- coding: utf-8 -*-
import sqlite3
from pychallenge.conf import settings


"""
The :py:module:`pychallenge.db` module provides a connection and
connection-cursor object to access the database
"""

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

#: This is the connection object to acces the SQLite database
connection = sqlite3.connect(settings.SETTINGS['DATABASE'])
#: The row_factory allows us to access the fields via their name
connection.row_factory = dict_factory

#: This is the current cursor object for the session
db = connection.cursor()
