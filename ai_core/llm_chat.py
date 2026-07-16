import requests
from utils.prompt_template import SYSTEM_PROMPT
from config import LLM_CONFIG

def llm_answer(user_question, knowledge_context, user_tag="通用游客"):
    """
    user_question: 游客提问
    knowledge_context: Milvus检索到的景区知识库
    user_tag: 游客偏好标签 历史/自然风光
    return: 大模型回答文本、情感标签
    """
    prompt = SYSTEM_PROMPT.format(
        knowledge=knowledge_context,
        user_tag=user_tag,
        question=user_question
    )
    headers = {"Authorization": f"Bearer {LLM_CONFIG['api_key']}", "Content-Type": "application/json"}
    data = {
        "model": "qwen-turbo",
        "input": {"messages": [{"role": "system", "content": prompt}]}
    }
    resp = requests.post(LLM_CONFIG["api_url"], json=data, headers=headers)
    result = resp.json()
    content = result["output"]["text"]
    # 简单情感识别（可扩展）
    if "好玩" in content or "推荐" in content:
        emotion = "happy"
    elif "抱歉" in content:
        emotion = "neutral"
    else:
        emotion = "calm"
    return content, emotion