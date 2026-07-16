from flask import Blueprint, request, jsonify
from ai_core.vector_milvus import search_knowledge
from ai_core.llm_chat import llm_answer
from ai_core.tts_edgetts import text_to_audio
from database.db_crud import add_interact_record
# from database.db_crud import add_chat_record, get_all_kb_docs
tourist_bp = Blueprint("tourist", __name__)

# 文本问答接口
@tourist_bp.route("/text_chat", methods=["POST"])
def text_chat():
    data = request.json
    question = data.get("question", "")
    user_tag = data.get("tag", "通用游客")
    if not question:
        return jsonify({"code": 400, "msg": "问题不能为空"})
    # 1.检索知识库
    know_text = search_knowledge(question)
    # 2.大模型生成回答
    ans_text, emotion = llm_answer(question, know_text, user_tag)
    # 3.生成语音
    audio_path = text_to_audio(ans_text)
    # 4.存入交互记录
    add_interact_record(question, ans_text, emotion)
    return jsonify({
        "code": 200,
        "data": {
            "answer": ans_text,
            "emotion": emotion,       # 传给数字人控制表情
            "audio_url": audio_path,
            "mouth_sync_info": "同步口型序列（数字人驱动使用）"
        }
    })