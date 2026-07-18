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

def update_last_record_emotion(emotion_tag: str):
    """更新最近一条对话记录的情感标签（游客真实反馈）"""
    conn, cur = get_conn()
    cur.execute("SELECT id FROM chat_record ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE chat_record SET emotion_tag=%s WHERE id=%s", (emotion_tag, row[0]))
        conn.commit()
    close_conn(conn, cur)

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

# ====================== 10. 情感分析报告 ======================
def get_emotion_report(days: int = 7):
    """获取最近N天的情感分布"""
    conn, cur = get_conn()
    sql = """
        SELECT emotion_tag, COUNT(*) as count
        FROM chat_record
        WHERE visit_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        GROUP BY emotion_tag
    """
    cur.execute(sql, (days,))
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    res = [dict(zip(cols, r)) for r in rows]
    close_conn(conn, cur)
    return res


# ====================== 11. 热门问答 ======================
def get_hot_questions(days: int = 7, top_n: int = 10):
    """获取最近N天的高频问题"""
    conn, cur = get_conn()
    sql = """
        SELECT user_input, COUNT(*) as freq
        FROM chat_record
        WHERE visit_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        GROUP BY user_input
        ORDER BY freq DESC
        LIMIT %s
    """
    cur.execute(sql, (days, top_n))
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    res = [dict(zip(cols, r)) for r in rows]
    close_conn(conn, cur)
    return res


# ====================== 12. 数据大屏概览 ======================
def get_dashboard_data():
    conn, cur = get_conn()

    cur.execute("SELECT SUM(chat_count) as total_chats, SUM(user_count) as total_users FROM daily_visit_stat")
    total = dict(zip([desc[0] for desc in cur.description], cur.fetchone()))

    cur.execute("SELECT COALESCE(SUM(chat_count),0) as today_chats FROM daily_visit_stat WHERE visit_date = CURDATE()")
    today_chats = cur.fetchone()[0]

    cur.execute("""
        SELECT COALESCE(SUM(chat_count),0) as week_chats
        FROM daily_visit_stat
        WHERE visit_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
    """)
    week_chats = cur.fetchone()[0]

    cur.execute("""
        SELECT emotion_tag, COUNT(*) as count
        FROM chat_record WHERE visit_date = CURDATE()
        GROUP BY emotion_tag
    """)
    today_emotion = [dict(zip([desc[0] for desc in cur.description], r)) for r in cur.fetchall()]

    cur.execute("""
        SELECT user_input, COUNT(*) as freq
        FROM chat_record WHERE visit_date = CURDATE()
        GROUP BY user_input ORDER BY freq DESC LIMIT 5
    """)
    today_hot = [dict(zip([desc[0] for desc in cur.description], r)) for r in cur.fetchall()]

    cur.execute("SELECT visit_date, chat_count FROM daily_visit_stat ORDER BY visit_date DESC LIMIT 7")
    weekly_trend = [dict(zip([desc[0] for desc in cur.description], r)) for r in cur.fetchall()]

    cur.execute("""
        SELECT visit_date,
            ROUND(COUNT(CASE WHEN emotion_tag='正面' THEN 1 END) / COUNT(*) * 100, 1) as satisfaction_rate
        FROM chat_record
        WHERE visit_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        GROUP BY visit_date
        ORDER BY visit_date DESC
    """)
    satisfaction_trend = [dict(zip([desc[0] for desc in cur.description], r)) for r in cur.fetchall()]

    close_conn(conn, cur)

    return {
        "total_chats": total.get("total_chats", 0) or 0,
        "total_users": total.get("total_users", 0) or 0,
        "today_chats": today_chats,
        "week_chats": week_chats,
        "today_emotion": today_emotion,
        "today_hot_questions": today_hot,
        "weekly_trend": weekly_trend,
        "satisfaction_trend": satisfaction_trend,
    }


