from flask import Blueprint, request, jsonify, session
from database.db_crud import (
    admin_login,
    get_all_knowledge, add_knowledge, update_knowledge, delete_knowledge,
    get_digital_human_config, save_dh_config, get_interact_stat,
    get_emotion_report, get_hot_questions, get_dashboard_data,
    get_focus_analysis, get_emotion_trend, generate_service_suggestions
)
from ai_core.vector_milvus import get_text_embedding, client, COLLECTION_NAME
import hashlib

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/login", methods=["POST"])
def login():
    req = request.json
    username = req.get("username", "")
    password = req.get("password", "")
    pwd_md5 = hashlib.md5(password.encode()).hexdigest()
    uid = admin_login(username, pwd_md5)
    if uid:
        session["admin_id"] = uid
        return jsonify({"code": 200, "msg": "登录成功"})
    return jsonify({"code": 400, "msg": "账号密码错误"})


@admin_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("admin_id", None)
    return jsonify({"code": 200, "msg": "已退出"})


@admin_bp.route("/knowledge/list", methods=["GET"])
def knowledge_list():
    try:
        client.load_collection(collection_name=COLLECTION_NAME)
        results = client.query(
            collection_name=COLLECTION_NAME,
            filter="id > 0",
            output_fields=["id", "text"],
            limit=1000
        )
        data_list = []
        for i, item in enumerate(results):
            title = item["text"][:50] if len(item["text"]) > 50 else item["text"]
            data_list.append({
                "id": item["id"],
                "doc_title": title,
                "category": "景区知识",
                "create_time": "-"
            })
        return jsonify({"code": 200, "data": data_list})
    except Exception as e:
        print(f"读取Milvus失败: {e}")
        return jsonify({"code": 200, "data": []})


@admin_bp.route("/knowledge/add", methods=["POST"])
def knowledge_add():
    req = request.json
    content = req.get("content", "")
    tag = req.get("tag", "通用")
    if not content:
        return jsonify({"code": 400, "msg": "讲解内容不能为空"})

    new_id = add_knowledge(content, tag)

    try:
        vec = get_text_embedding([content])[0]
        client.insert(
            collection_name=COLLECTION_NAME,
            data=[{"text": content, "vector": vec}]
        )
    except Exception as e:
        print(f"向量库写入失败: {e}")

    return jsonify({"code": 200, "msg": "新增成功", "id": new_id})


@admin_bp.route("/knowledge/update", methods=["POST"])
def knowledge_update():
    req = request.json
    kid = req.get("id")
    content = req.get("content")
    tag = req.get("tag")
    if not kid or not content:
        return jsonify({"code": 400, "msg": "参数缺失"})

    update_knowledge(kid, content, tag)

    try:
        client.delete(collection_name=COLLECTION_NAME, filter=f"id == {kid}")
        vec = get_text_embedding([content])[0]
        client.insert(
            collection_name=COLLECTION_NAME,
            data=[{"id": kid, "text": content, "vector": vec}]
        )
    except Exception as e:
        print(f"向量库更新失败: {e}")

    return jsonify({"code": 200, "msg": "修改成功"})


@admin_bp.route("/knowledge/del", methods=["POST"])
def knowledge_del():
    kid = request.json.get("id")
    if not kid:
        return jsonify({"code": 400, "msg": "缺少ID"})

    try:
        delete_knowledge(kid)
    except:
        pass

    try:
        client.delete(collection_name=COLLECTION_NAME, filter=f"id == {kid}")
    except Exception as e:
        print(f"向量库删除失败: {e}")

    return jsonify({"code": 200, "msg": "删除成功"})


@admin_bp.route("/dh/config/get", methods=["GET"])
def dh_config_get():
    cfg = get_digital_human_config()
    return jsonify({"code": 200, "data": cfg})


@admin_bp.route("/dh/config/save", methods=["POST"])
def dh_config_save():
    req = request.json
    save_dh_config(
        dh_name=req.get("dh_name"),
        voice=req.get("voice"),
        style=req.get("style"),
        character_model=req.get("character_model", "HaruGreeter")
    )
    # 清除游客端缓存，使新配置立即生效
    from api.tourist_api import invalidate_dh_cache
    invalidate_dh_cache()
    return jsonify({"code": 200, "msg": "数字人配置保存成功"})


@admin_bp.route("/stat/interact", methods=["GET"])
def stat_interact():
    days = request.args.get("days", 7, type=int)
    stat_data = get_interact_stat(days)
    return jsonify({"code": 200, "data": stat_data})


@admin_bp.route("/stat/emotion", methods=["GET"])
def stat_emotion():
    days = request.args.get("days", 7, type=int)
    report = get_emotion_report(days)
    return jsonify({"code": 200, "data": report})


@admin_bp.route("/stat/hot_questions", methods=["GET"])
def stat_hot_questions():
    days = request.args.get("days", 7, type=int)
    top_n = request.args.get("top", 10, type=int)
    hot_list = get_hot_questions(days, top_n)
    return jsonify({"code": 200, "data": hot_list})


@admin_bp.route("/stat/dashboard", methods=["GET"])
def stat_dashboard():
    dashboard = get_dashboard_data()
    return jsonify({"code": 200, "data": dashboard})


@admin_bp.route("/stat/focus", methods=["GET"])
def stat_focus():
    days = request.args.get("days", 7, type=int)
    data = get_focus_analysis(days)
    return jsonify({"code": 200, "data": data})


@admin_bp.route("/stat/emotion_trend", methods=["GET"])
def stat_emotion_trend():
    days = request.args.get("days", 7, type=int)
    data = get_emotion_trend(days)
    return jsonify({"code": 200, "data": data})


@admin_bp.route("/stat/suggestions", methods=["GET"])
def stat_suggestions():
    days = request.args.get("days", 7, type=int)
    data = generate_service_suggestions(days)
    return jsonify({"code": 200, "data": data})
