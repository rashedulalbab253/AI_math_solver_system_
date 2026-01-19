from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

db_path = "rag/vector_store"

class RAGRetriever:

    def __init__(self):
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        self.db = FAISS.load_local(
            db_path,
            embeddings,
            allow_dangerous_deserialization = True
        )

    def retrieve(self, query: str, k: int = 3):
        results = self.db.similarity_search(query, k=k)

        if not results:
            return []
        
        return [doc.page_content for doc in results]