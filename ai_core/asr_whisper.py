import whisper

# 轻量中文模型，首次运行自动下载
model = whisper.load_model("tiny")

def audio_file_to_text(audio_path: str) -> str:
    result = model.transcribe(audio_path, language="zh")
    return result["text"]

if __name__ == "__main__":
    path = input("输入音频文件路径：")
    print(audio_file_to_text(path))