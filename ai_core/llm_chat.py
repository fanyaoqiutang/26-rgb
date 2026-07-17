from ai_core.vector_milvus import search_relevant_context
from config import LLM_CONFIG
import requests

API_URL = LLM_CONFIG["api_url"]
API_KEY = LLM_CONFIG["api_key"]

def get_guide_answer(user_question: str, user_tag: str = "通用游客") -> str:
    context = search_relevant_context(user_question)

    if context.strip():
        prompt = f"""你是灵山景区AI导游，请根据以下参考资料回答问题。
要求：口语化、简短，不要使用**等markdown符号，不要加粗。

【参考资料】
{context}

游客偏好：{user_tag}
【游客问题】
{user_question}"""
    else:
        prompt = f"""你是灵山景区AI导游，请用口语化、简短的语言回答问题。
不要使用**等markdown符号，不要加粗，不要列条目符号。

游客偏好：{user_tag}
【游客问题】
{user_question}"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "qwen-turbo",
        "input": {"prompt": prompt},
        "parameters": {"result_format": "message", "temperature": 0.5}
    }

    resp = requests.post(API_URL, headers=headers, json=payload)
    res_data = resp.json()

    if "code" in res_data:
        return f"接口错误：{res_data['code']} {res_data['message']}"

    answer = res_data["output"]["choices"][0]["message"]["content"]
    answer = answer.replace("**", "").replace("*", "")
    return answer

if __name__ == "__main__":
    q = input("输入问题：")
    print(get_guide_answer(q))