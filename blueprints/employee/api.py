from flask import Blueprint, jsonify, session
from database import get_db_connection
from utils import get_value

emp_api = Blueprint('emp_api', __name__)

@emp_api.route('/empdash')
def empdash_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""SELECT
                (SELECT COUNT(*) FROM eerm_req r JOIN eerm_users u ON r.user_id = u.user_id WHERE u.dept_id = %s ) +
                (SELECT COUNT(*) FROM eerm_exp e JOIN eerm_users u ON e.user_id = u.user_id WHERE u.dept_id = %s )
                AS total_requests;""", (session.get("dept_id"),session.get("dept_id"),))
    all_requests = get_value(cursor)

    cursor.execute("""SELECT 
            (SELECT COUNT(*) FROM eerm_req WHERE user_id = %s ) +
            (SELECT COUNT(*) FROM eerm_exp WHERE user_id = %s )
            AS total_requests;""", (session.get("user_id"),session.get("user_id"),))
    my_requests = get_value(cursor)

    cursor.execute("""SELECT 
            (SELECT COUNT(*) FROM eerm_req WHERE user_id = %s AND req_status = 'Pending') +
            (SELECT COUNT(*) FROM eerm_exp WHERE user_id = %s AND exp_status = 'Pending')
            AS total_requests;""", (session.get("user_id"),session.get("user_id"),))
    Pen_requests = get_value(cursor)

    cursor.execute("""SELECT 
            (SELECT COUNT(*) FROM eerm_req WHERE user_id = %s AND req_status = 'Approved') +
            (SELECT COUNT(*) FROM eerm_exp WHERE user_id = %s AND exp_status = 'Approved')
            AS total_requests;""", (session.get("user_id"),session.get("user_id"),))
    apr_requests = get_value(cursor)

    cursor.execute("""SELECT 
            (SELECT COUNT(*) FROM eerm_req WHERE user_id = %s AND req_status = 'Rejected') +
            (SELECT COUNT(*) FROM eerm_exp WHERE user_id = %s AND exp_status = 'Rejected')
            AS total_requests;""", (session.get("user_id"),session.get("user_id"),))
    rej_requests = get_value(cursor)


    return jsonify({
    "requests": {
        "total": my_requests or 0,
        "pending": Pen_requests or 0,
        "approved": apr_requests or 0,
        "rejected": rej_requests or 0
    }
})