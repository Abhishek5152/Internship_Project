from flask import render_template, request, redirect, url_for, session
from database import get_db_connection
from utils import login_required, add_log
from services.notif_service import create_notif

import cloudinary.uploader
import uuid
import pymysql

from . import emp_bp

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@emp_bp.route('/empdash')
@login_required
def empdash():
    return render_template('employee/emp_dashboard.html')

@emp_bp.route('/myresources')
@login_required
def myresources():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
            SELECT a.alloc_id,
                   a.res_id,
                   c.res_name,
                   a.ret_date
            FROM eerm_alloc a 
            JOIN eerm_res c ON a.res_id = c.res_id
            where a.alloc_status != 'Pending' AND a.user_id = %s
        """, (session.get('user_id'),))
    resources = cursor.fetchall()
    cursor.close()
    
    return render_template('employee/emp_myresources.html', resources=resources)

@emp_bp.route('/resreturn/<int:res_id>', methods=['POST'])
@login_required
def resreturn(res_id):
    conn = get_db_connection()
    user_id = session.get('user_id')
    cursor = conn.cursor()
    cursor.execute("UPDATE eerm_alloc SET alloc_status = 'Returned' WHERE alloc_id = %s AND user_id = %s", (res_id, user_id))
    add_log(
        conn,
        session.get("user_id"),
        "RETURN",
        "RESOURCE",
        res_id,
        f"Returned resource with Alloc ID {res_id}"
    )
    conn.commit()
    msg = "Resource returned successfully"
    cursor.close()
    
    return redirect(url_for('employee.myresources', msg=msg))

@emp_bp.route('/myrequests')
@login_required
def myrequests():
    conn = get_db_connection()
    user_id = session.get('user_id')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.req_id, r.res_id, res.res_name, r.req_date, r.req_status
        FROM eerm_req r
        JOIN eerm_res res ON r.res_id = res.res_id
        WHERE r.user_id = %s
        ORDER BY r.req_date DESC
    """, (user_id,))
    requests = cursor.fetchall()
    cursor.execute("SELECT res_id, res_name FROM eerm_res")
    resources = cursor.fetchall()
    cursor.close()
    
    return render_template('employee/emp_myrequests.html', requests=requests, resources=resources)

@emp_bp.route('/new_request', methods=['POST'])
@login_required
def new_request():
    conn = get_db_connection()
    user_id = session.get('user_id')
    res_id = request.form.get('res_id')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO eerm_req (user_id, res_id) VALUES (%s, %s)", (user_id, res_id))
    add_log(
            conn,
            session.get("user_id"),
            "CREATE",
            "REQUEST",
            res_id,
        f"Created new request for resource ID {res_id}"
    )
    
    conn.commit()
    msg = "Request submitted successfully"
    return redirect(url_for('employee.myrequests', msg=msg))

@emp_bp.route('/reqcancel/<int:req_id>', methods=['POST'])
@login_required
def reqcancel(req_id):
    conn = get_db_connection()
    user_id = session.get('user_id')
    cursor = conn.cursor()
    cursor.execute("UPDATE eerm_req SET req_status = 'Cancelled' WHERE req_id = %s AND user_id = %s", (req_id, user_id))
    add_log(
        conn,
        session.get("user_id"),
        "CANCEL",
        "REQUEST",
        req_id,
        f"Cancelled request with ID {req_id}"
    )
    conn.commit()
    msg = "Request cancelled successfully"
    cursor.close()
    
    return redirect(url_for('employee.myrequests', msg=msg))

@emp_bp.route('/upload_profile_photo', methods=['POST'])
@login_required
def upload_profile_photo():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        file = request.files.get('photo')

        if not file or not allowed_file(file.filename):
            return "Invalid file type"

        result = cloudinary.uploader.upload(
            file,
            folder="eerm_profiles",
            public_id=f"user_{session.get('user_id')}",
            overwrite=True,
            transformation=[
                {"width": 300, "height": 300, "crop": "fill"}
            ]
        )

        image_url = result['secure_url']

        cursor.execute("""
            UPDATE eerm_users
            SET user_img_url=%s
            WHERE user_id=%s
        """, (image_url, session.get('user_id')))

        add_log(
            conn,
            session.get("user_id"),
            "UPDATE",
            "USER_PHOTO",
            session.get("user_id"),
            "Updated profile picture"
        )

        conn.commit()

        return redirect(url_for('employee.emp_mngprof'))

    finally:
        cursor.close()

@emp_bp.route('/addexpense')
@login_required
def addexpense():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT cat_id, cat_name FROM eerm_expcat")
        exp_types = cursor.fetchall()
        return render_template('employee/emp_addexp.html', exp_types=exp_types)
    except Exception as e:
        print("Error fetching expense types:", e)
    finally:        
        cursor.close()

