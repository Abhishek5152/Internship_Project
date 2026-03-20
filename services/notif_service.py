from database import get_db_connection


def create_notif(
    user_id,
    message,
    notif_type='system_alert',
    actor_id=None,
    reference_id=None,
    reference_table=None,
    priority='normal',
    channel='in_app'
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO eerm_notifs
            (user_id, actor_id, notif_type, message,
             reference_id, reference_table, priority, channel)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            user_id,
            actor_id,
            notif_type,
            message,
            reference_id,
            reference_table,
            priority,
            channel
        ))

        conn.commit()

    except Exception as e:
        print("Error creating notification:", e)

    finally:
        cursor.close()

def manager_broadcast(
    message,
    notif_type='system_alert',
    actor_id=None,
    priority='normal',
    channel='in_app'
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT user_id FROM eerm_users WHERE user_role='Manager'")

        managers = cursor.fetchall()

        data = []
        for manager in managers:
            user_id = manager[0]

            data.append((
                user_id,
                actor_id,
                notif_type,
                message,
                None,  
                None,
                priority,
                channel
            ))

        query = """
            INSERT INTO eerm_notifs
            (user_id, actor_id, notif_type, message,
             reference_id, reference_table, priority, channel)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.executemany(query,data)

        conn.commit()

    except Exception as e:
        print("Error creating notification:", e)

    finally:
        cursor.close()