#!/usr/bin/env python3
"""Command-line interface for RAG Document Assistant."""

import argparse
import sys
from pathlib import Path
import time
from typing import List

from src.config import Config
from src.document_processor import DocumentProcessor
from src.vector_store import VectorStore
from src.rag_chain import RAGChain
from src.evaluator import RAGEvaluator


class RAGCli:
    """CLI for RAG Document Assistant."""
    
    def __init__(self):
        """Initialize CLI."""
        self.vector_store = VectorStore()
        self.rag_chain = RAGChain(self.vector_store)
        self.processor = DocumentProcessor()
        self.evaluator = RAGEvaluator()
    
    def index_document(self, file_path: str):
        """Index a document.
        
        Args:
            file_path: Path to document file
        """
        path = Path(file_path)
        
        if not path.exists():
            print(f"Error: File not found: {file_path}")
            return
        
        print(f"Processing {path.name}...")
        
        try:
            documents = self.processor.process_document(path)
            self.vector_store.add_documents(documents)
            print(f"✅ Indexed {len(documents)} chunks from {path.name}")
        except Exception as e:
            print(f"❌ Error processing document: {e}")
    
    def index_directory(self, dir_path: str):
        """Index all documents in a directory.
        
        Args:
            dir_path: Path to directory
        """
        directory = Path(dir_path)
        
        if not directory.is_dir():
            print(f"Error: Directory not found: {dir_path}")
            return
        
        # Find all supported files
        files = []
        for ext in ['.pdf', '.txt', '.md', '.markdown']:
            files.extend(directory.glob(f"**/*{ext}"))
        
        if not files:
            print(f"No supported files found in {dir_path}")
            return
        
        print(f"Found {len(files)} documents to index")
        
        for file_path in files:
            self.index_document(str(file_path))
    
    def query(self, question: str, mode: str = "hybrid", evaluate: bool = False):
        """Query the system.
        
        Args:
            question: Question to ask
            mode: Search mode (vector, keyword, hybrid)
            evaluate: Whether to evaluate the response
        """
        stats = self.vector_store.get_collection_stats()
        
        if stats['total_chunks'] == 0:
            print("No documents indexed. Use 'index' command first.")
            return
        
        print(f"\n📚 Searching {stats['unique_documents']} documents ({stats['total_chunks']} chunks)...")
        print(f"Question: {question}\n")
        
        start_time = time.time()
        response = self.rag_chain.query(question, search_mode=mode)
        response_time = time.time() - start_time
        
        # Print answer
        print("Answer:")
        print("-" * 80)
        print(response.answer)
        print("-" * 80)
        
        # Print citations
        if response.citations:
            print("\n📖 Citations:")
            for i, citation in enumerate(response.citations, 1):
                print(f"  [{i}] {citation.source}, Page {citation.page if citation.page else 'N/A'}")
        
        # Print metadata
        print(f"\n⚡ Confidence: {response.confidence:.2%}")
        print(f"⏱️  Response Time: {response_time:.2f}s")
        
        # Evaluate if requested
        if evaluate:
            print("\n📊 Evaluating response...")
            metrics = self.evaluator.evaluate_response(question, response, response_time)
            
            print("\nEvaluation Metrics:")
            print(f"  Answer Relevance: {metrics.answer_relevance:.2%}")
            print(f"  Citation Accuracy: {metrics.citation_accuracy:.2%}")
            print(f"  Faithfulness: {metrics.faithfulness:.2%}")
            print(f"  Retrieval Precision: {metrics.retrieval_precision:.2%}")
    
    def interactive(self):
        """Start interactive query mode."""
        stats = self.vector_store.get_collection_stats()
        
        if stats['total_chunks'] == 0:
            print("No documents indexed. Use 'index' command first.")
            return
        
        print(f"\n📚 RAG Document Assistant - Interactive Mode")
        print(f"Indexed: {stats['unique_documents']} documents ({stats['total_chunks']} chunks)")
        print("\nCommands:")
        print("  - Type your question to get an answer")
        print("  - 'quit' or 'exit' to exit")
        print("  - 'clear' to clear conversation history")
        print("  - 'stats' to show collection statistics")
        print()
        
        while True:
            try:
                question = input("\n❓ Question: ").strip()
                
                if not question:
                    continue
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if question.lower() == 'clear':
                    self.rag_chain.clear_history()
                    print("✅ Conversation history cleared")
                    continue
                
                if question.lower() == 'stats':
                    stats = self.vector_store.get_collection_stats()
                    print(f"\nCollection Statistics:")
                    print(f"  Documents: {stats['unique_documents']}")
                    print(f"  Chunks: {stats['total_chunks']}")
                    continue
                
                # Query
                start_time = time.time()
                response = self.rag_chain.query(question)
                response_time = time.time() - start_time
                
                print(f"\n💬 Answer:")
                print(response.answer)
                
                if response.citations:
                    print(f"\n📖 Sources: ", end="")
                    sources = set(c.source for c in response.citations)
                    print(", ".join(sources))
                
                print(f"\n⚡ Confidence: {response.confidence:.2%} | ⏱️  {response_time:.2f}s")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def list_documents(self):
        """List all indexed documents."""
        all_docs = self.vector_store.get_all_documents()
        
        if not all_docs:
            print("No documents indexed.")
            return
        
        # Group by document
        doc_map = {}
        for doc in all_docs:
            filename = doc.metadata.get('filename', 'Unknown')
            doc_id = doc.metadata.get('doc_id', 'unknown')
            
            if doc_id not in doc_map:
                doc_map[doc_id] = {
                    'filename': filename,
                    'chunks': 0,
                    'pages': set()
                }
            
            doc_map[doc_id]['chunks'] += 1
            if 'page' in doc.metadata:
                doc_map[doc_id]['pages'].add(doc.metadata['page'])
        
        print(f"\n📚 Indexed Documents ({len(doc_map)} documents):\n")
        
        for i, (doc_id, info) in enumerate(doc_map.items(), 1):
            pages = f"{len(info['pages'])} pages" if info['pages'] else "N/A"
            print(f"{i}. {info['filename']}")
            print(f"   ID: {doc_id}")
            print(f"   Chunks: {info['chunks']} | Pages: {pages}\n")
    
    def clear_collection(self):
        """Clear all indexed documents."""
        confirm = input("Are you sure you want to delete all documents? (yes/no): ")
        
        if confirm.lower() == 'yes':
            self.vector_store.clear_collection()
            print("✅ All documents cleared")
        else:
            print("Operation cancelled")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="RAG Document Assistant - Query documents with AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Index a single document
  python cli.py index document.pdf
  
  # Index all documents in a directory
  python cli.py index-dir ./documents
  
  # Ask a question
  python cli.py query "What are the main findings?"
  
  # Interactive mode
  python cli.py interactive
  
  # List indexed documents
  python cli.py list
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Index a document')
    index_parser.add_argument('file', help='Path to document file')
    
    # Index directory command
    index_dir_parser = subparsers.add_parser('index-dir', help='Index all documents in a directory')
    index_dir_parser.add_argument('directory', help='Path to directory')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query the system')
    query_parser.add_argument('question', help='Question to ask')
    query_parser.add_argument('--mode', choices=['vector', 'keyword', 'hybrid'], 
                             default='hybrid', help='Search mode')
    query_parser.add_argument('--evaluate', action='store_true', 
                             help='Evaluate response quality')
    
    # Interactive command
    subparsers.add_parser('interactive', help='Start interactive query mode')
    
    # List command
    subparsers.add_parser('list', help='List indexed documents')
    
    # Clear command
    subparsers.add_parser('clear', help='Clear all indexed documents')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize CLI
    cli = RAGCli()
    
    # Execute command
    if args.command == 'index':
        cli.index_document(args.file)
    elif args.command == 'index-dir':
        cli.index_directory(args.directory)
    elif args.command == 'query':
        cli.query(args.question, mode=args.mode, evaluate=args.evaluate)
    elif args.command == 'interactive':
        cli.interactive()
    elif args.command == 'list':
        cli.list_documents()
    elif args.command == 'clear':
        cli.clear_collection()


if __name__ == '__main__':
    main()
