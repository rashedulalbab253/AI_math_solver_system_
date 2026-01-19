import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

kb_path = "rag/knowledge_base"
db_path = "rag/vector_store"

def ingest():
    docs = []

    for file in os.listdir(kb_path):
        with open(os.path.join(kb_path, file), "r", encoding = "utf-8") as f:
            docs.append(f.read())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 400,
        chunk_overlap = 50
    )

    chunks = splitter.create_documents(docs)

    embeddings = HuggingFaceEmbeddings(
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(db_path)

    print("RAG ingestion complete")

if __name__ == "__main__":
    ingest()











    