# 📚 RAG-Powered Document Assistant

An intelligent document Q&A system that ingests PDFs, research papers, and technical documentation to answer questions with accurate source citations.

## 🌟 Features

### Core Capabilities
- **Multi-Document Support**: Upload and query multiple PDFs, text files, and markdown documents
- **Source Citations**: Every answer includes citations with source document, page numbers, and sections
- **Conversation Memory**: Maintains context across follow-up questions
- **Hybrid Search**: Combines vector similarity search with keyword matching (BM25)
- **Document Comparison**: Compare information across multiple documents
- **Confidence Scoring**: Each answer includes a confidence score based on retrieval quality

### Technical Features
- **Semantic Chunking**: Intelligent text splitting that preserves document structure
- **Vector Database**: ChromaDB for efficient similarity search
- **LLM-Powered**: Uses GPT-4 for answer generation
- **Comprehensive Evaluation**: Built-in metrics for answer relevance, citation accuracy, and faithfulness

## 🏗️ Architecture

```
User Query → Query Processing → Hybrid Retrieval (Vector + BM25)
    ↓
Retrieved Chunks → Context Formation → LLM Generation
    ↓
Answer with Citations → Evaluation Metrics → Response
```

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- 2GB+ RAM (for embeddings and vector store)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd rag_document_assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### Uploading Documents

1. Click the sidebar file uploader
2. Select one or more PDF, TXT, or Markdown files
3. Wait for processing (documents are chunked and indexed automatically)
4. View indexed documents and statistics in the sidebar

### Asking Questions

1. Type your question in the chat input
2. The system will:
   - Retrieve relevant document chunks
   - Generate an answer with citations
   - Display confidence score
3. View citations by clicking "View Citations"

### Example Questions

**Factual Questions:**
- "What are the key findings in the research paper?"
- "What is the revenue reported in the financial statement?"

**Analytical Questions:**
- "Why did the authors choose this methodology?"
- "How does the proposed solution work?"

**Comparison Questions:**
- "Compare the results from Study A and Study B"
- "What are the differences between the 2023 and 2024 reports?"

### Document Comparison Mode

1. Navigate to the "Document Comparison" tab
2. Select 2+ documents to compare
3. Enter your comparison question
4. Click "Compare" to get a structured comparison

### Evaluation Mode

1. Navigate to the "Evaluation" tab
2. Enter a test question
3. Click "Run Evaluation" to get detailed metrics:
   - Answer Relevance (0-1)
   - Citation Accuracy (0-1)
   - Faithfulness to Source (0-1)
   - Retrieval Precision@K (0-1)
   - Response Time

## 🔧 Configuration Options

Edit `.env` to customize:

```env
# Model Selection
EMBEDDING_MODEL=text-embedding-3-small  # or text-embedding-3-large
LLM_MODEL=gpt-4-turbo-preview  # or gpt-4, gpt-3.5-turbo

# Generation Parameters
TEMPERATURE=0.1  # Lower = more focused, Higher = more creative

# Chunking Strategy
CHUNK_SIZE=1000  # Characters per chunk
CHUNK_OVERLAP=200  # Overlap between chunks

# Retrieval Settings
TOP_K_RESULTS=5  # Number of chunks to retrieve
SIMILARITY_THRESHOLD=0.7  # Minimum similarity score

# Features
ENABLE_CONVERSATION_MEMORY=true  # Remember conversation context
```

## 📊 Evaluation Metrics

### Answer Relevance
Measures how well the answer addresses the question (0-1)

### Citation Accuracy
Verifies that citations match retrieved documents (0-1)

### Faithfulness
Ensures answer claims are supported by context (0-1)

### Retrieval Precision@K
Percentage of retrieved chunks that are relevant (0-1)

### Response Time
Time taken to generate answer (seconds)

## 🎯 Use Cases

### Medical Research
- Upload research papers
- Ask diagnostic questions
- Compare treatment approaches
- Find evidence-based recommendations

### Legal Analysis
- Upload legal documents and contracts
- Query specific clauses
- Compare documents for inconsistencies
- Extract key obligations

### Financial Analysis
- Upload financial reports (10-K, 10-Q)
- Compare quarterly/annual performance
- Extract specific metrics
- Analyze trends across documents

### Technical Documentation
- Upload API docs, manuals, specifications
- Answer "how-to" questions
- Find configuration instructions
- Compare versions

## 🔬 Advanced Features

### Custom Chunking Strategies

Edit `src/document_processor.py` to implement custom chunking:

