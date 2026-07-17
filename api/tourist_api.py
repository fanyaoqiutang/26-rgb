from flask import Blueprint, request, jsonify
from ai_core.vector_milvus import search_relevant_context
from ai_core.llm_chat import get_guide_answer
from ai_core.tts_edgetts import text_to_audio
from ai_core.asr_whisper import audio_file_to_text
from database.db_crud import add_interact_record
import os

tourist_bp = Blueprint("tourist", __name__)


@tourist_bp.route("/text_chat", methods=["POST"])
def text_chat():
    data = request.json
    question = data.get("question", "")
    user_tag = data.get("tag", "通用游客")
    if not question:
        return jsonify({"code": 400, "msg": "问题不能为空"})

    know_text = search_relevant_context(question)
    ans_text = get_guide_answer(question, user_tag)
    audio_path = text_to_audio(ans_text)
    emotion = analyze_emotion(ans_text)
    add_interact_record(question, ans_text, emotion)
    return jsonify({
        "code": 200,
        "data": {
            "answer": ans_text,
            "emotion": emotion,
            "audio_url": audio_path,
        }
    })


@tourist_bp.route("/voice_chat", methods=["POST"])
def voice_chat():
    if "audio" not in request.files:
        return jsonify({"code": 400, "msg": "未上传音频"})
    audio_file = request.files["audio"]
    user_tag = request.form.get("tag", "通用游客")

    audio_path = f"data/audio_cache/{audio_file.filename}"
    audio_file.save(audio_path)

    question = audio_file_to_text(audio_path)
    if not question:
        return jsonify({"code": 400, "msg": "语音识别失败"})

    ans_text = get_guide_answer(question, user_tag)
    reply_audio = text_to_audio(ans_text)
    emotion = analyze_emotion(ans_text)
    add_interact_record(question, ans_text, emotion)
    return jsonify({
        "code": 200,
        "data": {
            "question": question,
            "answer": ans_text,
            "emotion": emotion,
            "audio_url": reply_audio,
        }
    })


@tourist_bp.route("/recommend", methods=["POST"])
def recommend():
    data = request.json
    tag = data.get("tag", "")
    if not tag:
        return jsonify({"code": 400, "msg": "请提供兴趣标签"})

    prompt = f"""你是灵山景区导游，根据游客兴趣标签「{tag}」，推荐2-3条个性化游览路线，
每条路线包含：路线名称、途经景点、推荐理由。语言简洁口语化。"""

    ans_text = get_guide_answer(prompt, tag)
    audio_path = text_to_audio(ans_text)
    return jsonify({
        "code": 200,
        "data": {"answer": ans_text, "audio_url": audio_path}
    })


def analyze_emotion(text: str) -> str:
    positive_words = ["欢迎", "美丽", "精彩", "推荐", "棒", "好", "赞", "喜欢", "开心"]
    negative_words = ["抱歉", "遗憾", "无法", "没有", "不足", "差"]
    pos = sum(1 for w in positive_words if w in text)
    neg = sum(1 for w in negative_words if w in text)
    if pos > neg:
        return "正面"
    elif neg > pos:
        return "负面"
    return "中性"
