from flask import Blueprint

man_bp = Blueprint('manager', __name__, url_prefix='/manager')

from . import routes