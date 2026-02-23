from flask import Flask, url_for, redirect
from flask_session import Session

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

@app.route('/')
def home():
    return redirect(url_for('auth.user_login'))

if __name__ == '__main__':
    app.run(debug=True)
