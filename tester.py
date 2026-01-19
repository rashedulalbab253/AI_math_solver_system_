from rag.retriever import RagRetriever

r = RagRetriever()
context = r.retrieve("minimum value of quadratic function")

for c in context:
    print("----")
    print(c)