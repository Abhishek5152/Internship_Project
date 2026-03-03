from flask import render_template, request, redirect, url_for, session
from database import get_db_connection
from utils import login_required, add_log

import cloudinary.uploader

from . import man_bp

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@man_bp.route('/mandash')
@login_required
def mandash():
    return render_template('manager/man_dashboard.html')

@man_bp.route('/manusers-m')
@login_required
def manusers_m():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id, user_name, user_email, user_role, created_at, user_status FROM eerm_users where user_role = 'Employee'")
        users = cursor.fetchall()
        return render_template('manager/man_manusers.html', users=users)
    except Exception as e:
        print("Error fetching users:", e)
        return "Error fetching users"
    finally:
        cursor.close()
        

@man_bp.route('/toggle_user_status/<int:user_id>', methods=['POST'])
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

        if new_status == 'Inactive':
            cursor.execute("UPDATE eerm_users SET user_status = 'Inactive' WHERE user_id = %s", (user_id,))
        else:
            cursor.execute("UPDATE eerm_users SET user_status = 'Active' WHERE user_id = %s", (user_id,))
        conn.commit()

        add_log(
            conn,
            session.get("user_id"),
            "TOGGLE",
            "USER",
            user_id,
            f"Changed user status to {new_status}"
        )

        msg = f"User status changed to {new_status}"
        return redirect(url_for('manager.manusers_m', msg=msg))

    except Exception as e:
        print("Error toggling user status:", e)
        return "Error toggling user status"

    finally:
        cursor.close()
        

@man_bp.route('/viewreq')
@login_required
def viewreq():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT r.req_id,
                   r.user_id,
                   u.user_name,
                   r.res_id,
                   c.res_name,
                   r.req_date,
                   r.req_status
            FROM eerm_req r 
            JOIN eerm_users u ON r.user_id = u.user_id
            JOIN eerm_res c ON r.res_id = c.res_id
            where r.req_status = 'Pending'
        """)
        requests = cursor.fetchall()
        return render_template('manager/man_viewreq.html', requests=requests)
    except Exception as e:
        print("Error fetching requests:", e)
        return "Error fetching requests"
    finally:
        cursor.close()
        

@man_bp.route('/reqapprove/<int:req_id>', methods=['POST'])
@login_required
def reqapprove(req_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE eerm_req SET req_status = 'Approved' WHERE req_id = %s", (req_id,))
        cursor.execute("""
            INSERT INTO eerm_alloc (res_id, user_id, alloc_date, ret_date)
            SELECT res_id, 
            user_id, 
            NOW(), 
            DATE_ADD(NOW(), INTERVAL 30 DAY)
            FROM eerm_req 
            WHERE req_id = %s
        """, (req_id,))
        conn.commit()
        add_log(
            conn,
            session.get("user_id"),
            "APPROVE",
            "REQUEST",
            req_id,
            f"Approved request with ID {req_id}"
        )
        msg = "Request approved successfully"
        return redirect(url_for('manager.viewreq', msg=msg))
    except Exception as e:
        print("Error approving request:", e)
        return "Error approving request"
    finally:
        cursor.close()
        

@man_bp.route('/reqreject/<int:req_id>', methods=['POST'])
@login_required
def reqreject(req_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE eerm_req SET req_status = 'Rejected' WHERE req_id = %s", (req_id,))
        conn.commit()
        add_log(
            conn,
            session.get("user_id"),
            "REJECT",
            "REQUEST",
            req_id,
            f"Rejected request with ID {req_id}"
        )
        msg = "Request rejected successfully"
        return redirect(url_for('manager.viewreq', msg=msg))
    except Exception as e:
        print("Error rejecting request:", e)
        return "Error rejecting request"
    finally:
        cursor.close()
        

@man_bp.route('/reqhistory')
@login_required
def reqhistory():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT r.req_id,
                   r.user_id,
                   u.user_name,
                   r.res_id,
                   c.res_name,
                   r.req_date,
                   r.req_status
            FROM eerm_req r 
            JOIN eerm_users u ON r.user_id = u.user_id
            JOIN eerm_res c ON r.res_id = c.res_id
            where r.req_status != 'Pending'
        """)
        requests = cursor.fetchall()
        return render_template('manager/man_reqhistory.html', requests=requests)
    except Exception as e:
        print("Error fetching request history:", e)
        return "Error fetching request history"
    finally:
        cursor.close()

@man_bp.route('/upload_profile_photo', methods=['POST'])
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

        return redirect(url_for('manager.man_mngprof'))

    finally:
        cursor.close() 
        
    
@man_bp.route('/man_mngprof')
@login_required
def man_mngprof():
    user_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, user_name, user_email, user_contact, user_address, user_about, user_img_url FROM eerm_users WHERE user_id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    
    return render_template('manager/man_mngprof.html', user_data=user_data)

@man_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    conn = get_db_connection()
    user_id = session.get('user_id')
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
            return redirect(url_for('manager.man_mngprof', msg=msg))
        else:
            cursor.execute("SELECT user_id, user_name, user_email, user_contact, user_address, user_about FROM eerm_users WHERE user_id = %s", (user_id,))
            user_data = cursor.fetchone()
            return render_template('manager/man_edit_profile.html', user_data=user_data)
    except Exception as e:
        print("Error updating profile:", e)
        return "Error updating profile"
    finally:
        cursor.close()
        
