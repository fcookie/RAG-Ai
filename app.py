"""Streamlit web application for RAG Document Assistant."""

import streamlit as st
import time
from pathlib import Path
import sys
from typing import List
import json

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.config import Config
from src.document_processor import DocumentProcessor
from src.vector_store import VectorStore
from src.rag_chain import RAGChain
from src.evaluator import RAGEvaluator


# Page configuration
st.set_page_config(
    page_title="RAG Document Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .citation-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1E88E5;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .confidence-high {
        color: #4CAF50;
        font-weight: 600;
    }
    .confidence-medium {
        color: #FF9800;
        font-weight: 600;
    }
    .confidence-low {
        color: #F44336;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None
if 'rag_chain' not in st.session_state:
    st.session_state.rag_chain = None
if 'evaluator' not in st.session_state:
    st.session_state.evaluator = RAGEvaluator()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {}


def initialize_system():
    """Initialize the RAG system."""
    try:
        with st.spinner("Initializing RAG system..."):
            st.session_state.vector_store = VectorStore()
            st.session_state.rag_chain = RAGChain(st.session_state.vector_store)
        st.success("✅ System initialized!")
        return True
    except Exception as e:
        st.error(f"❌ Failed to initialize system: {str(e)}")
        st.info("Make sure to set your OPENAI_API_KEY in the .env file")
        return False


def process_uploaded_file(uploaded_file):
    """Process and index uploaded file."""
    try:
        # Save file temporarily
        temp_path = Config.UPLOAD_DIR / uploaded_file.name
        with open(temp_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        # Process document
        processor = DocumentProcessor()
        documents = processor.process_document(temp_path)
        
        # Add to vector store
        st.session_state.vector_store.add_documents(documents)
        
        # Store file info
        doc_id = documents[0].metadata['doc_id'] if documents else None
        st.session_state.uploaded_files[uploaded_file.name] = {
            'doc_id': doc_id,
            'num_chunks': len(documents),
            'size': uploaded_file.size
        }
        
        return True, len(documents)
    except Exception as e:
        return False, str(e)


def format_confidence(confidence: float) -> str:
    """Format confidence score with color."""
    if confidence >= 0.7:
        css_class = "confidence-high"
        label = "High"
    elif confidence >= 0.4:
        css_class = "confidence-medium"
        label = "Medium"
    else:
        css_class = "confidence-low"
        label = "Low"
    
    return f'<span class="{css_class}">{label} ({confidence:.2%})</span>'


def main():
    """Main application."""
    
    # Header
    st.markdown('<div class="main-header">📚 RAG Document Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Intelligent Document Q&A with Source Citations</div>', unsafe_allow_html=True)
    
    # Initialize system if not done
    if st.session_state.vector_store is None:
        if not initialize_system():
            st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Document Management")
        
        # File upload
        uploaded_files = st.file_uploader(
            "Upload Documents",
            type=['pdf', 'txt', 'md'],
            accept_multiple_files=True,
            help="Upload PDFs, text files, or markdown documents"
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                if uploaded_file.name not in st.session_state.uploaded_files:
                    with st.spinner(f"Processing {uploaded_file.name}..."):
                        success, result = process_uploaded_file(uploaded_file)
                        if success:
                            st.success(f"✅ {uploaded_file.name}: {result} chunks indexed")
                        else:
                            st.error(f"❌ Error processing {uploaded_file.name}: {result}")
        
        # Display uploaded files
        st.subheader("Indexed Documents")
        if st.session_state.uploaded_files:
            for filename, info in st.session_state.uploaded_files.items():
                with st.expander(f"📄 {filename}"):
                    st.write(f"**Chunks:** {info['num_chunks']}")
                    st.write(f"**Size:** {info['size'] / 1024:.1f} KB")
                    if st.button(f"Remove", key=f"remove_{filename}"):
                        st.session_state.vector_store.delete_document(info['doc_id'])
                        del st.session_state.uploaded_files[filename]
                        st.rerun()
        else:
            st.info("No documents uploaded yet")
        
        # Collection stats
        st.divider()
        st.subheader("📊 Statistics")
        stats = st.session_state.vector_store.get_collection_stats()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Documents", stats['unique_documents'])
        with col2:
            st.metric("Chunks", stats['total_chunks'])
        
        # Settings
        st.divider()
        st.subheader("⚙️ Settings")
        
        search_mode = st.selectbox(
            "Search Mode",
            ["hybrid", "vector", "keyword"],
            help="Hybrid combines vector similarity and keyword matching"
        )
        
        use_conversation = st.checkbox(
            "Conversation Memory",
            value=Config.ENABLE_CONVERSATION_MEMORY,
            help="Remember previous questions in the conversation"
        )
        
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.session_state.rag_chain.clear_history()
            st.rerun()
        
        # Clear all data
        if st.button("🗑️ Clear All Data", type="secondary"):
            st.session_state.vector_store.clear_collection()
            st.session_state.uploaded_files = {}
            st.session_state.chat_history = []
            st.success("✅ All data cleared!")
            st.rerun()

    # Main content - Chat Interface
    st.subheader("💬 Ask Questions About Your Documents")

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if "citations" in message and message["citations"]:
                with st.expander("📚 View Citations"):
                    for i, citation in enumerate(message["citations"], 1):
                        st.markdown(f"""
                        <div class="citation-box">
                            <strong>Citation {i}:</strong><br>
                            📄 {citation.source}<br>
                            📖 Page: {citation.page if citation.page else 'N/A'}<br>
                            {f"📑 Section: {citation.section}<br>" if citation.section else ""}
                        </div>
                        """, unsafe_allow_html=True)

            if "confidence" in message:
                st.markdown(f"**Confidence:** {format_confidence(message['confidence'])}", unsafe_allow_html=True)

    # Chat input - OUTSIDE all containers
    if question := st.chat_input("Ask a question about your documents..."):
        if not st.session_state.uploaded_files:
            st.warning("⚠️ Please upload documents first!")
        else:
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": question})

            # Display user message
            with st.chat_message("user"):
                st.markdown(question)

            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    start_time = time.time()
                    response = st.session_state.rag_chain.query(
                        question,
                        use_conversation_history=use_conversation,
                        search_mode=search_mode
                    )
                    response_time = time.time() - start_time

                st.markdown(response.answer)

                # Display citations
                if response.citations:
                    with st.expander("📚 View Citations"):
                        for i, citation in enumerate(response.citations, 1):
                            st.markdown(f"""
                            <div class="citation-box">
                                <strong>Citation {i}:</strong><br>
                                📄 {citation.source}<br>
                                📖 Page: {citation.page if citation.page else 'N/A'}<br>
                                {f"📑 Section: {citation.section}<br>" if citation.section else ""}
                            </div>
                            """, unsafe_allow_html=True)

                # Display confidence
                st.markdown(f"**Confidence:** {format_confidence(response.confidence)}", unsafe_allow_html=True)
                st.caption(f"⏱️ Response time: {response_time:.2f}s")

                # Add assistant message
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response.answer,
                    "citations": response.citations,
                    "confidence": response.confidence
                })

            # Rerun to update chat display
            st.rerun()


if __name__ == "__main__":
    main()