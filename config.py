import os


class Config(object):
    """A default config class for the app"""

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
