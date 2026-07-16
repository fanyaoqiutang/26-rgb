import edge_tts
import os
import uuid
from config import AUDIO_CACHE_PATH

def text_to_audio(text, voice="zh-CN-YunyangNeural"):
    """文本转语音，返回相对音频路径"""
    file_name = f"{uuid.uuid4()}.mp3"
    output_path = os.path.join(AUDIO_CACHE_PATH, file_name)
    communicate = edge_tts.Communicate(text, voice)
    communicate.save_sync(output_path)
    # 返回前端可访问的相对url
    return f"/api/common/audio/{file_name}"