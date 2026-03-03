import pymysql
from flask import g

def get_db_connection():
    if 'db_connection' not in g:
        g.db_connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='db_eerm',
            autocommit=False
        )
    return g.db_connection

def close_db_connection(e=None):
    db_connection = g.pop('db_connection', None)
    if db_connection is not None:
        db_connection.close()