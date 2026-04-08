import cloudinary
from dotenv import load_dotenv
import os
import pymysql

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)


from flask import Flask, session, url_for, redirect
from flask_session import Session
from database import close_db_connection

from blueprints.admin import admin_bp
from blueprints.manager import man_bp
from blueprints.employee import emp_bp
from blueprints.auth import auth_bp

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.register_blueprint(admin_bp)
app.register_blueprint(man_bp)
app.register_blueprint(emp_bp)
app.register_blueprint(auth_bp)

app.teardown_appcontext(close_db_connection)

@app.route('/')
def home():
    return redirect(url_for('auth.user_login'))

@app.context_processor
def inject_user():
    from database import get_db_connection

    user_id = session.get("user_id")
    if not user_id:
        return {}

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT u.user_name, u.user_role, u.user_img_url, u.dept_id, d.dept_name
        FROM eerm_users u
        LEFT JOIN eerm_dept d ON u.dept_id = d.dept_id
        WHERE u.user_id = %s
    """, (user_id,))

    user = cursor.fetchone()
    cursor.close()

    if user:
        return {
            "current_user_name": user[0],
            "current_user_role": user[1],
            "current_user_img": user[2],
            "current_user_dept": user[4]
        }

    return {}

@app.context_processor
def inject_notifications():
    from database import get_db_connection

    conn = get_db_connection()

    if 'user_id' not in session:
        return dict(unread_count=0, notifications=[])

    cursor = conn.cursor(pymysql.cursors.DictCursor)

    user_id = session['user_id']

    cursor.execute("""
        SELECT COUNT(*) AS count 
        FROM eerm_notifs 
        WHERE user_id = %s AND read_at IS NULL AND is_deleted = 0
    """, (user_id,))
    unread_count = cursor.fetchone()['count']

    cursor.execute("""
        SELECT n.notif_id, n.message, n.created_at, n.read_at,
        u.user_name AS actor_name, u.user_img_url
        FROM eerm_notifs n
        LEFT JOIN eerm_users u ON n.actor_id = u.user_id
        WHERE n.user_id = %s AND n.is_deleted = 0
        ORDER BY n.created_at DESC
        LIMIT 5
    """, (user_id,))
    notifications = cursor.fetchall()

    return dict(
        unread_count=unread_count,
        notifications=notifications
    )

    

if __name__ == '__main__':
    app.run(debug=True)
