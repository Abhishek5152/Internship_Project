from flask import session, redirect, url_for
from functools import wraps
import re


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin_id" not in session and "user_id" not in session:
            return redirect(url_for('auth.addlogin'))
        return f(*args, **kwargs)
    return decorated_function


def add_log(conn, user_id, action_type, entity_type, entity_id, description):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO eerm_logs 
            (user_id, action, entity, entity_id, log_desc)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, action_type, entity_type, entity_id, description))
    finally:
        cursor.close()


def validate_password(password, email=None):
    errors = []

    if len(password) < 10:
        errors.append("Password must be at least 10 characters long.")

    if not re.search(r"[A-Z]", password):
        errors.append("Must contain at least one uppercase letter.")

    if not re.search(r"[a-z]", password):
        errors.append("Must contain at least one lowercase letter.")

    if not re.search(r"\d", password):
        errors.append("Must contain at least one number.")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("Must contain at least one special character.")

    if email and email.split("@")[0].lower() in password.lower():
        errors.append("Password cannot contain your email/username.")

    return errors