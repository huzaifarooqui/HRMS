import mysql.connector
from mysql.connector import pooling
from flask import current_app

_pool=None

def init_pool(app):
    global _pool
    _pool=pooling.MySQLConnectionPool(pool_name="game_pool",pool_size=8,pool_reset_session=True,
        host=app.config["DB_HOST"],port=app.config["DB_PORT"],database=app.config["DB_NAME"],
        user=app.config["DB_USER"],password=app.config["DB_PASSWORD"],autocommit=False)

def get_db():
    if _pool is None: raise RuntimeError("Database pool not initialized")
    return _pool.get_connection()

def query(sql,params=(),one=False,commit=False):
    cnx=get_db(); cur=cnx.cursor(dictionary=True)
    try:
        cur.execute(sql,params)
        if commit:
            cnx.commit(); return cur.lastrowid
        rows=cur.fetchall(); return (rows[0] if rows else None) if one else rows
    except Exception:
        cnx.rollback(); raise
    finally:
        cur.close(); cnx.close()
