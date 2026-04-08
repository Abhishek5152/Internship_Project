import pymysql
from flask import g
from dotenv import load_dotenv
import os

load_dotenv()

def get_db_connection():
    if 'db_connection' not in g:
        g.db_connection = pymysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            autocommit=False
        )
    return g.db_connection

def close_db_connection(e=None):
    db_connection = g.pop('db_connection', None)
    if db_connection is not None:
        db_connection.close()