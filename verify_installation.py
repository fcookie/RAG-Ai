#!/usr/bin/env python3
"""
Installation Verification Script for RAG Document Assistant
Run this after installation to verify everything is set up correctly.
"""

import sys
from pathlib import Path

def print_header(text):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def check_mark(passed):
    """Return check mark or X."""
    return "✅" if passed else "❌"

def verify_installation():
    """Verify the installation."""
    print_header("RAG Document Assistant - Installation Verification")
    
    all_passed = True
    
    # Check Python version
    print("1. Checking Python version...")
    python_version = sys.version_info
    python_ok = python_version >= (3, 8)
    print(f"   {check_mark(python_ok)} Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    if not python_ok:
        print("   ⚠️  Python 3.8+ required")
    all_passed &= python_ok
    
    # Check required packages
    print("\n2. Checking required packages...")
    required_packages = [
        'langchain',
        'chromadb',
        'openai',
        'streamlit',
        'PyPDF2',
        'pdfplumber',
        'numpy',
        'tiktoken'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_').lower())
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - NOT INSTALLED")
            all_passed = False
    
    # Check project structure
    print("\n3. Checking project structure...")
    required_files = [
        'src/__init__.py',
        'src/config.py',
        'src/document_processor.py',
        'src/vector_store.py',
        'src/rag_chain.py',
        'src/evaluator.py',
        'app.py',
        'cli.py',
        'requirements.txt',
        '.env.example'
    ]
    
    for file in required_files:
        file_path = Path(file)
        exists = file_path.exists()
        print(f"   {check_mark(exists)} {file}")
        all_passed &= exists
    
    # Check directories
    print("\n4. Checking directories...")
    required_dirs = ['src', 'data', 'data/uploads', 'notebooks']
    
    for directory in required_dirs:
        dir_path = Path(directory)
        exists = dir_path.exists()
        print(f"   {check_mark(exists)} {directory}/")
        if not exists:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"      Created {directory}/")
    
    # Check .env file
    print("\n5. Checking configuration...")
    env_exists = Path('.env').exists()
    print(f"   {check_mark(env_exists)} .env file")
    
    if env_exists:
        with open('.env', 'r') as f:
            env_content = f.read()
            has_api_key = 'OPENAI_API_KEY' in env_content and 'sk-' in env_content
            print(f"   {check_mark(has_api_key)} OpenAI API key configured")
            if not has_api_key:
                print("      ⚠️  Set your OpenAI API key in .env file")
    else:
        print("      ⚠️  Copy .env.example to .env and add your API key")
        all_passed = False
    
    # Test imports
    print("\n6. Testing module imports...")
    try:
        from src.config import Config
        print(f"   ✅ Config module")
        
        from src.document_processor import DocumentProcessor
        print(f"   ✅ DocumentProcessor module")
        
        from src.vector_store import VectorStore
        print(f"   ✅ VectorStore module")
        
        from src.rag_chain import RAGChain
        print(f"   ✅ RAGChain module")
        
        from src.evaluator import RAGEvaluator
        print(f"   ✅ Evaluator module")
        
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        all_passed = False
    
    # Summary
    print_header("Verification Summary")
    
    if all_passed:
        print("✅ All checks passed!")
        print("\nYou're ready to go! Try these commands:")
        print("\n  Streamlit Web Interface:")
        print("    streamlit run app.py")
        print("\n  Command Line Interface:")
        print("    python cli.py interactive")
        print("\n  Jupyter Notebook:")
        print("    jupyter notebook notebooks/example_usage.ipynb")
    else:
        print("❌ Some checks failed.")
        print("\nPlease fix the issues above and run this script again.")
        print("\nCommon fixes:")
        print("  - Install packages: pip install -r requirements.txt")
        print("  - Create .env file: cp .env.example .env")
        print("  - Add API key to .env file")
    
    print()
    return all_passed

if __name__ == '__main__':
    success = verify_installation()
    sys.exit(0 if success else 1)
