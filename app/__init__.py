import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os


from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel


from config import Config


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()
babel = Babel()


def create_app(config_class=Config):
    """Create and return a new app"""

    # Create a new app and get configurations
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Register other app related objects with the app
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)

    # Register blueprints
    from app.errors import bp as bp_errors
    app.register_blueprint(bp_errors)

    from app.auth import bp as bp_auth
    app.register_blueprint(bp_auth, url_prefix='/auth')

    from app.main import bp as bp_main
    app.register_blueprint(bp_main)

    # Logging
    if not app.debug:

        # Mail handler
        if app.config['MAIL_SERVER']:
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()

            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])

            mail_handler = SMTPHandler(mailhost=(app.config['MAIL_SERVER'],
                                                 app.config['MAIL_PORT']),
                                       fromaddr='no_reply@' +
                                                app.config['MAIL_SERVER'],
                                       toaddrs=app.config['ADMINS'],
                                       subject='Microblog Failure',
                                       credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        # Rotating file handler
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s %(levelname)s: %(message)s '
                              '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')

    return app


from app import models


@babel.localeselector
def get_locale():
    """A locale selector to be registered with the babel object"""

    return request.accept_languages.best_match(current_app.config['LANGUAGES'])
