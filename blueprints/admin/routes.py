from flask import render_template, request, redirect, url_for, session
from database import get_db_connection
from utils import login_required, add_log

import cloudinary.uploader

from . import admin_bp

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM eerm_users where user_role != 'Admin'")
        users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM eerm_users WHERE user_role = 'Employee'")
        employees = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM eerm_users WHERE user_role = 'Manager'")
        managers = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM eerm_res")
        all_resources = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM eerm_alloc")
        active_resources = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(amt_lmt) FROM eerm_budget")
        budget = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(avail_bgt) FROM eerm_budget")
        avail_budget = cursor.fetchone()[0]

        emp_percent = (employees / users * 100) if users else 0
        mgr_percent = (managers / users * 100) if users else 0
        res_percent = (active_resources / all_resources * 100) if all_resources else 0
        bgt_percent = (avail_budget / budget * 100) if budget else 0

        return render_template('admin/admin_dashboard.html', 
                               employees=employees, 
                               managers=managers, 
                               active_resources=active_resources,
                               avail_budget=int(avail_budget),
                               bgt_percent=bgt_percent,
                               emp_percent=emp_percent,
                               mgr_percent=mgr_percent,
                               res_percent=res_percent)
        
    except Exception as e:
        print("Error loading dashboard:", e)
    finally:
        cursor.close()

@admin_bp.route('/addres')
@login_required
def addres():
    return render_template('admin/admin_addres.html')

@admin_bp.route('/add_resource', methods=['POST'])
def add_resource():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        res_name = request.form['res_name']
        res_type = request.form['res_type']   
        res_desc = request.form['res_desc']

        if not res_name:
            msg = "Resource Name is required"
            return redirect(url_for('admin.addres', msg=msg))
        
        if not res_type:
            msg = "Resource Type is required"
            return redirect(url_for('admin.addres', msg=msg))

        cursor.execute("SELECT cat_id FROM eerm_rescat WHERE cat_name = %s", (res_type,))
        result = cursor.fetchone()

        if result is None:
            msg = "Invalid Resource Type"
            return redirect(url_for('admin.addres', msg=msg))

        cat_id = result[0]

        cursor.execute("""
            INSERT INTO eerm_res (cat_id, res_name, res_type, res_desc)
            VALUES (%s, %s, %s, %s)
        """, (cat_id, res_name, res_type, res_desc))

        add_log(
            conn,
            session.get("user_id"),
            "ADD",
            "RESOURCE",
            cursor.lastrowid,
            f"Added new resource: {res_name} of type {res_type}"
        )

        conn.commit()
        msg = "Resource added successfully"
        return redirect(url_for('admin.viewres', msg=msg))

    except Exception as e:
        print("Error adding resource:", e)
        return "Error adding resource"

    finally:
        cursor.close()
        


@admin_bp.route('/viewres')
@login_required
def viewres():
    conn = get_db_connection()
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
        

@admin_bp.route('/toggle_resource_status/<int:res_id>', methods=['POST'])
@login_required
def toggle_resource_status(res_id):
    conn = get_db_connection()
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

        add_log(
            conn,
            session.get("user_id"),
            "TOGGLE",
            "RESOURCE",
            res_id,
            f"Changed resource status to {new_status}"
        )

        msg = "Resource status updated successfully"
        return redirect(url_for('admin.viewres', msg=msg))

    except Exception as e:
        print("Error toggling resource status:", e)
        return "Error toggling resource status"

    finally:
        cursor.close()
        

@admin_bp.route('/addbgt')
@login_required
def addbgt():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT dept_id, dept_name FROM eerm_dept")
        departments = cursor.fetchall()
        cursor.execute("SELECT cat_id, cat_name FROM eerm_expcat")
        categories = cursor.fetchall()
        return render_template('admin/admin_addbgt.html', departments=departments, categories=categories)

    except Exception as e:
        print("Error fetching categories:", e)
        return "Error fetching categories"
    finally:
        cursor.close()
        

