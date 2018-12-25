from flask import Blueprint

bp = Blueprint('auth', __name__)

from team9.auth import routes