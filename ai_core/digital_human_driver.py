def get_mouth_sequence(text):
    """简易口型序列生成，前端数字人渲染使用"""
    mouth_list = []
    for char in text:
        # 简单模拟开口闭口，可对接专业数字人SDK
        if char in "aeiouaeiou":
            mouth_list.append("open")
        else:
            mouth_list.append("close")
    return mouth_list

def get_emotion_face(emotion):
    """根据情感返回表情标识"""
    emotion_map = {
        "happy": "smile",
        "calm": "normal",
        "neutral": "normal",
        "sad": "sad"
    }
    return emotion_map.get(emotion, "normal")