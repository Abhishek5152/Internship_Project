from flask import render_template, request, redirect, url_for, session
from database import get_db_connection
from utils import add_log
from werkzeug.security import generate_password_hash, check_password_hash
from utils import validate_password
from datetime import datetime, timedelta
import secrets

from . import auth_bp


@auth_bp.route('/addlogin')
def addlogin():
    return render_template('admin/admin_login.html')


@auth_bp.route('/admin_login', methods=['POST'])
def admin_login():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        admin_email = request.form['admin_email']
        admin_pass = request.form['admin_pass']
        cursor.execute("SELECT * FROM eerm_users WHERE user_email = %s", (admin_email,))
        admin = cursor.fetchone()
        cursor.close()
        if admin and check_password_hash(admin[3], admin_pass):
            session["user_id"] = admin[0]
            session["user_name"] = admin[1]
            session["user_email"] = admin[2]
            session["user_role"] = admin[4]

            msg = "Login successful!"

            add_log(
                conn,
                session.get("user_id"),
                "LOGIN",
                "Admin",
                session.get("user_id"),
                f"Admin logged in successfully"
            )

            return redirect(url_for('admin.dashboard', msg=msg))
        else:
            msg = "Invalid email or password"
            return redirect(url_for('auth.addlogin', msg=msg))
    except Exception as e:
        print("Error during login:", e)
        cursor.close()
        return "Error during login"
    finally:        
        cursor.close()
        

@auth_bp.route('/user_register')
def user_register():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT dept_id, dept_name FROM eerm_dept")
        departments = cursor.fetchall()
        return render_template('global_user/user_register.html', departments=departments)  
    except Exception as e:
        print("Error fetching departments:", e)
        return "Error fetching departments"
    finally:
        cursor.close()

@auth_bp.route('/register_user', methods=['POST'])
def register_user():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        reg_name = request.form['reg_name']
        reg_email = request.form['reg_email']
        reg_pass = request.form['reg_pass']
        reg_dept = request.form['reg_dept']

        if not reg_name or not reg_email or not reg_pass or not reg_dept:
            msg = "All fields are required"
            return redirect(url_for('auth.user_register', msg=msg))

        cursor.execute("SELECT * FROM eerm_users WHERE user_email = %s", (reg_email,))
        existing_user = cursor.fetchone()

        if existing_user:
            msg = "Email already registered"
            return redirect(url_for('auth.user_register', msg=msg))

        errors = validate_password(reg_pass, reg_email)

        if errors:
            return redirect(url_for('auth.user_register', msg=" ".join(errors)))
        
        register_pass = generate_password_hash(reg_pass)

        cursor.execute("""
            INSERT INTO eerm_users (user_name, user_email, user_pass, user_role, user_status, dept_id)
            VALUES (%s, %s, %s, 'Employee', 'Active', %s)
        """, (reg_name, reg_email, register_pass, reg_dept))
        conn.commit()

        add_log(
            conn,
            cursor.lastrowid,
            "REGISTER",
            "USER",
            cursor.lastrowid,
            f"New user registered with email {reg_email} in department ID {reg_dept}"
        )

        msg = "Registration successful! Please log in."
        return redirect(url_for('auth.user_login', msg=msg))
    except Exception as e:
        print("Error during registration:", e)
        return "Error during registration"
    finally:
        cursor.close()
        


@auth_bp.route('/user_login')
def user_login():
    return render_template('global_user/user_login.html')

@auth_bp.route('/userlogin', methods=['POST'])
def userlogin():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        user_email = request.form['user_email']
        user_pass = request.form['user_pass']
        cursor.execute("SELECT * FROM eerm_users WHERE user_email = %s", (user_email,))
        user = cursor.fetchone()
        if user and check_password_hash(user[3], user_pass):
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            session["user_role"] = user[4]
            session["dept_id"] = user[5]



            add_log(
                conn,
                session.get("user_id"),
                "LOGIN",
                session.get("user_role"),
                session.get("user_id"),
                f"{session.get('user_role')} '{session.get('user_name')} 'logged in successfully"
            )

            msg = "Login successful!"

            if user[4] == 'Manager' and user[6] == 'Active':
                return redirect(url_for('manager.mandash', msg=msg))
            elif user[4] == 'Employee' and user[6] == 'Active':
                return redirect(url_for('employee.empdash', msg=msg))
            elif user[4] == 'Admin':
                msg = "Admins must log in through the admin portal"
                return redirect(url_for('auth.addlogin', msg=msg))
            elif user[6] == 'Inactive':
                msg = "Your account is inactive. Please contact the administrator."
                return redirect(url_for('auth.user_login', msg=msg))
            else:
                msg = "Invalid account state."
                return redirect(url_for('auth.user_login', msg=msg))

        else:
            msg = "Invalid email or password"
            return redirect(url_for('auth.user_login', msg=msg))
    except Exception as e:
        print("Error during login:", e)
        return "Error during login"
    finally:
        cursor.close()
        
@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        user_email = request.form['user_email']

        cursor.execute("SELECT user_id, user_role FROM eerm_users WHERE user_email = %s", (user_email,))
        user = cursor.fetchone()

        if user and user[1] == 'Admin':
            return "Admin accounts cannot reset password through this portal. Please contact the administrator."

        if not user:
            return "If this email exists, a reset link has been sent."

        token = secrets.token_urlsafe(32)
        expiry = datetime.utcnow() + timedelta(minutes=15)

        cursor.execute("""
            INSERT INTO eerm_forpass (user_id, token, expires_at)
            VALUES (%s, %s, %s)
        """, (user[0], token, expiry))

        conn.commit()

        # reset_link = url_for('auth.reset_password', token=token, _external=True)

        # msg = "If this email exists, a reset link has been sent."

        return redirect(url_for('auth.reset_password', token=token, _external=True))

    finally:
        cursor.close()

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT user_id, expires_at FROM eerm_forpass WHERE token = %s
        """, (token,))
        record = cursor.fetchone()

        if not record:
            return "Invalid or expired token"

        if datetime.utcnow() > record[1]:
            return "Token expired"

        if request.method == 'POST':
            new_password = request.form['password']

            errors = validate_password(new_password)
            if errors:
                return render_template("global_user/user_resetpass.html", token=token, msg=" ".join(errors))

            hashed = generate_password_hash(new_password)

            cursor.execute("""
                UPDATE eerm_users SET user_pass = %s WHERE user_id = %s
            """, (hashed, record[0]))

            cursor.execute("DELETE FROM eerm_forpass WHERE token = %s", (token,))

            conn.commit()

            msg = "Password reset successful! Please log in with your new password."
            
            return render_template("global_user/user_login.html", msg=msg)

        return render_template("global_user/user_resetpass.html", token=token)

    finally:
        cursor.close()

@auth_bp.route('/logout')
def logout():   
    user_id = session.get("user_id")
    if user_id:
        add_log(
            get_db_connection(),
            user_id,
            "LOGOUT",
            session.get("user_role"),
            user_id,
            f"{session.get('user_role')} '{session.get('user_name')}' logged out successfully"
        )
    session.clear()
    return redirect(url_for('auth.user_login'))