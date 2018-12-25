from flask import Blueprint

bp = Blueprint('email', __name__)

from team9.email import routes