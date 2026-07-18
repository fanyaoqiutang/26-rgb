from flask import Blueprint, request, jsonify, send_file, make_response
import os
from utils.file_util import save_upload_file, get_file_abs_path
from config import BASE_DIR

common_bp = Blueprint("common", __name__)

# 文件上传接口（音频/知识库文档上传）
@common_bp.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"code": 400, "msg": "未上传文件"})
    file = request.files["file"]
    save_dir = request.form.get("save_dir", "audio_cache")
    save_path = save_upload_file(file, save_dir)
    rel_path = os.path.relpath(save_path, BASE_DIR).replace("\\", "/")
    return jsonify({
        "code": 200,
        "msg": "上传成功",
        "file_path": rel_path
    })

# 静态音频文件读取（前端播放TTS语音）
@common_bp.route("/audio/<filename>", methods=["GET"])
def get_audio(filename):
    audio_full_path = get_file_abs_path(f"data/audio_cache/{filename}")
    if not os.path.exists(audio_full_path):
        return jsonify({"code": 404, "msg": "音频文件不存在"})
    response = make_response(send_file(audio_full_path))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response