@admin_bp.route('/add_budget', methods=['POST'])
def add_budget():
    conn = get_db_connection()
    cursor = conn.cursor() 
    try:
        bgt_dept = request.form['bgt_dept']
        bgt_cat = request.form['bgt_cat']
        bgt_amtlmt = request.form['bgt_amtlmt']
        bgt_year = request.form['bgt_year']


        if not bgt_amtlmt or not bgt_dept or not bgt_cat or not bgt_year:
            msg = "All fields are required"
            return redirect(url_for('admin.addbgt', msg=msg))

        cursor.execute("""
            INSERT INTO eerm_budget (dept_id, cat_id, amt_lmt, avail_bgt, bgt_year)
            VALUES (%s, %s, %s, %s, %s)
        """, (bgt_dept, bgt_cat, bgt_amtlmt, bgt_amtlmt, bgt_year))

        add_log(
            conn,
            session.get("user_id"),
            "CREATE",
            "BUDGET",
            cursor.lastrowid,
            f"Created budget for {bgt_dept} with category {bgt_cat} and amount limit {bgt_amtlmt}"
        )


        conn.commit()
        msg = "Budget added successfully"
        return redirect(url_for('admin.viewbgt', msg=msg))
    except Exception as e:
        print("Error adding budget:", e)
        return "Error adding budget"
    finally:
        cursor.close()
        


@admin_bp.route('/viewbgt')
@login_required
def viewbgt():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT d.dept_name,
                   SUM(b.amt_lmt) AS total_budget,
                   SUM(b.avail_bgt) AS available_budget,
                   b.bgt_year,
                   b.dept_id
            FROM eerm_budget b
            JOIN eerm_dept d ON b.dept_id = d.dept_id
            GROUP BY b.dept_id, d.dept_name, b.bgt_year
        """, )
        budgets = cursor.fetchall()
        return render_template('admin/admin_viewbgt.html', budgets=budgets)
    except Exception as e:
        print("Error fetching budgets:", e)
        return "Error fetching budgets"
    finally:
        cursor.close()
        
@admin_bp.route('/viewbgtdata/<int:dept_id>')
@login_required
def viewbgtdata(dept_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT b.budget_id,
                   b.cat_id,
                   c.cat_name,
                   b.amt_lmt,
                   b.avail_bgt,
                   b.bgt_year,
                   b.dept_id
            FROM eerm_budget b
            JOIN eerm_expcat c ON b.cat_id = c.cat_id
            where b.dept_id =%s
        """, (dept_id))
        budgets = cursor.fetchall()
        cursor.execute("SELECT cat_id, cat_name FROM eerm_expcat")
        categories = cursor.fetchall()
        cursor.execute("SELECT dept_name FROM eerm_dept where dept_id=%s", dept_id)
        dept = cursor.fetchone()
        return render_template('admin/admin_viewbgtdata.html', budgets=budgets, categories=categories, dept=dept)
    except Exception as e:
        print("Error fetching budgets:", e)
        return "Error fetching budgets"
    finally:
        cursor.close()


@admin_bp.route('/update_budget', methods=['POST'])
@login_required
def update_budget():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        budget_id = request.form['budget_id']
        department = request.form['department']
        category = request.form['category']
        amt_lmt = request.form['amt_lmt']
        avail_bgt = request.form['avail_bgt']
        bgt_year = request.form['bgt_year']

        cursor.execute("""
            UPDATE eerm_budget
            SET dept_id=%s,
                cat_id=%s,
                amt_lmt=%s,
                avail_bgt=%s,
                bgt_year=%s
            WHERE budget_id=%s
        """, (department, category, amt_lmt, avail_bgt, bgt_year, budget_id))

        add_log(
            conn,
            session.get("user_id"),
            "UPDATE",
            "BUDGET",
            budget_id,
            f"Updated budget for {department} with category {category} and amount limit {amt_lmt}"
        )


        conn.commit()
        msg = "Budget updated successfully"
        return redirect(url_for('admin.viewbgt', msg=msg))

    finally:
        cursor.close()
        

