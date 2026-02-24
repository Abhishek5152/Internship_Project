from flask import render_template, request, redirect, url_for, session
from database import get_db_connection
from utils import login_required, add_log

from . import admin_bp

conn = get_db_connection()

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('admin/admin_dashboard.html')

@admin_bp.route('/addres')
@login_required
def addres():
    return render_template('admin/admin_addres.html')

@admin_bp.route('/add_resource', methods=['POST'])
def add_resource():
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
            session.get("admin_id"),
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
            session.get("admin_id"),
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

@admin_bp.route('/add_budget', methods=['POST'])
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
            return redirect(url_for('admin.addbgt', msg=msg))

        cursor.execute("""
            INSERT INTO eerm_budget (department, cat_id, amt_lmt, avail_bgt, start_date, end_date)

            VALUES (%s, %s, %s, %s, %s, %s)
        """, (bgt_dept, bgt_cat, bgt_amtlmt, bgt_amtlmt, bgt_start_date, bgt_end_date))

        add_log(
            session.get("admin_id"),
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
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT b.budget_id,
                   b.department,
                   b.cat_id,
                   c.cat_name,
                   b.amt_lmt,
                   b.avail_bgt,
                   b.start_date,
                   b.end_date
            FROM eerm_budget b
            JOIN eerm_expcat c ON b.cat_id = c.cat_id
        """)
        budgets = cursor.fetchall()
        cursor.execute("SELECT cat_id, cat_name FROM eerm_expcat")
        categories = cursor.fetchall()
        return render_template('admin/admin_viewbgt.html', budgets=budgets, categories=categories)
    except Exception as e:
        print("Error fetching budgets:", e)
        return "Error fetching budgets"
    finally:
        cursor.close()

@admin_bp.route('/update_budget', methods=['POST'])
@login_required
def update_budget():
    cursor = conn.cursor()
    try:
        budget_id = request.form['budget_id']
        department = request.form['department']
        category = request.form['category']
        amt_lmt = request.form['amt_lmt']
        avail_bgt = request.form['avail_bgt']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        cursor.execute("""
            UPDATE eerm_budget
            SET department=%s,
                cat_id=%s,
                amt_lmt=%s,
                avail_bgt=%s,
                start_date=%s,
                end_date=%s
            WHERE budget_id=%s
        """, (department, category, amt_lmt, avail_bgt, start_date, end_date, budget_id))

        add_log(
            session.get("admin_id"),
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
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM eerm_budget WHERE budget_id=%s", (budget_id,))
        add_log(
            session.get("admin_id"),
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

@admin_bp.route('/add_policy', methods=['POST'])
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

        add_log(
            session.get("admin_id"),
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
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT p.poli_id,
                   p.cat_id,
                   c.cat_name,
                   p.poli_type,
                   p.rule_value,
                   p.poli_desc,
                   p.created_at
            FROM eerm_poli p
            JOIN eerm_expcat c ON p.cat_id = c.cat_id
        """)
        policies = cursor.fetchall()
        cursor.execute("SELECT cat_id, cat_name FROM eerm_expcat")
        categories = cursor.fetchall()
        return render_template('admin/admin_viewpoli.html', policies=policies, categories=categories)
    except Exception as e:
        print("Error fetching policies:", e)
        return "Error fetching policies"
    finally:
        cursor.close()

@admin_bp.route('/update_policy', methods=['POST'])
@login_required
def update_policy():
    cursor = conn.cursor()
    try:
        poli_id = request.form['poli_id']
        poli_type = request.form['poli_type']
        exp_cat = request.form['exp_cat']
        poli_rule = request.form['poli_rule']
        poli_desc = request.form['poli_desc']

        cursor.execute("""
            UPDATE eerm_poli SET 
                poli_type=%s, 
                cat_id=%s, 
                rule_value=%s, 
                poli_desc=%s
            WHERE poli_id=%s
        """, (poli_type, exp_cat, poli_rule, poli_desc, poli_id))

        add_log(
            session.get("admin_id"),
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
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM eerm_poli WHERE poli_id=%s", (poli_id,))
        add_log(
            session.get("admin_id"),
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
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM eerm_users where user_role != 'Admin'")
        users = cursor.fetchall()
        cursor.execute("SELECT DISTINCT user_role FROM eerm_users")
        return render_template('admin/admin_manusers.html', users=users)
    except Exception as e:
        print("Error fetching users:", e)
        return "Error fetching users"
    finally:
        cursor.close()

@admin_bp.route('/update_user', methods=['POST'])
@login_required
def update_user():
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
            session.get("admin_id"),
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

@admin_bp.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM eerm_users WHERE user_id = %s", (user_id,))
        add_log(
            session.get("admin_id"),
            "DELETE",
            "USER",
            user_id,
            f"Deleted User ID {user_id}"
        )
        conn.commit()
        msg = "User deleted successfully"
        return redirect(url_for('admin.manusers', msg=msg))
    except Exception as e:
        print("Error deleting user:", e)
        return "Error deleting user"
    finally:
        cursor.close()


@admin_bp.route('/viewlogs')
@login_required
def viewlogs():
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



