# 数据库连接测试文档
import pymysql
from config import MYSQL_CONFIG

def get_conn():
    # 获取数据库连接
    conn = pymysql.connect(
        host=MYSQL_CONFIG["host"],
        port=MYSQL_CONFIG["port"],
        user=MYSQL_CONFIG["user"],
        password=MYSQL_CONFIG["password"],
        database=MYSQL_CONFIG["database"],
        charset=MYSQL_CONFIG["charset"]
    )
    cursor = conn.cursor()
    return conn, cursor

def close_conn(conn, cursor):
    # 关闭游标和连接
    if cursor:
        cursor.close()
    if conn:
        conn.close()

# 本地测试连接是否正常
if __name__ == "__main__":
    try:
        conn, cur = get_conn()
        print("数据库连接成功！表创建正常")
        close_conn(conn, cur)
    except Exception as e:
        print("连接失败，检查config里账号密码/MySQL服务是否开启：", e)