@admin_bp.route('/delete_budget/<int:budget_id>')
@login_required
def delete_budget(budget_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM eerm_budget WHERE budget_id=%s", (budget_id,))
        add_log(
            conn,
            session.get("user_id"),
            "DELETE",
            "BUDGET",
            budget_id,
            f"Deleted budget with ID {budget_id}"
        )
        conn.commit()
        msg = "Budget deleted successfully"
        return redirect(url_for('admin.viewbgt', msg=msg))
    finally:
        cursor.close()
        

@admin_bp.route('/addpoli')
@login_required
def addpoli():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT cat_id, cat_name FROM eerm_expcat")
        categories = cursor.fetchall()
        cursor.execute("SELECT cat_id, cat_name FROM eerm_policat")
        policies = cursor.fetchall()
        return render_template('admin/admin_addpoli.html', categories=categories, policies=policies)

    except Exception as e:
        print("Error fetching categories:", e)
        return "Error fetching categories"
    finally:
        cursor.close()
        

@admin_bp.route('/add_policy', methods=['POST'])
def add_policy():
    conn = get_db_connection()
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
            INSERT INTO eerm_poli (policat_id, cat_id, rule_value, poli_desc)
            VALUES (%s, %s, %s, %s)
        """, (poli_type, exp_cat, poli_rule, poli_desc))

        add_log(
            conn,
            session.get("user_id"),
            "ADD",
            "POLICY",
            cursor.lastrowid,
            f"Added new policy: {poli_type} with rule {poli_rule} for category {exp_cat}"
        )

        conn.commit()
        msg = "Policy added successfully"
        return redirect(url_for('admin.viewpoli', msg=msg))
    except Exception as e:
        print("Error adding policy:", e)
        return "Error adding policy"
    finally:
        cursor.close()
        

@admin_bp.route('/viewpoli')
@login_required
def viewpoli():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT p.poli_id,
                   p.cat_id,
                   c.cat_name,
                   p.policat_id,
                   pc.cat_name as policat_name,
                   p.rule_value,
                   p.poli_desc,
                   p.created_at
            FROM eerm_poli p
            JOIN eerm_expcat c ON p.cat_id = c.cat_id
            JOIN eerm_policat pc ON p.policat_id = pc.cat_id
        """)
        policies = cursor.fetchall()
        cursor.execute("SELECT cat_id, cat_name FROM eerm_expcat")
        categories = cursor.fetchall()
        cursor.execute("SELECT cat_id, cat_name FROM eerm_policat")
        policat = cursor.fetchall()
        return render_template('admin/admin_viewpoli.html', policies=policies, categories=categories, policat=policat)
    except Exception as e:
        print("Error fetching policies:", e)
        return "Error fetching policies"
    finally:
        cursor.close()
        

@admin_bp.route('/update_policy', methods=['POST'])
@login_required
def update_policy():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        poli_id = request.form['poli_id']
        poli_type = request.form['poli_type']
        exp_cat = request.form['exp_cat']
        poli_rule = request.form['poli_rule']
        poli_desc = request.form['poli_desc']

        cursor.execute("""
            UPDATE eerm_poli SET 
                policat_id=%s, 
                cat_id=%s, 
                rule_value=%s, 
                poli_desc=%s
            WHERE poli_id=%s
        """, (poli_type, exp_cat, poli_rule, poli_desc, poli_id))

        add_log(
            conn,
            session.get("user_id"),
            "UPDATE",
            "POLICY",
            poli_id,
            f"Updated policy with ID {poli_id}"
        )

        conn.commit()
        msg = "Policy updated successfully"
        return redirect(url_for('admin.viewpoli', msg=msg))
    except Exception as e:
        print("Error updating policy:", e)
        return "Error updating policy"
    finally:
        cursor.close()
        

