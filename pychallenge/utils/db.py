import sqlite3
from pychallenge.utils import settings


connection = sqlite3.connect(settings.SETTINGS['DATABASE'])
db = connection.cursor()

