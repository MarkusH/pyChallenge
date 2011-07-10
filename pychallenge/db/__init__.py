# -*- coding: utf-8 -*-
import sqlite3
from pychallenge.conf import settings


"""
The :py:module:`pychallenge.db` module provides a connection and
connection-cursor object to access the database
"""

#: This is the connection object to acces the SQLite database
connection = sqlite3.connect(settings.SETTINGS['DATABASE'])

#: This is the current cursor object for the session
db = connection.cursor()
