import os
import uuid
from config import BASE_DIR

def get_file_abs_path(relative_path):
    """根据相对路径获取绝对路径"""
    return os.path.join(BASE_DIR, relative_path)

def save_upload_file(file_obj, save_sub_dir):
    """保存上传文件，自动生成唯一文件名"""
    save_dir = get_file_abs_path(f"data/{save_sub_dir}")
    os.makedirs(save_dir, exist_ok=True)
    suffix = os.path.splitext(file_obj.filename)[1]
    new_name = str(uuid.uuid4()) + suffix
    full_path = os.path.join(save_dir, new_name)
    file_obj.save(full_path)
    return full_path