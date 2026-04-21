from flask import Blueprint, jsonify, session
from database import get_db_connection

man_api = Blueprint('man_api', __name__)

@man_api.route('/mandash')
def mandash_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM eerm_res")
    total_res = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM eerm_alloc a JOIN eerm_users u ON a.user_id = u.user_id WHERE u.dept_id = %s", (session.get("dept_id"),))
    allocated = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(amt_lmt) FROM eerm_budget WHERE dept_id = %s", (session.get("dept_id"),))
    total_budget = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(avail_bgt) FROM eerm_budget WHERE dept_id = %s", (session.get("dept_id"),))
    avail_budget = cursor.fetchone()[0] or 0

    cursor.execute("SELECT rc.cat_name, COUNT(r.res_id) FROM eerm_res r JOIN eerm_rescat rc ON r.cat_id = rc.cat_id GROUP BY rc.cat_name;")
    categories = cursor.fetchall() or []


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
        }
    })