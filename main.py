import os
from pathlib import Path
from dotenv import load_dotenv

import fitz  # PyMuPDF
from langchain_groq import ChatGroq
import chromadb

# Load API key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ── STEP 1: EXTRACT TEXT FROM PDFs ──────────────────────────
def extract_text_from_pdfs(data_folder="data"):
    documents = []
    pdf_files = list(Path(data_folder).glob("*.pdf"))

    if not pdf_files:
        print("❌ No PDF files found in data/ folder!")
        print(f"   Please add PDF files to: {Path(data_folder).absolute()}")
        return documents

    for pdf_path in pdf_files:
        print(f"📄 Reading: {pdf_path.name}")
        pdf = fitz.open(pdf_path)
        for page_num in range(len(pdf)):
            page = pdf[page_num]
            text = page.get_text()
            if text.strip():
                documents.append({
                    "text": text,
                    "source": pdf_path.name,
                    "page": page_num + 1
                })
                
        pdf.close()

    print(f"✅ Extracted {len(documents)} pages from {len(pdf_files)} PDFs")
    return documents


# ── STEP 2: CHUNKING ────────────────────────────────────────
def chunk_documents(documents):
    chunks = []
    chunk_size = 500
    overlap = 50

    for doc in documents:
        text = doc["text"]
        words = text.split()

        i = 0
        while i < len(words):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)

            if len(chunk_text.strip()) > 50:
                chunks.append({
                    "text": chunk_text,
                    "source": doc["source"],
               
                    "page": doc["page"]
                })
            i += chunk_size - overlap

    print(f"✅ Created {len(chunks)} chunks")
    return chunks

# ── STEP 3: CREATE VECTOR STORE ─────────────────────────────
def create_vector_store(chunks):
    print("⏳ Storing chunks in ChromaDB...")

    client = chromadb.PersistentClient(path="chroma_db")

    try:
        client.delete_collection("hr_documents")
    except:
        pass

    collection = client.create_collection(
        name="hr_documents",
        metadata={"hnsw:space": "cosine"}
    )

    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        collection.add(
            documents=[c["text"] for c in batch],
            metadatas=[{"source": c["source"], "page": c["page"]} for c in batch],
            ids=[f"chunk_{i + j}" for j, _ in enumerate(batch)]
        )
        print(f"  Stored {min(i + batch_size, len(chunks))}/{len(chunks)} chunks...")

    print("✅ Vector store created and saved!")
    return collection

# ── STEP 4: LOAD EXISTING VECTOR STORE ──────────────────────
def load_vector_store():
    print("📂 Loading existing vector store...")
    client = chromadb.PersistentClient(path="chroma_db")
    collection = client.get_collection("hr_documents")
    print(f"✅ Loaded collection with {collection.count()} chunks")
    return collection


# ── STEP 5: RETRIEVE RELEVANT CHUNKS ────────────────────────
def retrieve_chunks(collection, query, k=5):
    results = collection.query(
        query_texts=[query],
        n_results=k
    )

    chunks = []
    print(f"\n🔍 Retrieved chunks for: '{query}'")
    for i, (doc, meta, distance) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    )):
        print(f"  [{i+1}] Distance: {distance:.3f} | {meta['source']} - Page {meta['page']}")
        chunks.append({"text": doc, "source": meta["source"], "page": meta["page"]})

    return chunks


# ── STEP 6: GENERATE ANSWER WITH LLM ────────────────────────
def generate_answer(query, retrieved_chunks):
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY not found in .env file!")
        return "Error: No API key found."

    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model_name="llama-3.3-70b-versatile",
        temperature=0
    )

    context = "\n\n".join([
        f"Source: {chunk['source']} (Page {chunk['page']})\n{chunk['text']}"
        for chunk in retrieved_chunks
    ])

    prompt = f"""You are an HR assistant. Answer ONLY using the context below.
If the answer is not in the context, say exactly: "I don't have this information in the HR documents."
Do NOT use any outside knowledge. Be concise and clear.

CONTEXT:
{context}

QUESTION: {query}

ANSWER:"""

    response = llm.invoke(prompt)
    return response.content


# ── MAIN: RUN EVERYTHING ─────────────────────────────────────
def main():
    print("\n" + "="*55)
    print("   HR Document Q&A System - RAG Pipeline")
    print("="*55 + "\n")

    # Build or load vector store
    if not os.path.exists("chroma_db"):
        print("🔨 First run — building pipeline...\n")
        documents = extract_text_from_pdfs("data")
        if not documents:
            return
        chunks = chunk_documents(documents)
        collection = create_vector_store(chunks)
    else:
        collection = load_vector_store()

    # Test questions
    test_questions = [
        "What is the sick leave policy?",
        "How many annual leaves does an employee get?",
        "What is the work from home policy?"
    ]

    print("\n" + "="*55)
    print("   Testing RAG Pipeline with Sample Questions")
    print("="*55)

    for question in test_questions:
        print(f"\n❓ Question: {question}")
        chunks = retrieve_chunks(collection, question)
        answer = generate_answer(question, chunks)
        print(f"\n💬 Answer: {answer}")
        print("-"*55)

    # Interactive mode
    print("\n✅ Ask your own questions! Type 'exit' to quit.\n")
    while True:
        user_input = input("❓ Your question: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break
        if user_input:
            chunks = retrieve_chunks(collection, user_input)
            answer = generate_answer(user_input, chunks)
            print(f"\n💬 Answer: {answer}\n")

if __name__ == "__main__":
    main()