def get_focus_analysis(days: int = 7):
    """分析游客关注点：从对话记录中提取高频关键词分类"""
    conn, cur = get_conn()
    cur.execute("""
        SELECT user_input FROM chat_record
        WHERE visit_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
    """, (days,))
    rows = cur.fetchall()
    close_conn(conn, cur)

    focus_keywords = {
        "景点介绍": ["景点", "介绍", "有什么", "哪里", "地方", "景区", "灵山", "梵宫", "大佛", "九龙", "祥符", "禅意", "小镇"],
        "交通路线": ["交通", "路线", "怎么走", "地铁", "公交", "停车", "开车", "导航", "多远", "多久"],
        "门票价格": ["门票", "价格", "多少钱", "优惠", "免费", "票", "学生", "老人", "儿童"],
        "开放时间": ["时间", "开放", "关门", "几点", "营业", "早上", "晚上"],
        "餐饮住宿": ["吃饭", "餐厅", "美食", "住宿", "酒店", "住", "吃", "特色"],
        "游览建议": ["推荐", "路线", "攻略", "怎么玩", "最佳", "必看", "顺序", "安排"],
        "历史文化": ["历史", "文化", "故事", "传说", "佛教", "建造", "年代", "意义"],
        "其他": []
    }

    focus_count = {k: 0 for k in focus_keywords}
    total = 0
    for row in rows:
        text = row[0].lower()
        total += 1
        matched = False
        for category, keywords in focus_keywords.items():
            if category == "其他":
                continue
            for kw in keywords:
                if kw in text:
                    focus_count[category] += 1
                    matched = True
                    break
            if matched:
                break
        if not matched:
            focus_count["其他"] += 1

    result = []
    for cat, count in sorted(focus_count.items(), key=lambda x: -x[1]):
        if count > 0:
            result.append({"focus": cat, "count": count, "percent": round(count/total*100, 1) if total > 0 else 0})
    return result


def get_emotion_trend(days: int = 7):
    """获取每日情感趋势"""
    conn, cur = get_conn()
    sql = """
        SELECT visit_date,
            COUNT(*) as total,
            COUNT(CASE WHEN emotion_tag='正面' THEN 1 END) as positive,
            COUNT(CASE WHEN emotion_tag='中性' THEN 1 END) as neutral,
            COUNT(CASE WHEN emotion_tag='负面' THEN 1 END) as negative
        FROM chat_record
        WHERE visit_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        GROUP BY visit_date
        ORDER BY visit_date ASC
    """
    cur.execute(sql, (days,))
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    res = [dict(zip(cols, r)) for r in rows]
    close_conn(conn, cur)
    return res


def generate_service_suggestions(days: int = 7):
    """根据数据生成服务建议"""
    conn, cur = get_conn()

    cur.execute("""
        SELECT COUNT(*) as total FROM chat_record WHERE visit_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
    """, (days,))
    total = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) as neg FROM chat_record
        WHERE visit_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY) AND emotion_tag='负面'
    """, (days,))
    neg = cur.fetchone()[0]

    cur.execute("""
        SELECT user_input, COUNT(*) as freq FROM chat_record
        WHERE visit_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        GROUP BY user_input ORDER BY freq DESC LIMIT 3
    """, (days,))
    top_qs = [dict(zip([desc[0] for desc in cur.description], r)) for r in cur.fetchall()]

    close_conn(conn, cur)

    suggestions = []
    if total == 0:
        suggestions.append("暂无足够数据，建议加强景区宣传引导游客使用AI导游服务")
    else:
        neg_rate = neg / total * 100
        if neg_rate > 20:
            suggestions.append(f"负面评价占比{neg_rate:.0f}%，建议优化回答质量，补充知识库内容")
        elif neg_rate > 10:
            suggestions.append(f"负面评价占比{neg_rate:.0f}%，建议关注游客不满意的问题并改进")
        else:
            suggestions.append(f"负面评价仅{neg_rate:.0f}%，服务质量良好，继续保持")

        if top_qs:
            suggestions.append(f"游客最关心的问题：{top_qs[0]['user_input']}（{top_qs[0]['freq']}次），建议完善相关知识")

        if total < 10:
            suggestions.append("对话量较少，建议在景区入口增设AI导游使用引导")
        elif total > 50:
            suggestions.append("对话量充足，可考虑增加多语言支持服务境外游客")

    return suggestions

# ====================== 测试入口 ======================
if __name__ == "__main__":
    print("=== 测试登录admin账号 ===")
    uid = admin_login("admin", "e10adc3949ba59abbe56e057f20f883e")
    print("管理员ID：", uid)

    print("\n=== 读取默认数字人配置 ===")
    human_cfg = get_default_human_config()
    print(human_cfg)