@admin_bp.route('/delete_policy/<int:poli_id>')
@login_required
def delete_policy(poli_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM eerm_poli WHERE poli_id=%s", (poli_id,))
        add_log(
            conn,
            session.get("user_id"),
            "DELETE",
            "POLICY",
            poli_id,
            f"Deleted policy with ID {poli_id}"
        )
        conn.commit()
        msg = "Policy deleted successfully"
        return redirect(url_for('admin.viewpoli', msg=msg))
    finally:
        cursor.close()
        
        

@admin_bp.route('/manusers')
@login_required
def manusers():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""SELECT u.user_id, u.user_name, u.user_email, u.user_role, u.user_status, u.created_at , d.dept_name ,u.dept_id
        FROM eerm_users u 
        JOIN eerm_dept d ON u.dept_id = d.dept_id
        where u.user_role != 'Admin'""")
        users = cursor.fetchall()
        cursor.execute("SELECT dept_id, dept_name from eerm_dept")
        department = cursor.fetchall()
        return render_template('admin/admin_manusers.html', users=users, department = department)
    except Exception as e:
        print("Error fetching users:", e)
        return "Error fetching users"
    finally:
        cursor.close()
        

@admin_bp.route('/update_user', methods=['POST'])
@login_required
def update_user():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        user_id = request.form['user_id']
        user_name = request.form['user_name']
        user_email = request.form['user_email']
        user_role = request.form['user_role']
        user_status = request.form['user_status']

        cursor.execute("""
            UPDATE eerm_users SET 
                user_name=%s, 
                user_email=%s, 
                user_role=%s,
                user_status=%s
            WHERE user_id=%s
        """, (user_name, user_email, user_role, user_status, user_id))

        add_log(
            conn,
            session.get("user_id"),
            "UPDATE",
            "USER",
            user_id,
            f"Updated details for User ID {user_id}"
        )

        conn.commit()
        msg = "User updated successfully"
        return redirect(url_for('admin.manusers', msg=msg))
    except Exception as e:
        print("Error updating user:", e)
        return "Error updating user"
    finally:
        cursor.close()
        

@admin_bp.route('/toggle_user_status/<int:user_id>', methods=['POST'])
@login_required
def toggle_user_status(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_status FROM eerm_users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()

        if result is None:
            return "User not found"

        current_status = result[0]
        new_status = 'Inactive' if current_status == 'Active' else 'Active'

        cursor.execute("UPDATE eerm_users SET user_status = %s WHERE user_id = %s", (new_status, user_id))
        conn.commit()

        add_log(
            conn,
            session.get("user_id"),
            "TOGGLE",
            "USER_STATUS",
            user_id,
            f"Changed user status to {new_status}"
        )

        msg = "User status updated successfully"
        return redirect(url_for('admin.manusers', msg=msg))

    except Exception as e:
        print("Error toggling user status:", e)
        return "Error toggling user status"

    finally:
        cursor.close()
        


@admin_bp.route('/viewlogs')
@login_required
def viewlogs():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT l.log_id,
                   l.user_id,
                   l.action,
                   l.entity,
                   l.entity_id,
                   l.log_desc,
                   l.created_at
            FROM eerm_logs l
            ORDER BY l.created_at DESC
        """)
        logs = cursor.fetchall()
        return render_template('admin/admin_viewlogs.html', logs=logs)
    finally:
        cursor.close()
        

@admin_bp.route('/upload_profile_photo', methods=['POST'])
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

        return redirect(url_for('admin.mngprof'))

    finally:
        cursor.close()         

@admin_bp.route('/mngprof')
@login_required
def mngprof():
    user_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, user_name, user_email, user_contact, user_address, user_about, user_img_url FROM eerm_users WHERE user_id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    
    return render_template('admin/admin_mngprof.html', user_data=user_data)

@admin_bp.route('/edit_profile', methods=['GET', 'POST'])
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
            return redirect(url_for('admin.mngprof', msg=msg))
        else:
            cursor.execute("SELECT user_id, user_name, user_email, user_contact, user_address, user_about FROM eerm_users WHERE user_id = %s", (user_id,))
            user_data = cursor.fetchone()
            return render_template('admin/admin_edit_profile.html', user_data=user_data)
    finally:
        cursor.close()
        