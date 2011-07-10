# -*- coding: utf-8 -*-
import sqlite3
from pychallenge.conf import settings


connection = sqlite3.connect(settings.SETTINGS['DATABASE'])
db = connection.cursor()
