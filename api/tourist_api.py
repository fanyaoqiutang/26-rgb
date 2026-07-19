from flask import Blueprint, request, jsonify
from ai_core.vector_milvus import search_relevant_context
from ai_core.llm_chat import get_guide_answer
from ai_core.tts_edgetts import text_to_audio
from ai_core.asr_whisper import audio_file_to_text
from database.db_crud import add_interact_record
from config import BASE_DIR
import os
import threading

tourist_bp = Blueprint("tourist", __name__)

_dh_config_cache = None

def get_dh_config():
    global _dh_config_cache
    if _dh_config_cache is None:
        _dh_config_cache = get_digital_human_config() or {}
    return _dh_config_cache

def invalidate_dh_cache():
    global _dh_config_cache
    _dh_config_cache = None


def _async_generate_audio(ans_text: str, voice: str, question: str, emotion: str):
    """后台线程生成音频并记录交互"""
    try:
        text_to_audio(ans_text, voice=voice)
        add_interact_record(question, ans_text, emotion)
    except Exception as e:
        print(f"[async_audio] 异常: {e}")


@tourist_bp.route("/text_chat", methods=["POST"])
def text_chat():
    data = request.json
    question = data.get("question", "")
    user_tag = data.get("tag", "通用游客")
    if not question:
        return jsonify({"code": 400, "msg": "问题不能为空"})

    try:
        ans_text = get_guide_answer(question, user_tag)
        emotion = analyze_emotion(ans_text)

        cfg = get_dh_config()
        voice = cfg.get("voice_type")

        threading.Thread(target=_async_generate_audio, args=(ans_text, voice, question, emotion), daemon=True).start()

        return jsonify({
            "code": 200,
            "data": {
                "answer": ans_text,
                "emotion": emotion,
                "audio_url": None,
            }
        })
    except Exception as e:
        print(f"[text_chat] 异常: {e}")
        import traceback; traceback.print_exc()
        return jsonify({"code": 500, "msg": f"服务异常: {str(e)}"})


@tourist_bp.route("/voice_chat", methods=["POST"])
def voice_chat():
    if "audio" not in request.files:
        return jsonify({"code": 400, "msg": "未上传音频"})
    audio_file = request.files["audio"]
    user_tag = request.form.get("tag", "通用游客")

    os.makedirs(os.path.join(BASE_DIR, "data", "audio_cache"), exist_ok=True)
    audio_path = os.path.join(BASE_DIR, "data", "audio_cache", audio_file.filename)
    audio_file.save(audio_path)

    try:
        question = audio_file_to_text(audio_path)
    except Exception as e:
        print(f"语音识别异常: {e}")
        return jsonify({"code": 400, "msg": f"语音识别失败: {str(e)}"})

    if not question:
        return jsonify({"code": 400, "msg": "语音识别失败"})

    try:
        ans_text = get_guide_answer(question, user_tag)
        emotion = analyze_emotion(ans_text)

        cfg = get_dh_config()
        voice = cfg.get("voice_type")

        threading.Thread(target=_async_generate_audio, args=(ans_text, voice, question, emotion), daemon=True).start()

        return jsonify({
            "code": 200,
            "data": {
                "question": question,
                "answer": ans_text,
                "emotion": emotion,
                "audio_url": None,
            }
        })
    except Exception as e:
        print(f"[voice_chat] 异常: {e}")
        return jsonify({"code": 500, "msg": f"服务异常: {str(e)}"})


@tourist_bp.route("/recommend", methods=["POST"])
def recommend():
    data = request.json
    tag = data.get("tag", "")
    if not tag:
        return jsonify({"code": 400, "msg": "请提供兴趣标签"})

    prompt = f"""你是灵山景区导游，根据游客兴趣标签「{tag}」，推荐2-3条个性化游览路线，
每条路线包含：路线名称、途经景点、推荐理由。语言简洁口语化。"""

    try:
        ans_text = get_guide_answer(prompt, tag)
        cfg = get_dh_config()
        voice = cfg.get("voice_type")
        threading.Thread(target=_async_generate_audio, args=(ans_text, voice, "", "正面"), daemon=True).start()
        return jsonify({
            "code": 200,
            "data": {"answer": ans_text, "audio_url": None}
        })
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务异常: {str(e)}"})


@tourist_bp.route("/feedback", methods=["POST"])
def feedback():
    data = request.json
    emotion = data.get("emotion", "中性")
    from database.db_crud import update_last_record_emotion
    update_last_record_emotion(emotion)
    return jsonify({"code": 200, "msg": "感谢反馈"})


@tourist_bp.route("/dh_config", methods=["GET"])
def dh_config():
    """游客端获取当前数字人配置（角色+音色）"""
    cfg = get_dh_config()
    return jsonify({
        "code": 200,
        "data": {
            "name": cfg.get("config_name", "AI导游小灵"),
            "voice": cfg.get("voice_type", "zh-CN-XiaoyiNeural"),
            "costume": cfg.get("costume_style", "职业正装"),
            "character_model": cfg.get("character_model", "HaruGreeter"),
        }
    })


def analyze_emotion(text: str) -> str:
    positive_words = ["欢迎", "美丽", "精彩", "推荐", "棒", "好", "赞", "喜欢", "开心"]
    negative_words = ["抱歉", "遗憾", "无法", "没有", "不足", "差"]
    pos = sum(1 for w in positive_words if w in text)
    neg = sum(1 for w in negative_words in w in text)
    if pos > neg:
        return "正面"
    elif neg > pos:
        return "负面"
    return "中性"
