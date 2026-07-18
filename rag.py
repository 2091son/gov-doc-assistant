import os
import chromadb
import hashlib
import numpy as np

# 初始化 ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")
collection_name = "gov_docs"

try:
    collection = client.get_collection(collection_name)
    print(f"已连接知识库，共有 {collection.count()} 篇文档")
except:
    collection = client.create_collection(collection_name)
    print("创建新的知识库")

def load_knowledge():
    """加载 knowledge 文件夹里的所有 txt 文件"""
    knowledge_dir = "./knowledge"
    if not os.path.exists(knowledge_dir):
        os.makedirs(knowledge_dir)
        print(f"创建知识库文件夹: {knowledge_dir}")
        return
    
    txt_files = [f for f in os.listdir(knowledge_dir) if f.endswith('.txt')]
    
    if not txt_files:
        print("知识库文件夹为空，请放入 .txt 文件")
        return
    
    for file_name in txt_files:
        file_path = os.path.join(knowledge_dir, file_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        doc_id = hashlib.md5(content.encode()).hexdigest()
        
        existing = collection.get(ids=[doc_id])
        if existing['ids']:
            print(f"跳过已存在的文档: {file_name}")
            continue
        
        # 用零向量占位
        collection.add(
            ids=[doc_id],
            embeddings=[np.zeros(384).tolist()],
            metadatas=[{"source": file_name}],
            documents=[content]
        )
        print(f"已加载: {file_name}")

def search_knowledge(query, top_k=2):
    """关键词搜索"""
    all_docs = collection.get()
    if not all_docs['documents']:
        return []
    
    scored = []
    for i, doc in enumerate(all_docs['documents']):
        score = 0
        for kw in query:
            if kw in doc:
                score += 1
        scored.append((score, i))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    top_indices = [i for score, i in scored if score > 0][:top_k]
    
    result = []
    for idx in top_indices:
        result.append({
            "source": all_docs['metadatas'][idx]['source'],
            "content": all_docs['documents'][idx]
        })
    return result

if __name__ == "__main__":
    load_knowledge()
    
    query = input("请输入搜索关键词: ")
    results = search_knowledge(query)
    
    if results:
        print(f"\n找到 {len(results)} 篇相关文档：")
        for i, doc in enumerate(results):
            print(f"\n--- 结果 {i+1} ---")
            print(f"来源: {doc['source']}")
            print(doc['content'][:300] + "...")
    else:
        print("没有找到相关文档")