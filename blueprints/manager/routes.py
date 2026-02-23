from flask import render_template, request, redirect, url_for, session
from database import get_db_connection
from utils import login_required, add_log

from . import man_bp

conn = get_db_connection()

@man_bp.route('/mandash')
@login_required
def mandash():
    return render_template('manager/man_dashboard.html')

@man_bp.route('/manusers-m')
@login_required
def manusers_m():
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM eerm_users where user_role = 'Employee'")
        users = cursor.fetchall()
        return render_template('manager/man_manusers.html', users=users)
    except Exception as e:
        print("Error fetching users:", e)
        return "Error fetching users"
    finally:
        cursor.close()

@man_bp.route('/toggle_user_status/<int:user_id>', methods=['POST'])
@login_required
def toggle_user_status(user_id):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_status FROM eerm_users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()

        if result is None:
            return "User not found"

        current_status = result[0]
        new_status = 'Inactive' if current_status == 'Active' else 'Active'

        if new_status == 'Inactive':
            cursor.execute("UPDATE eerm_users SET user_status = 'Inactive' WHERE user_id = %s", (user_id,))
        else:
            cursor.execute("UPDATE eerm_users SET user_status = 'Active' WHERE user_id = %s", (user_id,))
        conn.commit()

        add_log(
            session.get("admin_id"),
            "TOGGLE",
            "USER",
            user_id,
            f"Changed user status to {new_status}"
        )


        return redirect(url_for('manager.manusers_m'))

    except Exception as e:
        print("Error toggling user status:", e)
        return "Error toggling user status"

    finally:
        cursor.close()

@man_bp.route('/viewreq')
@login_required
def viewreq():
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT r.req_id,
                   r.user_id,
                   u.user_name,
                   r.res_id,
                   c.res_name,
                   r.req_date,
                   r.req_status
            FROM eerm_req r 
            JOIN eerm_users u ON r.user_id = u.user_id
            JOIN eerm_res c ON r.res_id = c.res_id
            where r.req_status = 'Pending'
        """)
        requests = cursor.fetchall()
        return render_template('manager/man_viewreq.html', requests=requests)
    except Exception as e:
        print("Error fetching requests:", e)
        return "Error fetching requests"
    finally:
        cursor.close()

@man_bp.route('/reqapprove/<int:req_id>', methods=['POST'])
@login_required
def reqapprove(req_id):
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE eerm_req SET req_status = 'Approved' WHERE req_id = %s", (req_id,))
        conn.commit()
        add_log(
            session.get("user_id"),
            "APPROVE",
            "REQUEST",
            req_id,
            f"Approved request with ID {req_id}"
        )
        return redirect(url_for('manager.viewreq'))
    except Exception as e:
        print("Error approving request:", e)
        return "Error approving request"
    finally:
        cursor.close()

@man_bp.route('/reqreject/<int:req_id>', methods=['POST'])
@login_required
def reqreject(req_id):
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE eerm_req SET req_status = 'Rejected' WHERE req_id = %s", (req_id,))
        conn.commit()
        add_log(
            session.get("user_id"),
            "REJECT",
            "REQUEST",
            req_id,
            f"Rejected request with ID {req_id}"
        )
        return redirect(url_for('manager.viewreq'))
    except Exception as e:
        print("Error rejecting request:", e)
        return "Error rejecting request"
    finally:
        cursor.close()

@man_bp.route('/reqhistory')
@login_required
def reqhistory():
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT r.req_id,
                   r.user_id,
                   u.user_name,
                   r.res_id,
                   c.res_name,
                   r.req_date,
                   r.req_status
            FROM eerm_req r 
            JOIN eerm_users u ON r.user_id = u.user_id
            JOIN eerm_res c ON r.res_id = c.res_id
            where r.req_status != 'Pending'
        """)
        requests = cursor.fetchall()
        return render_template('manager/man_reqhistory.html', requests=requests)
    except Exception as e:
        print("Error fetching request history:", e)
        return "Error fetching request history"