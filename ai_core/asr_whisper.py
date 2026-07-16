import whisper
import os

# 模型可选 tiny/base/small，越小速度越快
model = whisper.load_model("base")

def audio_to_text(audio_file_path):
    """音频转文字"""
    result = model.transcribe(audio_file_path)
    return result["text"]