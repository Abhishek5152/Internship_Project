from flask import render_template, request, redirect, url_for, session
from database import get_db_connection
from utils import login_required

from . import emp_bp

conn = get_db_connection()

@emp_bp.route('/empdash')
@login_required
def empdash():
    return render_template('employee/emp_dashboard.html')
