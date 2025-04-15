from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv("../.env")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Connect to Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("llm")


def get_text_chunk(text):
    splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=500,
        chunk_overlap=50,
        length_function=len
    )
    return splitter.split_text(text)


def chunk_list(data, chunk_size=1000):
    """Helper to split data into chunks"""
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


def extract_title_from_filename(filename):
    base = os.path.splitext(filename)[0]
    parts = base.split('@')
    if len(parts) > 1:
        return parts[1].lower()
    return "default"


def process_embedding(input_folder):
    embeddings_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    text_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".txt")]

    for text in text_files:
        text_path = os.path.join(input_folder, text)
        try:
            with open(text_path, 'r', encoding='utf-8') as txt:
                text_content = txt.read()
                chunks = get_text_chunk(text_content)
                embeddings = embeddings_model.embed_documents(chunks)

                title = extract_title_from_filename(text)
                namespace = f"usc_title_{title.replace(' ', '_').lower()}"

                upserts = []

                for i, chunk in enumerate(chunks):
                    doc_id = f"{text}_{i}"
                    upserts.append({
                        "id": doc_id,
                        "values": embeddings[i],
                        "metadata": {"source": text}
                    })

                pinecone_vectors = [
                    (item["id"], item["values"], item["metadata"]) for item in upserts
                ]

                # Upsert in chunks to avoid limits
                for batch in chunk_list(pinecone_vectors, chunk_size=1000):
                    index.upsert(vectors=batch, namespace=namespace)

                print(f"✅ Processed and upserted: {text} into namespace: {namespace}")
        except Exception as e:
            print(f"❌ Failed to process {text}: {e}")


def main():
    data_folder = "../data"
    input_folder = os.path.join(data_folder, "processing_data")
    process_embedding(input_folder)


if __name__ == "__main__":
    main()
