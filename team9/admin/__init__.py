from flask import Blueprint

bp = Blueprint('admin', __name__)

from team9.admin import routes