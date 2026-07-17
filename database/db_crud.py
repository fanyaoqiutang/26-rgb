from database.mysql_conn import get_conn, close_conn
from datetime import date, datetime

# ====================== 1. 管理员 admin_user 相关 ======================
def admin_login(username: str, password: str):
    """校验管理员账号密码，存在返回用户id，不存在返回None"""
    conn, cur = get_conn()
    sql = "SELECT id FROM admin_user WHERE username=%s AND password=%s"
    cur.execute(sql, (username, password))
    res = cur.fetchone()
    close_conn(conn, cur)
    if res:
        return res[0]
    return None

# ====================== 2. 知识库 kb_document 相关 ======================
def add_kb_doc(title: str, content: str, category: str = "景点介绍"):
    """新增知识库文档"""
    conn, cur = get_conn()
    sql = "INSERT INTO kb_document (doc_title, doc_content, category) VALUES (%s, %s, %s)"
    cur.execute(sql, (title, content, category))
    conn.commit()
    doc_id = cur.lastrowid
    close_conn(conn, cur)
    return doc_id

def get_all_kb_docs():
    """查询全部知识库文档"""
    conn, cur = get_conn()
    sql = "SELECT id, doc_title, doc_content, category, create_time FROM kb_document ORDER BY create_time DESC"
    cur.execute(sql)
    res = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    data = [dict(zip(cols, row)) for row in res]
    close_conn(conn, cur)
    return data

def del_kb_doc(doc_id: int):
    """删除单条知识库文档"""
    conn, cur = get_conn()
    sql = "DELETE FROM kb_document WHERE id=%s"
    cur.execute(sql, (doc_id,))
    conn.commit()
    close_conn(conn, cur)
    return True

def get_kb_doc_by_id(doc_id: int):
    """根据id获取单篇文档详情"""
    conn, cur = get_conn()
    sql = "SELECT * FROM kb_document WHERE id=%s"
    cur.execute(sql, (doc_id,))
    row = cur.fetchone()
    cols = [desc[0] for desc in cur.description]
    close_conn(conn, cur)
    if row:
        return dict(zip(cols, row))
    return None

# ====================== 3. 游客对话记录 chat_record 相关 ======================
def add_chat_record(user_input: str, ai_answer: str, emotion_tag: str = "中性"):
    """新增一条对话记录，自动记录当天日期"""
    today = date.today()
    conn, cur = get_conn()
    sql = """
    INSERT INTO chat_record (user_input, ai_answer, emotion_tag, visit_date)
    VALUES (%s, %s, %s, %s)
    """
    cur.execute(sql, (user_input, ai_answer, emotion_tag, today))
    conn.commit()
    record_id = cur.lastrowid
    close_conn(conn, cur)
    # 新增对话后，当日对话计数+1
    incr_daily_chat_count(today)
    return record_id

def get_all_chat_records():
    """查询所有对话日志"""
    conn, cur = get_conn()
    sql = "SELECT * FROM chat_record ORDER BY create_time DESC"
    cur.execute(sql)
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    res = [dict(zip(cols, r)) for r in rows]
    close_conn(conn, cur)
    return res

# ====================== 4. 每日访问统计 daily_visit_stat 相关 ======================
def incr_daily_chat_count(visit_date: date):
    """当日对话次数 +1，不存在则新建一条记录"""
    conn, cur = get_conn()
    cur.execute("SELECT id FROM daily_visit_stat WHERE visit_date=%s", (visit_date,))
    row = cur.fetchone()
    if row:
        sql = "UPDATE daily_visit_stat SET chat_count=chat_count+1, update_time=NOW() WHERE visit_date=%s"
        cur.execute(sql, (visit_date,))
    else:
        sql = "INSERT INTO daily_visit_stat (visit_date, chat_count, user_count) VALUES (%s, 1, 0)"
        cur.execute(sql, (visit_date,))
    conn.commit()
    close_conn(conn, cur)

def get_daily_stat_list():
    """获取全部日期统计数据，用于大屏图表"""
    conn, cur = get_conn()
    sql = "SELECT * FROM daily_visit_stat ORDER BY visit_date ASC"
    cur.execute(sql)
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    res = [dict(zip(cols, r)) for r in rows]
    close_conn(conn, cur)
    return res

# ====================== 5. 数字人配置 digital_human_config 相关 ======================
def get_default_human_config():
    """获取默认启用的数字人配置"""
    conn, cur = get_conn()
    sql = "SELECT * FROM digital_human_config WHERE is_default=1 LIMIT 1"
    cur.execute(sql)
    row = cur.fetchone()
    cols = [desc[0] for desc in cur.description]
    close_conn(conn, cur)
    if row:
        return dict(zip(cols, row))
    return None

def update_human_config(config_id: int, config_name: str, face_path: str, voice_type: str, costume: str):
    """修改数字人配置"""
    conn, cur = get_conn()
    sql = """
    UPDATE digital_human_config
    SET config_name=%s, face_image_path=%s, voice_type=%s, costume_style=%s
    WHERE id=%s
    """
    cur.execute(sql, (config_name, face_path, voice_type, costume, config_id))
    conn.commit()
    close_conn(conn, cur)
    return True

# ====================== 6. 知识库管理（admin_api 使用）======================
def get_all_knowledge():
    """获取全部知识库文档（别名）"""
    return get_all_kb_docs()

def add_knowledge(content: str, tag: str = "通用"):
    """新增知识库文档"""
    return add_kb_doc(title=content[:50] if len(content) > 50 else content, content=content, category=tag)

def update_knowledge(kid: int, content: str, tag: str = "通用"):
    """更新知识库文档"""
    conn, cur = get_conn()
    sql = "UPDATE kb_document SET doc_title=%s, doc_content=%s, category=%s WHERE id=%s"
    title = content[:50] if len(content) > 50 else content
    cur.execute(sql, (title, content, tag, kid))
    conn.commit()
    close_conn(conn, cur)
    return True

def delete_knowledge(kid: int):
    """删除知识库文档"""
    return del_kb_doc(kid)

# ====================== 7. 数字人配置（admin_api 使用）======================
def get_digital_human_config():
    """获取数字人配置（别名）"""
    return get_default_human_config()

def save_dh_config(dh_name: str, voice: str, style: str):
    """保存数字人配置"""
    conn, cur = get_conn()
    sql = "UPDATE digital_human_config SET config_name=%s, voice_type=%s, costume_style=%s WHERE is_default=1"
    cur.execute(sql, (dh_name, voice, style))
    conn.commit()
    close_conn(conn, cur)
    return True

# ====================== 8. 统计接口（admin_api 使用）======================
def get_interact_stat(days: int = 7):
    """获取最近N天的交互统计"""
    conn, cur = get_conn()
    sql = """
        SELECT visit_date, chat_count, user_count
        FROM daily_visit_stat
        WHERE visit_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        ORDER BY visit_date ASC
    """
    cur.execute(sql, (days,))
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    res = [dict(zip(cols, r)) for r in rows]
    close_conn(conn, cur)
    return res

# ====================== 9. 交互记录（tourist_api 使用）======================
def add_interact_record(user_input: str, ai_answer: str, emotion_tag: str = "中性"):
    """新增交互记录（别名）"""
    return add_chat_record(user_input, ai_answer, emotion_tag)

# ====================== 测试入口 ======================
if __name__ == "__main__":
    print("=== 测试登录admin账号 ===")
    uid = admin_login("admin", "e10adc3949ba59abbe56e057f20f883e")
    print("管理员ID：", uid)

    print("\n=== 读取默认数字人配置 ===")
    human_cfg = get_default_human_config()
    print(human_cfg)