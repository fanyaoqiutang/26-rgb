from pymilvus import connections, Collection, FieldSchema, DataType, utility
from sentence_transformers import SentenceTransformer
from config import MILVUS_CONFIG

# 加载向量化模型
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
DIM = 384  # 向量维度

def init_milvus():
    # 连接Milvus
    connections.connect(
        alias="default",
        host=MILVUS_CONFIG["host"],
        port=MILVUS_CONFIG["port"]
    )
    coll_name = MILVUS_CONFIG["collection_name"]
    # 不存在集合则新建
    if not utility.has_collection(coll_name):
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=2000),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=DIM),
            FieldSchema(name="tag", dtype=DataType.VARCHAR, max_length=100)
        ]
        coll = Collection(coll_name, fields)
        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128}
        }
        coll.create_index(field_name="vector", index_params=index_params)
    coll = Collection(coll_name)
    coll.load()
    return coll

# 文本向量化
def text_embedding(text):
    return embed_model.encode(text).tolist()

# 检索知识库
def search_knowledge(query_text, top_k=3):
    coll = init_milvus()
    vec = text_embedding(query_text)
    res = coll.search(
        data=[vec],
        anns_field="vector",
        param={"metric_type": "L2", "params": {"nprobe": 10}},
        limit=top_k,
        output_fields=["content", "tag"]
    )
    # 拼接检索到的景区资料
    knowledge_text = ""
    for hits in res:
        for hit in hits:
            knowledge_text += hit.entity.get("content") + "\n"
    return knowledge_text