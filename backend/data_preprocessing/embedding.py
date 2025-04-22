from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv
import re
from tqdm import tqdm

# Load env variables
load_dotenv("../.env")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Connect to Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("llm")


def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", "!", "?", " ", ""]
    )
    return splitter.split_text(text)

def split_by_page(text):
    # Matches [Page X] where X can be one or more digits
    pattern = r"\[Page (\d+)\]"
    splits = re.split(pattern, text)
    
    pages = []
    for i in range(1, len(splits), 2):
        page_num = int(splits[i])
        page_text = splits[i+1].strip()
        pages.append((page_num, page_text))
    return pages

def chunk_list(data, chunk_size=1000):
    """Helper to split data into chunks"""
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


def extract_specialization_from_filename(filename):
    # Assuming filename is in the format "Title X - Specialization.txt"
    base_name = os.path.splitext(filename)[0]
    parts = base_name.split(" - ")
    if len(parts) > 1:
        return parts[1].lower()  # Specialization is after the "Title X"
    return "default"  


def process_embedding(input_folder):
    embeddings_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    for text_file in os.listdir(input_folder):
        if text_file.lower().endswith(".txt"):
            file_path = os.path.join(input_folder, text_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    full_text = f.read()

                pages = split_by_page(full_text)
                specialization = extract_specialization_from_filename(text_file)
                namespace = "federal_law_code"
                source = "https://uscode.house.gov/download/download.shtml"

                upserts = []

                for page_num, page_text in tqdm(pages, desc=f"  → Pages of {text_file}", leave=False):
                    chunks = get_text_chunks(page_text)
                    embeddings = embeddings_model.embed_documents(chunks)

                    for i, chunk in enumerate(chunks):
                        doc_id = f"{text_file}_p{page_num}_{i}"
                        upserts.append({
                            "id": doc_id,
                            "values": embeddings[i],
                            "metadata": {
                                "source": source,
                                "page": page_num,
                                "specialization": specialization,
                                "chunk_text": chunk
                            }
                        })

                pinecone_vectors = [
                    (item["id"], item["values"], item["metadata"]) for item in upserts
                ]

                for batch in chunk_list(pinecone_vectors, chunk_size=1000):
                    index.upsert(vectors=batch, namespace=namespace)

                print(f"✅ Processed and upserted: {text_file} into namespace: {namespace}")
            except Exception as e:
                print(f"❌ Failed to process {text_file}: {e}")


def main():
    data_folder = "../data"
    input_folder = os.path.join(data_folder, "processing_data")
    process_embedding(input_folder)


if __name__ == "__main__":
    main()
