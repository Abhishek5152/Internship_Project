from flask import render_template, request, redirect, url_for, session
from database import get_db_connection
from utils import login_required, add_log

from . import emp_bp

conn = get_db_connection()

@emp_bp.route('/empdash')
@login_required
def empdash():
    return render_template('employee/emp_dashboard.html')

@emp_bp.route('/myresources')
@login_required
def myresources():
    cursor = conn.cursor()
    cursor.execute("""
            SELECT a.alloc_id,
                   a.res_id,
                   c.res_name,
                   a.ret_date
            FROM eerm_alloc a 
            JOIN eerm_res c ON a.res_id = c.res_id
            where a.alloc_status != 'Pending'
        """)
    resources = cursor.fetchall()
    return render_template('employee/emp_myresources.html', resources=resources)

@emp_bp.route('/resreturn/<int:res_id>', methods=['POST'])
@login_required
def resreturn(res_id):
    user_id = session.get('user_id')
    cursor = conn.cursor()
    cursor.execute("UPDATE eerm_alloc SET alloc_status = 'Returned' WHERE alloc_id = %s AND user_id = %s", (res_id, user_id))
    add_log(
        session.get("user_id"),
        f"Returned resource with Alloc ID {res_id}"
    )
    conn.commit()
    msg = "Resource returned successfully"
    return redirect(url_for('employee.myresources', msg=msg))

@emp_bp.route('/myrequests')
@login_required
def myrequests():
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
    return render_template('employee/emp_myrequests.html', requests=requests, resources=resources)

@emp_bp.route('/new_request', methods=['POST'])
@login_required
def new_request():
    user_id = session.get('user_id')
    res_id = request.form.get('res_id')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO eerm_req (user_id, res_id) VALUES (%s, %s)", (user_id, res_id))
    add_log(
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
    user_id = session.get('user_id')
    cursor = conn.cursor()
    cursor.execute("UPDATE eerm_req SET req_status = 'Cancelled' WHERE req_id = %s AND user_id = %s", (req_id, user_id))
    add_log(
        session.get("user_id"),
        "CANCEL",
        "REQUEST",
        req_id,
        f"Cancelled request with ID {req_id}"
    )
    conn.commit()
    msg = "Request cancelled successfully"
    return redirect(url_for('employee.myrequests', msg=msg))