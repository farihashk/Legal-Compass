from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint, HuggingFaceEmbeddings

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("legal-compass") 

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


persistent_vectorstore = PineconeVectorStore(
    index=index,
    embedding=embeddings,
    text_key="chunk_text"
)

legal_chunks = persistent_vectorstore.similarity_search(
"probate law ",
namespace="california_law_code",
k=3
)
print("Legal Chunks:", legal_chunks)