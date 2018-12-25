from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
import logging
from logging.handlers import RotatingFileHandler
import os


# This import with give me the missingMySQLdb python object
import pymysql
pymysql.install_as_MySQLdb()


# Manage environment variables, etc.
login = LoginManager()
login.login_view = 'auth.login'
mail = Mail()
bootstrap = Bootstrap()

# Create the DB engine object, which gives me access to the session later
db = SQLAlchemy()


def create_app(config_class=Config):
    team9 = Flask(__name__)
    team9.config.from_object(config_class)


    db.init_app(team9)
    with team9.app_context():
        db.Model.metadata.reflect(db.engine, views=True)

    login.init_app(team9)
    bootstrap.init_app(team9)
    mail.init_app(team9)

    # Manage blueprints
    from team9.errors import bp as errors_bp
    team9.register_blueprint(errors_bp)

    from team9.auth import bp as auth_bp
    team9.register_blueprint(auth_bp, url_prefix='/auth')

    from team9.main import bp as main_bp
    team9.register_blueprint(main_bp)

    from team9.admin import bp as admin_bp
    team9.register_blueprint(admin_bp)

    from team9.email import bp as email_bp
    team9.register_blueprint(email_bp)

    if not team9.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/team9.log', maxBytes=102400, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        team9.logger.addHandler(file_handler)

        team9.logger.setLevel(logging.INFO)
        team9.logger.info('Team 9 Startup')

    return team9
