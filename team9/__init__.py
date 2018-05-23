from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
import pymysql
pymysql.install_as_MySQLdb()

team9 = Flask(__name__)
team9.config.from_object(Config)
db = SQLAlchemy(team9)
db.Model.metadata.reflect(db.engine, views=True)
# migrate = Migrate(team9, db)

from team9 import routes, models