# 全局配置
import os

# 服务端口
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5000

# MySQL配置
MYSQL_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "你的数据库密码",
    "database": "scenic_digital_human",
    "charset": "utf8mb4"
}

# Milvus向量库配置
MILVUS_CONFIG = {
    "host": "127.0.0.1",
    "port": 19530,
    "collection_name": "scenic_knowledge"
}

# 大模型API配置（替换成你的API地址/Key）
LLM_CONFIG = {
    "api_key": "xxx",
    "api_url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
}

# 文件存储路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_CACHE_PATH = os.path.join(BASE_DIR, "data", "audio_cache")
KNOWLEDGE_PATH = os.path.join(BASE_DIR, "data", "scenic_knowledge")

# 创建缓存文件夹
os.makedirs(AUDIO_CACHE_PATH, exist_ok=True)
os.makedirs(KNOWLEDGE_PATH, exist_ok=True)