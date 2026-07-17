from pymilvus import MilvusClient, CollectionSchema, FieldSchema, DataType
from langchain_text_splitters import RecursiveCharacterTextSplitter
import dashscope
from dashscope import TextEmbedding
from utils.doc_parser import load_all_scenic_docs
from config import SCENIC_DOC_DIR, LLM_CONFIG

dashscope.api_key = LLM_CONFIG["api_key"]
COLLECTION_NAME = "scenic_kb"
EMBEDDING_DIM = 1536
DB_FILE_PATH = "../milvus_scenic.db"

client = MilvusClient(uri=DB_FILE_PATH)

def create_new_collection():
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
    print("✅ 向量库集合创建完成")

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
        print("❌ 未读取到任何文档内容，请检查文档路径与文件")
        return

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=350, chunk_overlap=60)
    text_chunks = text_splitter.split_text(full_document_text)

    create_new_collection()
    vectors = get_text_embedding(text_chunks)
    insert_data = [{"text": chunk, "vector": vec} for chunk, vec in zip(text_chunks, vectors)]
    client.insert(collection_name=COLLECTION_NAME, data=insert_data)
    print(f"🎉 知识库初始化完毕，总共入库 {len(text_chunks)} 条文本片段")

def search_relevant_context(query: str, top_k: int = 3):
    # 每次检索前加载集合
    client.load_collection(collection_name=COLLECTION_NAME)
    query_vec = get_text_embedding([query])[0]
    search_result = client.search(
        collection_name=COLLECTION_NAME,
        data=[query_vec],
        limit=top_k,
        output_fields=["text"]
    )
    context = "\n\n".join([hit["entity"]["text"] for hit in search_result[0]])
    return context
if __name__ == "__main__":
    init_knowledge_base()