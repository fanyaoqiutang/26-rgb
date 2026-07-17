import edge_tts
import os

def text_to_audio(text: str, save_path: str = "../temp/reply.mp3") -> str:
    dir_path = os.path.dirname(save_path)
    # 上级目录不存在就递归创建
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    voice = "zh-CN-YunyangNeural"
    communicate = edge_tts.Communicate(text, voice)
    communicate.save_sync(save_path)
    return save_path

if __name__ == "__main__":
    txt = "测试语音生成"
    p = text_to_audio(txt)
    print("音频路径：", p)