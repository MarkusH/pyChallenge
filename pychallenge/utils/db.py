import sqlite3
from pychallenge.utils import settings

db = sqlite3.connect(settings.SETTINGS['DATABASE'])

