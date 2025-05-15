from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_huggingface import HuggingFaceEndpoint, HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
import os
import pandas as pd
import re
app = Flask(__name__)
CORS(app)

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

lawyer_data = pd.read_csv("../data/wills_lawyers.csv", encoding="utf-8")

@app.route("/lawyers", methods = ["GET"])
def get_will_lawyers():
    result = lawyer_data.to_dict(orient = "records")
    return jsonify(result)

@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    return response

# Initialize components at startup
llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.3",
    task="text-generation",
    temperature=0.1,
    huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_TOKEN"),
    model_kwargs={
        "max_length": 2048
    }
)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

conversation_chain = None
vectorstore = None

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("legal-compass") 


persistent_vectorstore = PineconeVectorStore(
    index=index,
    embedding=embeddings,
    text_key="chunk_text"
)


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", "!", "?", " ", ""]
    )
    return splitter.split_text(text)

def get_conversation_chain(vectorstore=None):
    memory = ConversationBufferMemory(
        memory_key='chat_history',
        return_messages=True,
        output_key='answer'
    )
    
    retriever = (vectorstore if vectorstore else persistent_vectorstore).as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )
    
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True
    )

# Initialize conversation chain
conversation_chain = get_conversation_chain(persistent_vectorstore)

@app.route('/process-pdf', methods=['POST'])
def process_pdf():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No PDF provided'}), 400
    
    try:
        # 1. Extract text
        pdf_text = get_pdf_text([request.files['pdf']])
        
        # 2. Create chunks
        text_chunks = get_text_chunks(pdf_text)
        
        # 3. Create embeddings and upsert to Pinecone
        vectors = []
        namespace = "user_pdf"
        for i, chunk in enumerate(text_chunks):
            vector = embeddings.embed_query(chunk)
            vectors.append({
                'id': f"chunk_{i}",
                'values': vector,
                'metadata': {
                    'chunk_text': chunk,
                    'source': request.files['pdf'].filename
                }
            })
        index.upsert(vectors=vectors, namespace=namespace)
        # Update the conversation chain
        global conversation_chain, vectorstore
        conversation_chain = get_conversation_chain(persistent_vectorstore)
        
        return jsonify({
            'status': 'success',
            'chunks_processed': len(text_chunks)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def format_chunks(chunks, max_chars=1500):
    formatted = []
    total_chars = 0
    for doc in chunks:
        text = doc.metadata.get("chunk_text", "")
        if text:
            source = doc.metadata.get("source", "unknown")
            chunk_text = f"Source: {source}\n{text}"
            if total_chars + len(chunk_text) <= max_chars:
                formatted.append(chunk_text)
                total_chars += len(chunk_text)
    return "\n\n".join(formatted)


    

@app.route("/ask", methods=["POST"])
def ask():
    user_question = request.json["question"]
    
    # Step 1: Search legal info
    legal_chunks = persistent_vectorstore.similarity_search(user_question, namespace="california_law_code", k=3)
    
    # Step 2: Check if legal_chunks are empty or lack valid content
    if legal_chunks and any(doc.metadata.get("chunk_text", "") for doc in legal_chunks):
        legal_context = format_chunks(legal_chunks)
        # Prompt with legal context
        context = f"""
        You are a helpful and professional legal assistant with knowledge of federal and California law.

        Use the provided legal context to inform your answer.

        Do not simply repeat the laws. Instead, explain them in a way a non-lawyer can understand—using everyday language and natural, conversational paragraphs.

        Only quote short parts of the law if absolutely necessary to support your explanation. Otherwise, focus on providing a useful, easy-to-understand answer.

        Legal Context:
        {legal_context}

        User Question:
        {user_question}
        """
    else:
        # Prompt without legal context
        context = f"""
        You are a helpful and professional legal assistant with knowledge of federal and California law.

        No specific legal texts were retrieved. Provide a general explanation based on standard California trust and probate law.

        Do not simply repeat the laws. Instead, explain them in a way a non-lawyer can understand—using everyday language and natural, conversational paragraphs.

        Only quote short parts of the law if absolutely necessary to support your explanation. Otherwise, focus on providing a useful, easy-to-understand answer.

        User Question:
        {user_question}
        """
    
    # Step 3: Call LLM
    response = llm.invoke(context)
    print("Raw Response:", response)
    
    # Step 4: Clean response
    cleaned_response = re.sub(r'^-+\n*|\n*-+$', '', response).strip()
    print("Cleaned Response:", cleaned_response)
    
    # Step 5: Return the cleaned response
    return jsonify({"response": cleaned_response})

if __name__ == '__main__':
    app.run(debug=True)



    

