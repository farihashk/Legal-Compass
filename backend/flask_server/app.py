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

app = Flask(__name__)
CORS(app)

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

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
        "max_length": 1024
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
                    'text': chunk,
                    'source': request.files['pdf'].filename
                }
            })
        
        # Update the conversation chain
        global conversation_chain, vectorstore
        conversation_chain = get_conversation_chain(vectorstore)
        
        return jsonify({
            'status': 'success',
            'chunks_processed': len(text_chunks)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/ask", methods=["POST"])
def ask():
    user_question = request.json["question"]
    
    # Step 1: Search legal info
    legal_chunks = []
    for ns in ["federal_law_code", "california_law_case", "reddit_post"]:
        legal_chunks.extend(persistent_vectorstore.similarity_search(user_question, namespace=ns, k=3))
    
    # Step 2: Search lawyer info
    lawyer_chunks = persistent_vectorstore.similarity_search(
        query=user_question,
        namespace="default",
        k=3
    )
    
    # Step 3: Compose prompt
    context = f"""
    You are a helpful legal assistant. Provide legal context and suggest lawyers if available.

    User Question:
    {user_question}

    Legal Information:
    {''.join([chunk.page_content for chunk in legal_chunks])}

    Lawyer Recommendations:
    {''.join([chunk.page_content for chunk in lawyer_chunks])}
    """
        
    # Step 4: Call LLM
    response = llm.invoke(context)
    
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)

