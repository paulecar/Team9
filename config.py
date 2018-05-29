import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # Key for form management and combat XSS/CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hilton_head_island'
    # MySql DB configurations
    # TODO Create application account and stop using root/pwd combo
    SQLALCHEMY_DATABASE_URI = \
        os.environ.get('DATABASE_URL') or 'mysql://root:Cerbera1#@localhost:3306/AmsterdamTeam9'
    # SqlLite format - 'localhost:3306' + os.path.join(basedir, 'team9.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
