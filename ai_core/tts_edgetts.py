import edge_tts
import os
import glob
from config import AUDIO_CACHE_PATH

DEFAULT_VOICE = "zh-CN-XiaoyiNeural"

def text_to_audio(text: str, filename: str = None, voice: str = None) -> str:
    if filename is None:
        import time
        filename = f"reply_{int(time.time())}.mp3"
    save_path = os.path.join(AUDIO_CACHE_PATH, filename)
    if voice is None:
        voice = DEFAULT_VOICE

    try:
        communicate = edge_tts.Communicate(text, voice)
        communicate.save_sync(save_path)
    except Exception as e:
        print(f"[TTS] 语音生成失败: {e}")
        return ""

    for old in glob.glob(os.path.join(AUDIO_CACHE_PATH, "reply_*.mp3")):
        if old != save_path:
            try:
                os.remove(old)
            except OSError:
                pass

    return save_path

if __name__ == "__main__":
    txt = "测试语音生成"
    p = text_to_audio(txt)
    print("音频路径：", p)