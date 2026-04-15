import os
import pymysql
import psycopg2
from urllib.parse import urlparse
from flask import g

def get_db_connection():
    if 'db_connection' not in g:

        DATABASE_URL = os.getenv("DATABASE_URL")

        # If Railway (PostgreSQL)
        if DATABASE_URL:
            g.db_connection = psycopg2.connect(DATABASE_URL)

        # Else local MySQL
        else:
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