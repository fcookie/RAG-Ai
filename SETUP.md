# Quick Setup Guide

## 1. Install Dependencies

```bash
cd rag_document_assistant
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configure API Key

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-key-here
```

## 3. Run the Application

### Option A: Web Interface (Recommended)

```bash
streamlit run app.py
```

Open browser to `http://localhost:8501`

### Option B: Command Line

```bash
# Index documents
python cli.py index-dir ./data/uploads

# Interactive mode
python cli.py interactive

# Single query
python cli.py query "What are the main findings?"
```

### Option C: Jupyter Notebook

```bash
jupyter notebook notebooks/example_usage.ipynb
```

## 4. Test the System

1. Upload a PDF document
2. Ask questions like:
   - "What is this document about?"
   - "Summarize the key points"
   - "What methodology was used?"

## Troubleshooting

**No module named 'src'**
- Make sure you're in the project directory
- Run: `export PYTHONPATH="${PYTHONPATH}:$(pwd)"`

**OpenAI API errors**
- Check your API key is correct
- Verify you have API credits
- Check your internet connection

**Slow performance**
- Reduce CHUNK_SIZE in .env
- Use gpt-3.5-turbo instead of gpt-4
- Reduce TOP_K_RESULTS

## Next Steps

- Read the full [README.md](README.md)
- Try the [example notebook](notebooks/example_usage.ipynb)
- Customize prompts in `src/rag_chain.py`
- Add more document types in `src/document_processor.py`

## Support

For issues or questions, check:
1. Requirements are installed correctly
2. API key is configured
3. Documents are valid PDFs/text files
4. Python version is 3.8+