```python
# Fixed-size chunking
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

# Semantic chunking by sections
sections = self.extract_sections(text)
```

### Hybrid Search Tuning

Adjust the alpha parameter in `src/vector_store.py`:

```python
# Alpha = 1.0: Pure vector search
# Alpha = 0.0: Pure keyword search
# Alpha = 0.5: Balanced hybrid
results = retriever.hybrid_search(query, alpha=0.7)
```

### Custom Prompts

Modify prompts in `src/rag_chain.py` for domain-specific behavior:

```python
system_message = """You are a medical expert assistant..."""
```

## 📁 Project Structure

```
rag_document_assistant/
├── app.py                      # Streamlit web interface
├── requirements.txt            # Python dependencies
├── .env.example               # Configuration template
├── README.md                  # This file
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── document_processor.py # PDF parsing and chunking
│   ├── vector_store.py        # ChromaDB and retrieval
│   ├── rag_chain.py           # Answer generation
│   └── evaluator.py           # Evaluation metrics
├── data/
│   ├── chroma_db/            # Vector database (created on first run)
│   └── uploads/              # Uploaded documents
└── tests/                     # Unit tests (to be implemented)
```

## 🧪 Testing

### Manual Testing

1. Upload a sample document
2. Ask questions and verify:
   - Answers are accurate and relevant
   - Citations match the source
   - Confidence scores are reasonable

### Automated Evaluation

```python
from src.evaluator import RAGEvaluator

evaluator = RAGEvaluator()
metrics = evaluator.evaluate_response(question, response, response_time)
print(metrics)
```

## 🐛 Troubleshooting

### Issue: "Configuration warning: OPENAI_API_KEY is required"
**Solution**: Add your OpenAI API key to the `.env` file

### Issue: Slow response times
**Solutions**:
- Reduce `CHUNK_SIZE` for faster retrieval
- Use `gpt-3.5-turbo` instead of GPT-4
- Reduce `TOP_K_RESULTS`

### Issue: Poor citation accuracy
**Solutions**:
- Increase `CHUNK_SIZE` to capture more context
- Adjust `SIMILARITY_THRESHOLD`
- Use hybrid search instead of pure vector search

### Issue: Out of memory errors
**Solutions**:
- Process documents in smaller batches
- Reduce `CHUNK_SIZE`
- Use CPU instead of GPU for embeddings

## 🔐 Security Considerations

- **API Keys**: Never commit `.env` file to version control
- **Document Privacy**: Documents are stored locally; consider encryption for sensitive data
- **Rate Limiting**: OpenAI API has rate limits; implement retry logic for production
- **Input Validation**: Validate file types and sizes before processing

## 📈 Performance Tips

1. **Batch Processing**: Upload multiple documents at once
2. **Caching**: ChromaDB persists data between sessions
3. **Hybrid Search**: Best balance of speed and accuracy
4. **Parallel Processing**: Process multiple chunks concurrently (future enhancement)

## 🛣️ Roadmap

- [ ] Support for more file types (DOCX, XLSX, HTML)
- [ ] Advanced re-ranking with cross-encoders
- [ ] Multi-modal support (images, tables)
- [ ] Cloud deployment guide (AWS, GCP, Azure)
- [ ] API endpoint for programmatic access
- [ ] Batch evaluation suite
- [ ] User authentication and document isolation
- [ ] Conversation export and sharing

## 📚 References

- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [RAG Best Practices](https://www.anthropic.com/index/contextual-retrieval)

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional document formats
- Better chunking strategies
- Advanced retrieval methods
- UI/UX enhancements
- Documentation improvements

## 📄 License

MIT License - feel free to use this project for any purpose.

## 🙋 Support

For issues, questions, or suggestions:
1. Check the Troubleshooting section
2. Review closed issues in the repository
3. Open a new issue with detailed information

## 🎓 Learning Resources

### Understanding RAG
- [What is RAG?](https://www.anthropic.com/index/retrieval-augmented-generation)
- [Building RAG Systems](https://python.langchain.com/docs/use_cases/question_answering/)

### Vector Databases
- [Vector Database Fundamentals](https://www.pinecone.io/learn/vector-database/)
- [Embeddings Explained](https://platform.openai.com/docs/guides/embeddings/what-are-embeddings)

### Prompt Engineering
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [OpenAI Best Practices](https://platform.openai.com/docs/guides/prompt-engineering)

---

**Built with ❤️ using LangChain, ChromaDB, and OpenAI**

Happy Document Q&A! 📚✨
