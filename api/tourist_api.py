from flask import Blueprint, request, jsonify
from ai_core.vector_milvus import search_relevant_context
from ai_core.llm_chat import get_guide_answer
from ai_core.tts_edgetts import text_to_audio
from database.db_crud import add_interact_record
import os

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
    know_text = search_relevant_context(question)
    # 2.大模型生成回答
    ans_text = get_guide_answer(question)
    # 3.生成语音
    audio_path = text_to_audio(ans_text)
    # 4.存入交互记录
    add_interact_record(question, ans_text, "中性")
    return jsonify({
        "code": 200,
        "data": {
            "answer": ans_text,
            "emotion": "中性",
            "audio_url": audio_path,
            "mouth_sync_info": "同步口型序列（数字人驱动使用）"
        }
    })