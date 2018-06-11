from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# TODO Revisit Bootstrap instead of CSS
# from flask_bootstrap import Bootstrap

# Not manageing DB updates in the application, so this is not needed
# from flask_migrate import Migrate

# This import with give me the missingMySQLdb python object
import pymysql
pymysql.install_as_MySQLdb()

# Manage environment variables, etc.
team9 = Flask(__name__)
team9.config.from_object(Config)
login = LoginManager(team9)

# Create the DB engine object, which gives me access to the session later
db = SQLAlchemy(team9)
db.Model.metadata.reflect(db.engine, views=True)

# As noted above, not using the migrate options,
# but leaving this behind in case I want to refernece the example later
# migrate = Migrate(team9, db)

from team9 import routes, models