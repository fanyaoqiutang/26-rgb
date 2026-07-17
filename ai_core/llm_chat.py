from ai_core.vector_milvus import search_relevant_context
from config import LLM_CONFIG
import requests

API_URL = LLM_CONFIG["api_url"]
API_KEY = LLM_CONFIG["api_key"]

def get_guide_answer(user_question: str, user_tag: str = "通用游客") -> str:
    context = search_relevant_context(user_question)
    prompt = f"""
你是灵山景区专业导游，严格按照参考资料回答游客问题，语言口语简洁，禁止编造资料以外内容。
游客偏好：{user_tag}，回答时适当结合其兴趣推荐相关内容。
【参考资料】
{context}
【游客问题】
{user_question}
"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "qwen-turbo",
        "input": {"prompt": prompt},
        "parameters": {"result_format": "message", "temperature": 0.7}
    }

    resp = requests.post(API_URL, headers=headers, json=payload)
    res_data = resp.json()

    if "code" in res_data:
        return f"接口错误：{res_data['code']} {res_data['message']}"

    answer = res_data["output"]["choices"][0]["message"]["content"]
    return answer

if __name__ == "__main__":
    q = input("输入问题：")
    print(get_guide_answer(q))