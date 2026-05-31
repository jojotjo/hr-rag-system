\# HR Document Q\&A System — RAG Pipeline



An AI-powered Q\&A system for HR documents using 

Retrieval-Augmented Generation (RAG).



\## What it does

\- Ingests multiple HR PDF documents

\- Chunks and embeds them into a vector database

\- Answers employee questions with source citations

\- Uses hybrid semantic search for accurate retrieval



\## Tech Stack

\- \*\*Vector Database:\*\* ChromaDB

\- \*\*LLM:\*\* Llama 3.3 via Groq API

\- \*\*PDF Parsing:\*\* PyMuPDF

\- \*\*Framework:\*\* LangChain

\- \*\*UI:\*\* Streamlit (coming soon)



\## Architecture

PDF Documents → Extract → Chunk → Embed → ChromaDB

↓

User Query → Embed → Similarity Search → Retrieve Chunks

↓

LLM → Generate Answer



\## Setup



1\. Clone the repository

```bash

git clone https://github.com/YOUR\_USERNAME/hr-rag-system

cd hr-rag-system

```



2\. Create virtual environment

```bash

python -m venv venv

venv\\Scripts\\activate

```



3\. Install dependencies

```bash

pip install -r requirements.txt

```



4\. Add your Groq API key

```bash

\# Create .env file

echo GROQ\_API\_KEY=your\_key\_here > .env

```



5\. Add HR PDF files to `data/` folder



6\. Run the pipeline

```bash

python main.py

```



\## Results

\- Processes 4 HR documents (361 pages)

\- Creates 385 searchable chunks

\- Answers questions with source document citations

