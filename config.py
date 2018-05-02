import os
from dotenv import load_dotenv


base_dir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(base_dir, '.env'))


class Config(object):
    """A default config class for the app"""

    SECRET_KEY = os.environ.get('SECRET_KEY')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(base_dir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = os.environ.get('MAIL_PORT') or 25
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['gongwei619@hotmail.com']
    NOREPLY = 'no-reply@ourchatroom.com'

    POSTS_PER_PAGE = 5

    LANGUAGES = ['en', 'zh']

    MS_TRANSLATION_KEY = os.environ.get('MS_TRANSLATION_KEY')

    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')

    UPLOADS_URL = os.path.join(base_dir, 'uploads')
