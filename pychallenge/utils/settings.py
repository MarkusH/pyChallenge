from os.path import dirname, join

BASE_PATH = dirname(__file__)

SETTINGS = {
    'BASE_PATH': BASE_PATH,
    'DATABASE': join(BASE_PATH, '..', '..', 'data.db'),
    'DEBUG': False,
}


def load_settings():
    """
    :func:`load_settings` initializes the default settings and reads
    the user settings as well.
    """
    try:
        from pychallenge import usersettings as us
        for s in us.__all__:
            SETTINGS[s] = getattr(us, s)
    except ImportError:
        pass

load_settings()
