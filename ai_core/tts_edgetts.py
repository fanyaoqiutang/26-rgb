import edge_tts
import os
from config import AUDIO_CACHE_PATH

def text_to_audio(text: str, filename: str = None) -> str:
    if filename is None:
        import time
        filename = f"reply_{int(time.time())}.mp3"
    save_path = os.path.join(AUDIO_CACHE_PATH, filename)
    voice = "zh-CN-XiaoyiNeural"
    communicate = edge_tts.Communicate(text, voice)
    communicate.save_sync(save_path)
    return save_path

if __name__ == "__main__":
    txt = "测试语音生成"
    p = text_to_audio(txt)
    print("音频路径：", p)