from flask import Blueprint, jsonify
from database import get_db_connection

admin_api = Blueprint('admin_api', __name__)

@admin_api.route('/dashboard')
def dashboard_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM eerm_res")
    total_res = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM eerm_alloc")
    allocated = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(amt_lmt) FROM eerm_budget")
    total_budget = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(avail_bgt) FROM eerm_budget")
    avail_budget = cursor.fetchone()[0] or 0

    cursor.execute("SELECT rc.cat_name, COUNT(r.res_id) FROM eerm_res r JOIN eerm_rescat rc ON r.cat_id = rc.cat_id GROUP BY rc.cat_name;")
    categories = cursor.fetchall() or []

    cursor.execute("""SELECT d.dept_name,
        COUNT(r.req_id) AS total_requests,
        COALESCE(SUM(CASE WHEN r.req_status = 'Approved' THEN 1 ELSE 0 END), 0) AS approved_requests
        FROM eerm_dept d
        LEFT JOIN eerm_users u ON d.dept_id = u.dept_id
        LEFT JOIN eerm_req r ON u.user_id = r.user_id
        GROUP BY d.dept_name;""")
    res_requests = cursor.fetchall() or []

    cursor.execute("""SELECT 
        d.dept_name,
        COALESCE(SUM(e.exp_amt), 0) AS total_expense,
        COALESCE(SUM(CASE 
        WHEN e.exp_status = 'Approved' THEN e.exp_amt 
        ELSE 0 
        END), 0) AS approved_expense
        FROM eerm_dept d
        LEFT JOIN eerm_users u 
        ON d.dept_id = u.dept_id
        LEFT JOIN eerm_exp e 
        ON u.user_id = e.user_id
        GROUP BY d.dept_name
        ORDER BY d.dept_name;""")
    exp_requests = cursor.fetchall() or []

    return jsonify({
        "resources": {
            "total": total_res,
            "allocated": allocated
        },
        "budget": {
            "total": total_budget,
            "available": avail_budget
        },
        "categories": {
            "labels": [row[0] for row in categories],
            "values": [row[1] for row in categories],
            "total": len(categories)
        },
        "res_requests": {
            "labels": [row[0] for row in res_requests],
            "total": [row[1] for row in res_requests],
            "approved": [row[2] for row in res_requests]
        },
        "exp_requests": {
            "labels": [row[0] for row in exp_requests],
            "total": [row[1] for row in exp_requests],
            "approved": [row[2] for row in exp_requests]
        }
    })