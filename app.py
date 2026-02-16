from flask import Flask, render_template, url_for, request, session, redirect
from flask_session import Session

import pymysql


app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

conn = pymysql.connect(host='localhost', user='root', password='', database='db_eerm')

@app.route('/dashboard')
def dashboard():
    return render_template('admin/admin_dashboard.html')

@app.route('/addres')
def addres():
    return render_template('admin/admin_addres.html')

@app.route('/add_resource', methods=['POST'])
def add_resource():
    cursor = conn.cursor()
    try:
        res_name = request.form['res_name']
        res_type = request.form['res_type']   
        res_desc = request.form['res_desc']

        if not res_name:
            msg = "Resource Name is required"
            return redirect(url_for('addres', msg=msg))
        
        if not res_type:
            msg = "Resource Type is required"
            return redirect(url_for('addres', msg=msg))

        cursor.execute("SELECT cat_id FROM eerm_rescat WHERE cat_name = %s", (res_type))
        result = cursor.fetchone()

        if result is None:
            msg = "Invalid Resource Type"
            return redirect(url_for('addres', msg=msg))

        cat_id = result[0]

        cursor.execute("""
            INSERT INTO eerm_res (cat_id, res_name, res_type, res_desc)
            VALUES (%s, %s, %s, %s)
        """, (cat_id, res_name, res_type, res_desc))

        conn.commit()
        return redirect(url_for('addres'))

    except Exception as e:
        print("Error adding resource:", e)
        return "Error adding resource"

    finally:
        cursor.close()


@app.route('/viewres')
def viewres():
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM eerm_res")
        resources = cursor.fetchall()
        cursor.close()
        return render_template('admin/admin_viewres.html', resources=resources)
    except Exception as e:
        print("Error fetching resources:", e)
        return "Error fetching resources"
    finally:
        cursor.close()

@app.route('/toggle_resource_status/<int:res_id>', methods=['POST'])
def toggle_resource_status(res_id):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT res_lifestatus FROM eerm_res WHERE res_id = %s", (res_id,))
        result = cursor.fetchone()

        if result is None:
            return "Resource not found"

        current_status = result[0]
        new_status = 'Retired' if current_status == 'Active' else 'Active'

        if new_status == 'Retired':
            cursor.execute("UPDATE eerm_res SET res_status = 'Under Maintainance' WHERE res_id = %s", (res_id,))
        else:
            cursor.execute("UPDATE eerm_res SET res_status = 'Available' WHERE res_id = %s", (res_id,))
        cursor.execute("UPDATE eerm_res SET res_lifestatus = %s WHERE res_id = %s", (new_status, res_id))
        conn.commit()
        return redirect(url_for('viewres'))

    except Exception as e:
        print("Error toggling resource status:", e)
        return "Error toggling resource status"

    finally:
        cursor.close()

@app.route('/addbgt')
def addbgt():
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT cat_id, cat_name FROM eerm_expcat")
        categories = cursor.fetchall()
        return render_template('admin/admin_addbgt.html', categories=categories)

    except Exception as e:
        print("Error fetching categories:", e)
        return "Error fetching categories"
    finally:
        cursor.close()

@app.route('/add_budget', methods=['POST'])
def add_budget():
    cursor = conn.cursor() 
    try:
        bgt_dept = request.form['bgt_dept']
        bgt_cat = request.form['bgt_cat']
        bgt_amtlmt = request.form['bgt_amtlmt']
        bgt_start_date = request.form['bgt_start_date']
        bgt_end_date = request.form['bgt_end_date']


        if not bgt_amtlmt or not bgt_dept or not bgt_cat or not bgt_start_date or not bgt_end_date:
            msg = "All fields are required"
            return redirect(url_for('addbgt', msg=msg))

        cursor.execute("""
            INSERT INTO eerm_budget (department, cat_id, amt_lmt, start_date, end_date)

            VALUES (%s, %s, %s, %s, %s)
        """, (bgt_dept, bgt_cat, bgt_amtlmt, bgt_start_date, bgt_end_date))

        conn.commit()
        return redirect(url_for('addbgt'))
    except Exception as e:
        print("Error adding budget:", e)
        return "Error adding budget"
    finally:
        cursor.close()


