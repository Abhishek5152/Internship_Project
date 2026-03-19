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