from flask import Blueprint, request, jsonify
from database.db_crud import (
    get_all_knowledge, add_knowledge, update_knowledge, delete_knowledge,
    get_digital_human_config, save_dh_config, get_interact_stat
)
from ai_core.vector_milvus import get_text_embedding, get_client, COLLECTION_NAME

admin_bp = Blueprint("admin", __name__)


# 1. 知识库-获取全部景点资料
@admin_bp.route("/knowledge/list", methods=["GET"])
def knowledge_list():
    data_list = get_all_knowledge()
    return jsonify({"code": 200, "data": data_list})


# 2. 知识库-新增景点资料（同步写入Milvus向量库）
@admin_bp.route("/knowledge/add", methods=["POST"])
def knowledge_add():
    req = request.json
    content = req.get("content", "")
    tag = req.get("tag", "通用")
    if not content:
        return jsonify({"code": 400, "msg": "讲解内容不能为空"})

    # 写入MySQL
    new_id = add_knowledge(content, tag)

    # 同步写入Milvus向量库
    try:
        vec = get_text_embedding([content])[0]
        get_client().insert(
            collection_name=COLLECTION_NAME,
            data=[{"text": content, "vector": vec}]
        )
    except Exception as e:
        print(f"向量库写入失败: {e}")

    return jsonify({"code": 200, "msg": "新增成功", "id": new_id})


# 3. 知识库-编辑景点资料
@admin_bp.route("/knowledge/update", methods=["POST"])
def knowledge_update():
    req = request.json
    kid = req.get("id")
    content = req.get("content")
    tag = req.get("tag")
    if not kid or not content:
        return jsonify({"code": 400, "msg": "参数缺失"})

    update_knowledge(kid, content, tag)

    # 更新向量库（简易方案：删除重插）
    try:
        get_client().delete(collection_name=COLLECTION_NAME, filter=f"id == {kid}")
        vec = get_text_embedding([content])[0]
        get_client().insert(
            collection_name=COLLECTION_NAME,
            data=[{"id": kid, "text": content, "vector": vec}]
        )
    except Exception as e:
        print(f"向量库更新失败: {e}")

    return jsonify({"code": 200, "msg": "修改成功"})


# 4. 知识库-删除景点资料
@admin_bp.route("/knowledge/del", methods=["POST"])
def knowledge_del():
    kid = request.json.get("id")
    if not kid:
        return jsonify({"code": 400, "msg": "缺少ID"})

    delete_knowledge(kid)

    # 删除向量库对应数据
    try:
        get_client().delete(collection_name=COLLECTION_NAME, filter=f"id == {kid}")
    except Exception as e:
        print(f"向量库删除失败: {e}")

    return jsonify({"code": 200, "msg": "删除成功"})


# 5. 数字人配置-获取当前配置
@admin_bp.route("/dh/config/get", methods=["GET"])
def dh_config_get():
    cfg = get_digital_human_config()
    return jsonify({"code": 200, "data": cfg})


# 6. 数字人配置-保存修改
@admin_bp.route("/dh/config/save", methods=["POST"])
def dh_config_save():
    req = request.json
    save_dh_config(
        dh_name=req.get("dh_name"),
        voice=req.get("voice"),
        style=req.get("style")
    )
    return jsonify({"code": 200, "msg": "数字人配置保存成功"})


# 7. 运营数据统计接口（大屏）
@admin_bp.route("/stat/interact", methods=["GET"])
def stat_interact():
    days = request.args.get("days", 7, type=int)
    stat_data = get_interact_stat(days)
    return jsonify({"code": 200, "data": stat_data})