@app.route('/viewbgt')
def view_budget():
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT b.budget_id,
                   b.department,
                   c.cat_name,
                   b.amt_lmt,
                   b.start_date,
                   b.end_date
            FROM eerm_budget b
            JOIN eerm_expcat c ON b.cat_id = c.cat_id
        """)
        budgets = cursor.fetchall()
        return render_template('admin/admin_viewbgt.html', budgets=budgets)
    except Exception as e:
        print("Error fetching budgets:", e)
        return "Error fetching budgets"
    finally:
        cursor.close()

@app.route('/update_budget', methods=['POST'])
def update_budget():
    cursor = conn.cursor()
    try:
        budget_id = request.form['budget_id']
        department = request.form['department']
        category = request.form['category']
        amt_lmt = request.form['amt_lmt']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        cursor.execute("""
            UPDATE eerm_budget
            SET department=%s,
                cat_id=(SELECT cat_id FROM eerm_expcat WHERE cat_name=%s),
                amt_lmt=%s,
                start_date=%s,
                end_date=%s
            WHERE budget_id=%s
        """, (department, category, amt_lmt, start_date, end_date, budget_id))

        conn.commit()
        return redirect(url_for('view_budget'))

    finally:
        cursor.close()


@app.route('/addpoli')
def addpoli():
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT cat_id, cat_name FROM eerm_expcat")
        categories = cursor.fetchall()
        return render_template('admin/admin_addpoli.html', categories=categories)

    except Exception as e:
        print("Error fetching categories:", e)
        return "Error fetching categories"
    finally:
        cursor.close()

@app.route('/add_policy', methods=['POST'])
def add_policy():
    cursor = conn.cursor()
    try:
        poli_type = request.form['poli_type']
        exp_cat = request.form['exp_cat']
        poli_rule = request.form['poli_rule']
        poli_desc = request.form['poli_desc']

        if not poli_type or not poli_rule:
            msg = "All fields are required"
            return redirect(url_for('addpoli', msg=msg))

        cursor.execute("""
            INSERT INTO eerm_poli (poli_type, cat_id, rule_value, poli_desc)
            VALUES (%s, %s, %s, %s)
        """, (poli_type, exp_cat, poli_rule, poli_desc))

        conn.commit()
        return redirect(url_for('addpoli'))
    except Exception as e:
        print("Error adding policy:", e)
        return "Error adding policy"
    finally:
        cursor.close()

@app.route('/viewpoli')
def viewpoli():
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT p.poli_id,
                   p.poli_type,
                   c.cat_name,
                   p.rule_value,
                   p.poli_desc
            FROM eerm_poli p
            JOIN eerm_expcat c ON p.cat_id = c.cat_id
        """)
        policies = cursor.fetchall()
        return render_template('admin/admin_viewpoli.html', policies=policies)
    except Exception as e:
        print("Error fetching policies:", e)
        return "Error fetching policies"
    finally:
        cursor.close()

@app.route('/')
def addlogin():
    return render_template('admin/admin_login.html')

@app.route('/admin_login', methods=['POST'])
def admin_login():
    cursor = conn.cursor()
    try:
        admin_email = request.form['admin_email']
        admin_pass = request.form['admin_pass']
        cursor.execute("SELECT * FROM eerm_admin WHERE admin_email = %s AND admin_pass = %s", (admin_email, admin_pass))
        admin = cursor.fetchone()
        cursor.close()
        if admin:
            session["admin_id"] = admin[0]
            session["admin_email"] = admin[1]

            msg = "Login successful!"
            return redirect(url_for('dashboard', msg=msg))
        else:
            msg = "Invalid email or password"
            return redirect(url_for('addlogin', msg=msg))
    except Exception as e:
        print("Error during login:", e)
        cursor.close()
        return "Error during login"

if __name__ == '__main__':
    app.run(debug=True)