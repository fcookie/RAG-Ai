"""Document processing module for extracting and chunking text from various formats."""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import hashlib

import PyPDF2
import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from .config import Config


@dataclass
class DocumentMetadata:
    """Metadata for processed documents."""
    filename: str
    source: str
    page: Optional[int] = None
    total_pages: Optional[int] = None
    section: Optional[str] = None
    doc_id: Optional[str] = None


class DocumentProcessor:
    """Process and chunk documents for RAG system."""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """Initialize document processor.
        
        Args:
            chunk_size: Size of text chunks (default from config)
            chunk_overlap: Overlap between chunks (default from config)
        """
        self.chunk_size = chunk_size or Config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or Config.CHUNK_OVERLAP
        
        # Initialize text splitters
        self.recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
    def extract_text_from_pdf(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """Extract text from PDF with page-level metadata.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of dictionaries with page content and metadata
        """
        pages_content = []
        
        try:
            # Try pdfplumber first (better for complex layouts)
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    if text and text.strip():
                        pages_content.append({
                            'text': text,
                            'page': page_num,
                            'total_pages': total_pages
                        })
        except Exception as e:
            print(f"pdfplumber failed, trying PyPDF2: {e}")
            
            # Fallback to PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    total_pages = len(pdf_reader.pages)
                    
                    for page_num, page in enumerate(pdf_reader.pages, start=1):
                        text = page.extract_text()
                        if text and text.strip():
                            pages_content.append({
                                'text': text,
                                'page': page_num,
                                'total_pages': total_pages
                            })
            except Exception as e:
                raise ValueError(f"Failed to extract text from PDF: {e}")
        
        return pages_content
    
    def extract_sections(self, text: str) -> List[Dict[str, str]]:
        """Extract sections from text based on headers.
        
        Args:
            text: Input text
            
        Returns:
            List of sections with titles
        """
        # Pattern to match common section headers
        section_pattern = r'^(#{1,3}\s+.+|[A-Z][A-Za-z\s]+:|\d+\.\s+[A-Z].+)$'
        
        sections = []
        current_section = {"title": "Introduction", "content": ""}
        
        for line in text.split('\n'):
            if re.match(section_pattern, line.strip()):
                if current_section["content"].strip():
                    sections.append(current_section)
                current_section = {"title": line.strip(), "content": ""}
            else:
                current_section["content"] += line + "\n"
        
        # Add last section
        if current_section["content"].strip():
            sections.append(current_section)
        
        return sections if sections else [{"title": "Document", "content": text}]
    
    def create_semantic_chunks(self, text: str, metadata: Dict[str, Any]) -> List[Document]:
        """Create semantically meaningful chunks from text.
        
        Args:
            text: Input text
            metadata: Document metadata
            
        Returns:
            List of LangChain Document objects
        """
        # Extract sections first
        sections = self.extract_sections(text)
        
        all_chunks = []
        
        for section in sections:
            section_text = f"{section['title']}\n\n{section['content']}"
            
            # Split into chunks
            chunks = self.recursive_splitter.split_text(section_text)
            
            # Create Document objects with metadata
            for i, chunk in enumerate(chunks):
                chunk_metadata = metadata.copy()
                chunk_metadata['section'] = section['title']
                chunk_metadata['chunk_index'] = i
                
                all_chunks.append(Document(
                    page_content=chunk,
                    metadata=chunk_metadata
                ))
        
        return all_chunks
    
    def process_pdf(self, pdf_path: Path) -> List[Document]:
        """Process PDF file into chunks with metadata.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of Document objects ready for indexing
        """
        # Generate document ID
        doc_id = hashlib.md5(pdf_path.read_bytes()).hexdigest()[:16]
        
        # Extract text by page
        pages = self.extract_text_from_pdf(pdf_path)
        
        all_documents = []
        
        for page_data in pages:
            metadata = {
                'filename': pdf_path.name,
                'source': str(pdf_path),
                'page': page_data['page'],
                'total_pages': page_data['total_pages'],
                'doc_id': doc_id
            }
            
            # Create semantic chunks for this page
            page_chunks = self.create_semantic_chunks(page_data['text'], metadata)
            all_documents.extend(page_chunks)
        
        print(f"Processed {pdf_path.name}: {len(pages)} pages → {len(all_documents)} chunks")
        
        return all_documents
    
    def process_text_file(self, text_path: Path) -> List[Document]:
        """Process plain text or markdown file.
        
        Args:
            text_path: Path to text file
            
        Returns:
            List of Document objects
        """
        doc_id = hashlib.md5(text_path.read_bytes()).hexdigest()[:16]
        
        with open(text_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        metadata = {
            'filename': text_path.name,
            'source': str(text_path),
            'doc_id': doc_id
        }
        
        return self.create_semantic_chunks(text, metadata)
    
    def process_document(self, file_path: Path) -> List[Document]:
        """Process document based on file type.
        
        Args:
            file_path: Path to document
            
        Returns:
            List of processed Document objects
        """
        suffix = file_path.suffix.lower()
        
        if suffix == '.pdf':
            return self.process_pdf(file_path)
        elif suffix in ['.txt', '.md', '.markdown']:
            return self.process_text_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")


class QueryRewriter:
    """Rewrite queries for better retrieval."""
    
    def __init__(self, llm=None):
        """Initialize query rewriter.
        
        Args:
            llm: Language model for query expansion
        """
        self.llm = llm
    
    def expand_query(self, query: str) -> List[str]:
        """Expand query with synonyms and related terms.
        
        Args:
            query: Original query
            
        Returns:
            List of query variations
        """
        # Basic query variations
        variations = [query]
        
        # Add question variations
        if not query.endswith('?'):
            variations.append(f"{query}?")
        
        # Remove question marks for keyword search
        variations.append(query.replace('?', ''))
        
        # TODO: Use LLM for semantic expansion
        
        return variations
    
    def rephrase_for_context(self, query: str, conversation_history: List[str]) -> str:
        """Rephrase query considering conversation context.
        
        Args:
            query: Current query
            conversation_history: Previous conversation turns
            
        Returns:
            Rephrased query
        """
        # If query seems context-dependent and we have history
        if len(query.split()) < 5 and conversation_history:
            # TODO: Use LLM to incorporate context
            pass
        
        return query
