from database.mysql_conn import get_mysql_conn, close_conn
import time
from datetime import datetime

# ========== 知识库CRUD ==========
def get_all_knowledge():
    conn, cur = get_mysql_conn()
    cur.execute("SELECT id, content, tag FROM scenic_knowledge ORDER BY id DESC")
    res = cur.fetchall()
    close_conn(conn, cur)
    return res

def add_knowledge(content, tag):
    conn, cur = get_mysql_conn()
    sql = "INSERT INTO scenic_knowledge(content, tag) VALUES (%s, %s)"
    cur.execute(sql, (content, tag))
    conn.commit()
    new_id = cur.lastrowid
    close_conn(conn, cur)
    return new_id

def update_knowledge(kid, content, tag):
    conn, cur = get_mysql_conn()
    sql = "UPDATE scenic_knowledge SET content=%s, tag=%s WHERE id=%s"
    cur.execute(sql, (content, tag, kid))
    conn.commit()
    close_conn(conn, cur)

def delete_knowledge(kid):
    conn, cur = get_mysql_conn()
    sql = "DELETE FROM scenic_knowledge WHERE id=%s"
    cur.execute(sql, (kid,))
    conn.commit()
    close_conn(conn, cur)

# ========== 游客交互记录 ==========
def add_interact_record(question, answer, emotion):
    conn, cur = get_mysql_conn()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = """
    INSERT INTO interact_record(user_question, ai_answer, emotion, create_time)
    VALUES (%s, %s, %s, %s)
    """
    cur.execute(sql, (question, answer, emotion, now))
    conn.commit()
    close_conn(conn, cur)

# ========== 数字人配置 ==========
def get_digital_human_config():
    conn, cur = get_mysql_conn()
    cur.execute("SELECT dh_name, voice, style FROM digital_human_cfg LIMIT 1")
    row = cur.fetchone()
    close_conn(conn, cur)
    return row or {"dh_name": "导游小艾", "voice": "zh-CN-YunyangNeural", "style": "warm"}

def save_dh_config(dh_name, voice, style):
    conn, cur = get_mysql_conn()
    cur.execute("SELECT COUNT(*) cnt FROM digital_human_cfg")
    cnt = cur.fetchone()["cnt"]
    if cnt > 0:
        sql = "UPDATE digital_human_cfg SET dh_name=%s, voice=%s, style=%s"
        cur.execute(sql, (dh_name, voice, style))
    else:
        sql = "INSERT INTO digital_human_cfg(dh_name, voice, style) VALUES (%s,%s,%s)"
        cur.execute(sql, (dh_name, voice, style))
    conn.commit()
    close_conn(conn, cur)

# ========== 运营统计 ==========
def get_interact_stat(days=7):
    conn, cur = get_mysql_conn()
    sql = f"""
    SELECT DATE(create_time) day, COUNT(*) count
    FROM interact_record
    WHERE create_time >= DATE_SUB(NOW(), INTERVAL {days} DAY)
    GROUP BY day ORDER BY day
    """
    cur.execute(sql)
    data = cur.fetchall()
    close_conn(conn, cur)
    return data