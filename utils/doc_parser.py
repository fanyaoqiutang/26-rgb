import os
from docx import Document

def read_docx_text(file_path: str) -> str:
    doc = Document(file_path)
    content = []
    for p in doc.paragraphs:
        text = p.text.strip()
        if text:
            content.append(text)
    return "\n".join(content)

def load_all_scenic_docs(dir_path: str):
    """批量读取文件夹下所有docx"""
    all_text = ""
    for name in os.listdir(dir_path):
        if name.lower().endswith(".docx"):
            full_path = os.path.join(dir_path, name)
            text = read_docx_text(full_path)
            all_text += f"\n====={name}=====\n{text}\n"
    return all_text