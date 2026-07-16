import pymysql
from config import MYSQL_CONFIG

def get_mysql_conn():
    conn = pymysql.connect(
        host=MYSQL_CONFIG["host"],
        port=MYSQL_CONFIG["port"],
        user=MYSQL_CONFIG["user"],
        password=MYSQL_CONFIG["password"],
        database=MYSQL_CONFIG["database"],
        charset=MYSQL_CONFIG["charset"]
    )
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    return conn, cursor

def close_conn(conn, cursor):
    cursor.close()
    conn.close()