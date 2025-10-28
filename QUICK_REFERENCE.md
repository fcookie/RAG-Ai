# RAG Document Assistant - Quick Reference

## 🚀 5-Minute Quick Start

```bash
# 1. Setup (2 min)
cd rag_document_assistant
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure (1 min)
cp .env.example .env
# Edit .env: OPENAI_API_KEY=sk-your-key-here

# 3. Run (30 sec)
streamlit run app.py

# 4. Use (1 min)
# Upload sample_research_paper.md
# Ask: "What are the main findings?"
```

---

## 📝 Common Commands

### Web Interface
```bash
streamlit run app.py
```

### CLI - Index Documents
```bash
# Single file
python cli.py index document.pdf

# Directory
python cli.py index-dir ./documents

# List indexed
python cli.py list
```

### CLI - Query
```bash
# Single query
python cli.py query "What are the findings?"

# With evaluation
python cli.py query "What is the methodology?" --evaluate

# Interactive mode
python cli.py interactive
```

### Jupyter Notebook
```bash
jupyter notebook notebooks/example_usage.ipynb
```

---

## 🎯 Common Questions

### Simple Queries
```
"What is this document about?"
"Who are the authors?"
"When was this published?"
"What are the main conclusions?"
```

### Detailed Queries
```
"What methodology was used in the study?"
"What were the key findings on [topic]?"
"What are the limitations mentioned?"
"What recommendations do the authors make?"
```

### Comparison Queries
```
"Compare the results from Study A and Study B"
"What are the differences between the 2023 and 2024 reports?"
"How do these findings compare to previous research?"
```

### Analytical Queries
```
"Why did the authors choose this approach?"
"How does the proposed solution work?"
"What evidence supports the main conclusion?"
"What are the implications of these findings?"
```

---

## ⚙️ Configuration Quick Guide

### .env File
```env
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional - Performance
CHUNK_SIZE=1000              # Smaller = faster, less context
CHUNK_OVERLAP=200            # Higher = better continuity
TOP_K_RESULTS=5              # More = slower but comprehensive

# Optional - Models
EMBEDDING_MODEL=text-embedding-3-small  # or -large
LLM_MODEL=gpt-4-turbo-preview          # or gpt-3.5-turbo

# Optional - Features
ENABLE_CONVERSATION_MEMORY=true
SIMILARITY_THRESHOLD=0.7
```

---

## 🔧 Troubleshooting

### Problem: API Key Error
```bash
# Check .env file exists and has key
cat .env | grep OPENAI_API_KEY
```

### Problem: Slow Responses
```env
# In .env, reduce these:
CHUNK_SIZE=500
TOP_K_RESULTS=3
LLM_MODEL=gpt-3.5-turbo
```

### Problem: Poor Citation Accuracy
```env
# In .env, increase these:
CHUNK_SIZE=1500
TOP_K_RESULTS=7
SIMILARITY_THRESHOLD=0.6
```

### Problem: Out of Memory
```bash
# Process fewer documents at once
# Or reduce chunk size in .env
CHUNK_SIZE=500
```

---

## 📊 Evaluation Metrics Guide

| Metric | What It Measures | Good Score |
|--------|------------------|------------|
| Answer Relevance | Does answer address question? | > 0.8 |
| Citation Accuracy | Are citations valid? | > 0.9 |
| Faithfulness | Is answer grounded in sources? | > 0.8 |
| Retrieval Precision | Are retrieved chunks relevant? | > 0.7 |
| Response Time | How long did it take? | < 3s |

---

## 📁 File Locations

```
Configuration:     .env
Vector Database:   data/chroma_db/
Uploaded Docs:     data/uploads/
Evaluation Reports: data/evaluation_report_*.json
Sample Document:   data/uploads/sample_research_paper.md
```

---

## 🎨 Web Interface Tips

### Upload Documents
- Sidebar → File Uploader
- Supports: PDF, TXT, MD
- Multiple files at once

### Ask Questions
- Type in chat input at bottom
- View citations by clicking "View Citations"
- Check confidence score

### Document Comparison
- Tab: "Document Comparison"
- Select 2+ documents
- Enter comparison question

### View Evaluation
- Tab: "Evaluation"
- Enter test question
- Get detailed metrics

---

## 🐍 Programmatic Usage

```python
from src import VectorStore, RAGChain, DocumentProcessor

# Initialize
vector_store = VectorStore()
rag_chain = RAGChain(vector_store)

# Index document
processor = DocumentProcessor()
docs = processor.process_pdf("paper.pdf")
vector_store.add_documents(docs)

# Query
response = rag_chain.query("What are the findings?")
print(response.answer)
print(f"Confidence: {response.confidence:.2%}")

# View citations
for citation in response.citations:
    print(f"- {citation.source}, Page {citation.page}")
```

---

## 🎯 Search Modes

### Vector Search (Semantic)
```python
response = rag_chain.query(question, search_mode="vector")
```
- Best for: Conceptual questions
- Speed: Fast
- Accuracy: Good for semantic similarity

### Keyword Search (BM25)
```python
response = rag_chain.query(question, search_mode="keyword")
```
- Best for: Exact term matching
- Speed: Very fast
- Accuracy: Good for specific terms

### Hybrid Search (Recommended)
```python
response = rag_chain.query(question, search_mode="hybrid")
```
- Best for: Most queries
- Speed: Medium
- Accuracy: Best overall

---

## 📚 Documentation Index

- `README.md` - Full documentation
- `SETUP.md` - Installation guide
- `EXAMPLES.md` - Usage examples
- `PROJECT_SUMMARY.md` - Project overview
- `QUICK_REFERENCE.md` - This file

---

## 💡 Pro Tips

1. **Start Simple:** Use sample document first
2. **Check Citations:** Always verify important info
3. **Use Hybrid Search:** Best accuracy/speed balance
4. **Enable Memory:** For follow-up questions
5. **Evaluate Often:** Check quality of responses
6. **Iterate Queries:** Refine questions for better answers
7. **Monitor Metrics:** Track confidence scores
8. **Customize Prompts:** Edit for your domain

---

## 🆘 Getting Help

1. Check troubleshooting section above
2. Review README.md for detailed info
3. Try EXAMPLES.md for query patterns
4. Check .env configuration
5. Verify API key and credits

---

## 🎉 Next Steps

### Beginner
- [x] Run with sample document
- [ ] Try your own PDF
- [ ] Experiment with questions
- [ ] Check evaluation metrics

### Intermediate
- [ ] Customize chunking strategy
- [ ] Modify system prompts
- [ ] Add new document types
- [ ] Tune retrieval parameters

### Advanced
- [ ] Implement re-ranking
- [ ] Add custom evaluation metrics
- [ ] Build API endpoint
- [ ] Deploy to production

---

**Need more help?** See README.md for comprehensive documentation.

**Ready to start?** Run: `streamlit run app.py`
