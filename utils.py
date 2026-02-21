from flask import session, redirect, url_for
from functools import wraps
from database import get_db_connection

conn = get_db_connection()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin_id" not in session and "user_id" not in session:
            return redirect(url_for('auth.addlogin'))
        return f(*args, **kwargs)
    return decorated_function


def add_log(user_id, action_type, entity_type, entity_id, description):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO eerm_logs 
            (user_id, action, entity, entity_id, log_desc)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, action_type, entity_type, entity_id, description))
        conn.commit()
    finally:
        cursor.close()
