import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # MySql DB configurations
    # TODO Someting better than using root/pwd combo
    SQLALCHEMY_DATABASE_URI = \
        os.environ.get('DATABASE_URL') or 'mysql://root:Cerbera1#@localhost:3306/AmsterdamTeam9'
    # SqlLite format - 'localhost:3306' + os.path.join(basedir, 'team9.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
