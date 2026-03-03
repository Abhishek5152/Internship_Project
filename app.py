import cloudinary
from dotenv import load_dotenv
import os

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
        SELECT user_name, user_role, user_img_url
        FROM eerm_users
        WHERE user_id = %s
    """, (user_id,))

    user = cursor.fetchone()
    cursor.close()

    if user:
        return {
            "current_user_name": user[0],
            "current_user_role": user[1],
            "current_user_img": user[2]
        }

    return {}

if __name__ == '__main__':
    app.run(debug=True)
