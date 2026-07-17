from ai_core.llm_chat import get_guide_answer
from ai_core.tts_edgetts import text_to_audio

def text_qa_flow(question: str):
    # 知识库检索+大模型生成回答
    ans = get_guide_answer(question)
    # 文字转语音，生成mp3
    audio_path = text_to_audio(ans)
    return {
        "question": question,
        "answer": ans,
        "audio_file": audio_path
    }

if __name__ == "__main__":
    user_q = input("请输入灵山景区相关问题：")
    result = text_qa_flow(user_q)

    print("\n===== 问答结果 =====")
    print(f"游客提问：{result['question']}")
    print(f"导游回复：{result['answer']}")
    print(f"播报语音保存路径：{result['audio_file']}")