import whisper
import os

model = whisper.load_model("tiny")

def audio_file_to_text(audio_path: str) -> str:
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"音频文件不存在: {audio_path}")
    file_size = os.path.getsize(audio_path)
    if file_size == 0:
        raise ValueError(f"音频文件为空: {audio_path}")
    print(f"识别音频: {audio_path}, 大小: {file_size} bytes")
    result = model.transcribe(audio_path, language="zh")
    return result["text"].strip()

if __name__ == "__main__":
    path = input("输入音频文件路径：")
    print(audio_file_to_text(path))