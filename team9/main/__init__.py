from flask import Blueprint

bp = Blueprint('main', __name__)

from team9.main import routes