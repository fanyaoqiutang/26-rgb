from pymilvus import MilvusClient, CollectionSchema, FieldSchema, DataType
from langchain_text_splitters import RecursiveCharacterTextSplitter
import dashscope
from dashscope import TextEmbedding
from utils.doc_parser import load_all_scenic_docs
from config import SCENIC_DOC_DIR, LLM_CONFIG
import os

dashscope.api_key = LLM_CONFIG["api_key"]
COLLECTION_NAME = "scenic_kb"
EMBEDDING_DIM = 1536

# 数据库文件路径（放在项目目录下）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE_PATH = os.path.join(BASE_DIR, "data", "milvus_scenic.db")

# 客户端延迟初始化
_client = None

def get_client():
    """获取Milvus客户端（延迟初始化）"""
    global _client
    if _client is None:
        # 确保目录存在
        os.makedirs(os.path.dirname(DB_FILE_PATH), exist_ok=True)
        _client = MilvusClient(uri=DB_FILE_PATH)
    return _client

# 为了兼容现有代码，提供 client 属性
@property
def client():
    return get_client()

def create_new_collection():
    client = get_client()
    if client.has_collection(collection_name=COLLECTION_NAME):
        client.drop_collection(collection_name=COLLECTION_NAME)

    # 按官方标准构建字段与Schema
    fields = [
        FieldSchema(
            name="id",
            dtype=DataType.INT64,
            is_primary=True,
            auto_id=True
        ),
        FieldSchema(
            name="text",
            dtype=DataType.VARCHAR,
            max_length=4000
        ),
        FieldSchema(
            name="vector",
            dtype=DataType.FLOAT_VECTOR,
            dim=EMBEDDING_DIM
        )
    ]
    schema = CollectionSchema(fields=fields)

    # 准备索引参数
    index_params = client.prepare_index_params()
    index_params.add_index(
        field_name="vector",
        index_type="FLAT",
        metric_type="L2"
    )

    # 正确创建集合
    client.create_collection(
        collection_name=COLLECTION_NAME,
        schema=schema,
        index_params=index_params
    )
    print("向量库集合创建完成")

def get_text_embedding(text_list):
    response = TextEmbedding.call(
        model=TextEmbedding.Models.text_embedding_v2,
        input=text_list
    )
    embedding_list = [item["embedding"] for item in response.output["embeddings"]]
    return embedding_list

def init_knowledge_base():
    full_document_text = load_all_scenic_docs(SCENIC_DOC_DIR)
    if not full_document_text.strip():
        print("未读取到任何文档内容，请检查文档路径与文件")
        return

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=350, chunk_overlap=60)
    text_chunks = text_splitter.split_text(full_document_text)

    create_new_collection()
    vectors = get_text_embedding(text_chunks)
    insert_data = [{"text": chunk, "vector": vec} for chunk, vec in zip(text_chunks, vectors)]
    client = get_client()
    client.insert(collection_name=COLLECTION_NAME, data=insert_data)
    print(f"知识库初始化完毕，总共入库 {len(text_chunks)} 条文本片段")

def search_relevant_context(query: str, top_k: int = 3):
    client = get_client()
    # 检查集合是否存在
    if not client.has_collection(collection_name=COLLECTION_NAME):
        return ""
    # 加载集合
    client.load_collection(collection_name=COLLECTION_NAME)
    query_vec = get_text_embedding([query])[0]
    search_result = client.search(
        collection_name=COLLECTION_NAME,
        data=[query_vec],
        limit=top_k,
        output_fields=["text"]
    )
    if not search_result or not search_result[0]:
        return ""
    context = "\n\n".join([hit["entity"]["text"] for hit in search_result[0]])
    return context

if __name__ == "__main__":
    init_knowledge_base()