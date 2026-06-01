# 🏢 HR Document Q&A System — RAG Pipeline

An AI-powered Question & Answering system for HR documents built using 
**Retrieval-Augmented Generation (RAG)** architecture with a Streamlit chat UI.

---

## 🖼️ Demo

![HR Assistant UI](demo.png)

---

## 📌 Project Overview

This project ingests multiple HR PDF documents, processes them into a 
searchable vector database, and answers employee questions accurately 
with source citations — without hallucinating information.

---

## 🎯 What It Does

- 📄 Ingests and parses multiple HR PDF documents automatically
- ✂️ Chunks documents intelligently for precise retrieval
- 🔍 Embeds chunks into ChromaDB vector store using MiniLM model
- 💬 Answers natural language questions using Llama 3.3 70B
- 📎 Cites exact source document and page number for every answer
- ❌ Says "I don't have this information" when answer not in documents
- 🖥️ Beautiful Streamlit chat UI with settings and sample questions

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| PDF Parsing | PyMuPDF (fitz) |
| Chunking | Custom Recursive Word Chunker |
| Vector Database | ChromaDB |
| Embedding Model | all-MiniLM-L6-v2 (via ChromaDB) |
| LLM | Llama 3.3 70B via Groq API (free) |
| Framework | LangChain |
| UI | Streamlit |
| Language | Python 3.13 |

---

## 🏗️ Architecture


┌─────────────────────────────────────────────────────────┐
│                   INGESTION PIPELINE                     │
│                                                          │
│  PDF Files → Extract Text → Chunk (500 words, 50 overlap)│
│           → Generate Embeddings → Store in ChromaDB      │
└─────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────┐
│                RETRIEVAL + GENERATION                    │
│                                                          │
│  User Query → Embed Query → Cosine Similarity Search     │
│           → Retrieve Top K Chunks → Build Context        │
│           → LLM Generation → Answer + Source Citation    │
└─────────────────────────────────────────────────────────┘


---

## 📊 Dataset Stats

| Metric | Value |
|---|---|
| PDF Documents | 4 HR documents |
| Total Pages | 361 pages |
| Chunks Created | 385 searchable chunks |
| Chunk Size | 500 words |
| Chunk Overlap | 50 words |

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/hr-rag-system.git
cd hr-rag-system
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up Groq API key
Create a `.env` file in root folder:
GROQ_API_KEY=your_groq_api_key_here
Get your free API key at: https://console.groq.com

### 5. Add HR PDF files
Place your HR PDF documents inside the `data/` folder.

### 6. Build the pipeline (first time only)
```bash
python main.py
```

### 7. Launch the chat UI
```bash
streamlit run app.py
```

Open browser at: `http://localhost:8501`

---

## 💬 Example Conversations

**Question:** What are the working hours?
Answer: The Institute timings are from 9:00 am to 5:45 pm
(Monday to Friday) with a 15-minute grace period in the morning.
Sources:
📄 hr-policy.pdf — Page 6
📄 HR Policy Manual 2023.pdf — Page 78

**Question:** What is the sick leave policy?
Answer: Employers must provide at least 24 hours or three days
of paid sick leave per year. Employees accrue one hour of paid
sick leave for every 30 hours worked.
Sources:
📄 Employee-Handbook.pdf — Page 38

**Question:** What is the work from home policy?
Answer: You can occasionally work from home (WFH), normally
one day per week. Inform your manager at least two days in advance.
Sources:
📄 Employee-Handbook.pdf — Page 23
📄 HR Policy Manual 2023.pdf — Page 9

---

## 📁 Project Structure
hr-rag-system/
├── data/                    ← HR PDF documents (add your own)
├── chroma_db/               ← Vector store (auto-generated)
├── main.py                  ← Core RAG pipeline
├── app.py                   ← Streamlit chat UI
├── requirements.txt         ← Python dependencies
├── .env                     ← API keys (never uploaded)
├── .gitignore               ← Git ignore rules
└── README.md                ← This file

---

## 🔑 Key Design Decisions

| Decision | Reason |
|---|---|
| ChromaDB over Pinecone | Free, local, no API cost, easy setup |
| Groq API for LLM | Free tier, extremely fast inference |
| Temperature = 0 | Factual HR answers must be consistent |
| Chunk size 500 words | Balance between precision and context |
| Source citation | Prevents hallucination, builds user trust |
| Self-hosted embeddings | HR data privacy — no data sent externally |

---

## 🚀 Future Improvements

- [ ] Hybrid search — semantic + keyword (BM25)
- [ ] Reranking for better retrieval precision
- [ ] Document versioning for policy updates
- [ ] Multi-language support
- [ ] User authentication per department
- [ ] Conversation memory across sessions
- [ ] Deploy on Streamlit Cloud

---

## 🎓 What I Learned

- End-to-end RAG pipeline architecture
- Vector database concepts and similarity search
- Chunking strategies and their impact on retrieval quality
- LLM prompt engineering for factual grounding
- Preventing hallucinations using context constraints
- Building production-ready AI applications

---

## 👨‍💻 Author

Built as a portfolio project demonstrating RAG architecture
for enterprise HR document processing.

⭐ Star this repo if you found it helpful!
