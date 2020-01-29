import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # Key for form management and combat XSS/CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hilton_head_island'

    # MySql DB configurations
    SQLALCHEMY_DATABASE_URI = \
        os.environ.get('DATABASE_URL') or 'mysql://yrd:amsterdam@localhost:3306/AmsterdamTeam9'

    # SqlLite format - 'localhost:3306' + os.path.join(basedir, 'team9.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email Support - many not used since we use boto3 and AWS SES
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.googlemail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = int(os.environ.get('MAIL_USE_TLS') or 1)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'yourackdiscipline@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'password'
    ADMINS = ['yourackdiscipline@gmail.com']

    # Image uploads - upload for MIME, static for inline
    UPLOAD_FOLDER = './uploads'
    STATIC_FILES = './static'
    MOVE_TARGET = './static'
    ALLOWED_EXTENSIONS = set(['jpg'])

    # URL for pygal links
    PYGAL_URL = os.environ.get('PYGAL_URL') or 'https://www.yourackdiscipline.com'