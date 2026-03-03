from flask import render_template, request, redirect, url_for, session
from database import get_db_connection
from utils import add_log

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
        cursor.execute("SELECT * FROM eerm_users WHERE user_email = %s AND user_pass = %s", (admin_email, admin_pass))
        admin = cursor.fetchone()
        cursor.close()
        if admin:
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
    return render_template('global_user/user_register.html')

@auth_bp.route('/register_user', methods=['POST'])
def register_user():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        reg_name = request.form['reg_name']
        reg_email = request.form['reg_email']
        reg_pass = request.form['reg_pass']

        if not reg_name or not reg_email or not reg_pass:
            msg = "All fields are required"
            return redirect(url_for('auth.user_register', msg=msg))

        cursor.execute("SELECT * FROM eerm_users WHERE user_email = %s", (reg_email,))
        existing_user = cursor.fetchone()

        if existing_user:
            msg = "Email already registered"
            return redirect(url_for('auth.user_register', msg=msg))

        cursor.execute("""
            INSERT INTO eerm_users (user_name, user_email, user_pass, user_role, user_status)
            VALUES (%s, %s, %s, 'Employee', 'Active')
        """, (reg_name, reg_email, reg_pass))
        conn.commit()

        add_log(
            conn,
            cursor.lastrowid,
            "REGISTER",
            "USER",
            cursor.lastrowid,
            f"New user registered with email {reg_email}"
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
        cursor.execute("SELECT * FROM eerm_users WHERE user_email = %s AND user_pass = %s", (user_email, user_pass))
        user = cursor.fetchone()
        cursor.close()
        if user:
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            session["user_role"] = user[4]

            add_log(
                conn,
                session.get("user_id"),
                "LOGIN",
                session.get("user_role"),
                session.get("user_id"),
                f"{session.get('user_role')} '{session.get('user_name')} 'logged in successfully"
            )

            msg = "Login successful!"

            if user[4] == 'Manager' and user[5] == 'Active':
                return redirect(url_for('manager.mandash', msg=msg))
            elif user[4] == 'Employee' and user[5] == 'Active':
                return redirect(url_for('employee.empdash', msg=msg))
            elif user[4] == 'Admin':
                msg = "Admins must log in through the admin portal"
                return redirect(url_for('auth.addlogin', msg=msg))
            elif user[5] == 'Inactive':
                msg = "Your account is inactive. Please contact the administrator."
                return redirect(url_for('auth.user_login', msg=msg))

        else:
            msg = "Invalid email or password"
            return redirect(url_for('auth.user_login', msg=msg))
    except Exception as e:
        print("Error during login:", e)
        return "Error during login"
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