@emp_bp.route('/submitexpense', methods=['POST'])
@login_required
def submitexpense():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        exp_type = request.form.get('exp_type')
        exp_desc = request.form.get('exp_desc')
        exp_amount = request.form.get('exp_amount')
        exp_date = request.form.get('exp_date')
        user_id = session.get('user_id')

        file = request.files.get('document')

        if not file or not allowed_file(file.filename):
            return "Invalid file type"
        
        result = cloudinary.uploader.upload(
            file,
            folder="eerm_receipts",
            public_id=f"user_{user_id}_{uuid.uuid4()}",
            resource_type="auto",
            overwrite=True
        )
        receipt_url = result['secure_url']
        
        cursor.execute("INSERT INTO eerm_exp (user_id, cat_id, exp_amt, exp_desc, exp_date, receipt_url) VALUES (%s, %s, %s, %s, %s, %s)", (user_id, exp_type, exp_amount, exp_desc, exp_date, receipt_url))
        conn.commit()
        msg = "Expense submitted successfully"
        return redirect(url_for('employee.viewrequests', msg=msg))
    except Exception as e:
        print("Error submitting expense:", e)
    finally:
        cursor.close()

@emp_bp.route('/viewexpense')
@login_required
def viewexpense():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        user_id = session.get('user_id')
        cursor.execute("""
            SELECT e.exp_id, c.cat_name, e.exp_amt, e.exp_desc, e.exp_date, e.exp_status ,e.receipt_url
            FROM eerm_exp e
            JOIN eerm_expcat c ON e.cat_id = c.cat_id
            WHERE e.user_id = %s and e.exp_status != "Pending" and e.exp_status != "Cancelled"
            ORDER BY e.created_at DESC
        """, (user_id,))
        expenses = cursor.fetchall()
        return render_template('employee/emp_viewexp.html', expenses=expenses)
    except Exception as e:
        print("Error fetching expenses:", e)
        return "Error fetching expenses"
    finally:
        cursor.close()

@emp_bp.route('/exprequests')
@login_required
def exprequests():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        user_id = session.get('user_id')
        cursor.execute("""
            SELECT e.exp_id, c.cat_name, e.exp_amt, e.exp_desc, e.exp_date, e.exp_status ,e.receipt_url
            FROM eerm_exp e
            JOIN eerm_expcat c ON e.cat_id = c.cat_id
            WHERE e.user_id = %s AND e.exp_status != "Approved" AND e.exp_status != "Rejected"
            ORDER BY e.created_at DESC
        """, (user_id,))
        expenses = cursor.fetchall()
        print ("Fetched expense requests:", expenses)
        return render_template('employee/emp_viewexpreq.html', expenses=expenses)
    except Exception as e:
        print("Error fetching expense requests:", e)
        return "Error fetching expense requests"
    finally:
        cursor.close()

@emp_bp.route('/cancelreq/<int:exp_id>', methods=['POST'])
@login_required
def cancelreq(exp_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE eerm_exp SET exp_status='Cancelled' WHERE exp_id=%s", (exp_id,))
        conn.commit()
        return redirect(url_for('employee.exprequests'))
    except Exception as e:
        print("Error cancelling expense request:", e)
        return "Error cancelling expense request"
    finally:
        cursor.close()

@emp_bp.route('/emp_mngprof')
@login_required
def emp_mngprof():
    conn = get_db_connection()
    user_id = session.get('user_id')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, user_name, user_email, user_contact, user_address, user_about, user_img_url, dept_name FROM eerm_users JOIN eerm_dept ON eerm_users.dept_id = eerm_dept.dept_id WHERE user_id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    
    return render_template('employee/emp_mngprof.html', user_data=user_data)

@emp_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if request.method == 'POST':
            user_name = request.form.get('user_name')
            user_contact = request.form.get('user_contact')
            user_address = request.form.get('user_address')
            user_about = request.form.get('user_about')

            cursor.execute("""
                UPDATE eerm_users SET 
                    user_name=%s, 
                    user_contact=%s, 
                    user_address=%s,
                    user_about=%s
                WHERE user_id=%s
            """, (user_name, user_contact, user_address, user_about, user_id))

            add_log(
                conn,
                user_id,
                "UPDATE",
                "USER_PROFILE",
                user_id,
                f"Updated profile details for User ID {user_id}"
            )

            conn.commit()
            msg = "Profile updated successfully"
            return redirect(url_for('employee.emp_mngprof', msg=msg))
        else:
            cursor.execute("SELECT user_id, user_name, user_email, user_contact, user_address, user_about FROM eerm_users WHERE user_id = %s", (user_id,))
            user_data = cursor.fetchone()
            return render_template('employee/emp_edit_profile.html', user_data=user_data)
    except Exception as e:
        print("Error updating profile:", e)
        return "Error updating profile"
    finally:
        cursor.close()
        
@emp_bp.route('/notifications/all')
def all_notifications():
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT n.notif_id, n.message, n.created_at, n.read_at,
               u.user_name AS actor_name
        FROM eerm_notifs n
        LEFT JOIN eerm_users u ON n.actor_id = u.user_id
        WHERE n.user_id = %s AND n.is_deleted = 0
        ORDER BY n.created_at DESC
    """, (user_id,))

    notifications = cursor.fetchall()

    return render_template('partials/notifs_list.html', notifications=notifications)