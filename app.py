import os
import streamlit as st
from dotenv import load_dotenv
from main import load_vector_store, retrieve_chunks, generate_answer

# Load API key
load_dotenv()

# ── PAGE CONFIG ───────────────────────────────────────────
st.set_page_config(
    page_title="HR Assistant",
    page_icon="🏢",
    layout="centered"
)

# ── CUSTOM CSS ────────────────────────────────────────────
st.markdown("""
<style>
    .main {background-color: #f8f9fa;}
    .stTextInput > div > div > input {
        border-radius: 20px;
        border: 2px solid #0066cc;
        padding: 10px 15px;
    }
    .answer-box {
        background-color: #0066cc;
        border-left: 4px solid #0066cc;
        border-radius: 8px;
        padding: 15px 20px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .source-box {
        background-color: #f0f7ff;
        border-radius: 6px;
        padding: 8px 12px;
        margin: 5px 0;
        font-size: 0.85em;
        color: #0066cc;
    }
    .user-message {
        background-color: #0066cc;
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 10px 15px;
        margin: 5px 0;
        text-align: right;
        max-width: 80%;
        margin-left: auto;
    }
    .bot-message {
        background-color: #ffffff;
        color:#0066cc;
        border-radius: 18px 18px 18px 4px;
        padding: 10px 15px;
        margin: 5px 0;
        max-width: 80%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .header-box {
        background: linear-gradient(135deg, #0066cc, #004499);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────
st.markdown("""
<div class="header-box">
    <h1>🏢 HR Document Assistant</h1>
    <p>Ask any question about company HR policies and documents</p>
</div>
""", unsafe_allow_html=True)

# ── LOAD VECTOR STORE ─────────────────────────────────────
@st.cache_resource
def load_db():
    if not os.path.exists("chroma_db"):
        st.error("❌ No vector store found! Run main.py first.")
        return None
    return load_vector_store()

collection = load_db()

# ── SIDEBAR ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    num_chunks = st.slider("Number of chunks to retrieve", 3, 10, 5)
    show_sources = st.toggle("Show source documents", value=True)
    show_chunks = st.toggle("Show retrieved chunks", value=False)

    st.markdown("---")
    st.markdown("### 📄 Documents Loaded")
    if collection:
        st.success(f"✅ {collection.count()} chunks ready")
        st.info("""
        - Employee Handbook (Nonprofits)
        - Employee Handbook
        - HR Policy Manual 2023
        - HR Policy Document
        """)

    st.markdown("---")
    st.markdown("### 💡 Sample Questions")
    sample_questions = [
        "What is the sick leave policy?",
        "What are the working hours?",
        "What is the work from home policy?",
        "What is the code of conduct?",
        "How many days notice period is required?",
        "What is the maternity leave policy?",
    ]
    for q in sample_questions:
        if st.button(q, key=q, use_container_width=True):
            st.session_state.clicked_question = q

# ── CHAT HISTORY ──────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "clicked_question" not in st.session_state:
    st.session_state.clicked_question = None

# ── DISPLAY CHAT HISTORY ──────────────────────────────────
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
        <div class="user-message">
            👤 {message["content"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="bot-message">
            🤖 {message["content"]}
        </div>
        """, unsafe_allow_html=True)

        if show_sources and "sources" in message:
            st.markdown("📎 **Sources:**")
            for source in message["sources"]:
                st.markdown(f"""
                <div class="source-box">
                    📄 {source['source']} — Page {source['page']}
                </div>
                """, unsafe_allow_html=True)

        if show_chunks and "chunks" in message:
            with st.expander("🔍 View retrieved chunks"):
                for i, chunk in enumerate(message["chunks"]):
                    st.markdown(f"**Chunk {i+1}** — {chunk['source']} Page {chunk['page']}")
                    st.text(chunk['text'][:300] + "...")
                    st.divider()

# ── HANDLE QUESTION ───────────────────────────────────────
def process_question(question):
    if not collection:
        st.error("Vector store not loaded!")
        return

    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    # Get answer
    with st.spinner("🔍 Searching HR documents..."):
        chunks = retrieve_chunks(collection, question, k=num_chunks)
        answer = generate_answer(question, chunks)

    # Unique sources only
    seen = set()
    unique_sources = []
    for chunk in chunks:
        key = f"{chunk['source']}_p{chunk['page']}"
        if key not in seen:
            seen.add(key)
            unique_sources.append({
                "source": chunk["source"],
                "page": chunk["page"]
            })

    # Add bot message
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": unique_sources,
        "chunks": chunks
    })

    st.rerun()

# ── INPUT BOX ─────────────────────────────────────────────
st.markdown("---")

# Handle sidebar button click
if st.session_state.clicked_question:
    question = st.session_state.clicked_question
    st.session_state.clicked_question = None
    process_question(question)

# Text input
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            "Ask a question:",
            placeholder="e.g. What is the sick leave policy?",
            label_visibility="collapsed"
        )
    with col2:
        submitted = st.form_submit_button("Send 🚀", use_container_width=True)

if submitted and user_input.strip():
    process_question(user_input.strip())

# ── CLEAR CHAT ────────────────────────────────────────────
if st.session_state.messages:
    if st.button("🗑️ Clear Chat", use_container_width=False):
        st.session_state.messages = []
        st.rerun()

# ── FOOTER ────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:grey; font-size:0.8em;'>"
    "HR Document Assistant — Powered by RAG + Llama 3.3 via Groq"
    "</p>",
    unsafe_allow_html=True
)