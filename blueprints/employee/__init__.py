from flask import Blueprint

emp_bp = Blueprint('employee', __name__, url_prefix='/employee')

from . import routes