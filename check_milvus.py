from pymilvus import MilvusClient

client = MilvusClient("./ai_core/milvus_scenic.db")
coll_name = "scenic_kb"

if not client.has_collection(coll_name):
    print("❌ 集合不存在")
else:
    # 关键：先加载集合到内存
    client.load_collection(collection_name=coll_name)
    res = client.query(
        collection_name=coll_name,
        filter="id >= 0",
        output_fields=["text"]
    )
    print(f"✅ 向量库内总片段数量：{len(res)}")
    for idx, item in enumerate(res, 1):
        print(f"\n===== 第{idx}条 =====\n{item['text']}")