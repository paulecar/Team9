from flask import Blueprint

bp = Blueprint('errors', __name__)

from team9.errors import handlers