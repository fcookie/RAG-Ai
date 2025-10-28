"""Vector store management for document embeddings and retrieval."""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np

import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi

from .config import Config


class VectorStore:
    """Manage vector database for document embeddings."""
    
    def __init__(self, collection_name: str = None):
        """Initialize vector store.
        
        Args:
            collection_name: Name of the collection (default from config)
        """
        self.collection_name = collection_name or Config.COLLECTION_NAME
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=Config.EMBEDDING_MODEL,
            openai_api_key=Config.OPENAI_API_KEY
        )
        
        # Initialize Chroma client
        self.client = chromadb.Client(Config.get_chroma_settings())
        
        # Initialize or get collection
        self.vectorstore = Chroma(
            client=self.client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(Config.CHROMA_DIR)
        )
        
        print(f"Vector store initialized: {self.collection_name}")
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to vector store.
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of document IDs
        """
        if not documents:
            return []
        
        # Add to vector store
        ids = self.vectorstore.add_documents(documents)
        
        # Persist changes
        self.vectorstore.persist()
        
        print(f"Added {len(documents)} documents to vector store")
        
        return ids
    
    def similarity_search(
        self,
        query: str,
        k: int = None,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Document, float]]:
        """Perform similarity search.
        
        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Metadata filters
            
        Returns:
            List of (Document, score) tuples
        """
        k = k or Config.TOP_K_RESULTS
        
        # Perform similarity search with scores
        results = self.vectorstore.similarity_search_with_relevance_scores(
            query=query,
            k=k,
            filter=filter_dict
        )
        
        # Filter by similarity threshold
        filtered_results = [
            (doc, score) for doc, score in results
            if score >= Config.SIMILARITY_THRESHOLD
        ]
        
        return filtered_results
    
    def get_all_documents(self) -> List[Document]:
        """Retrieve all documents from vector store.
        
        Returns:
            List of all documents
        """
        collection = self.client.get_collection(self.collection_name)
        results = collection.get()
        
        documents = []
        if results and results['documents']:
            for i, doc_text in enumerate(results['documents']):
                metadata = results['metadatas'][i] if results['metadatas'] else {}
                documents.append(Document(page_content=doc_text, metadata=metadata))
        
        return documents
    
    def delete_document(self, doc_id: str):
        """Delete documents by doc_id.
        
        Args:
            doc_id: Document ID to delete
        """
        collection = self.client.get_collection(self.collection_name)
        
        # Get all documents with this doc_id
        results = collection.get(where={"doc_id": doc_id})
        
        if results and results['ids']:
            collection.delete(ids=results['ids'])
            print(f"Deleted document: {doc_id}")
    
    def clear_collection(self):
        """Clear all documents from collection."""
        self.client.delete_collection(self.collection_name)
        self.vectorstore = Chroma(
            client=self.client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(Config.CHROMA_DIR)
        )
        print(f"Cleared collection: {self.collection_name}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        collection = self.client.get_collection(self.collection_name)
        count = collection.count()
        
        # Get unique documents
        all_docs = self.get_all_documents()
        unique_docs = set()
        for doc in all_docs:
            if 'doc_id' in doc.metadata:
                unique_docs.add(doc.metadata['doc_id'])
        
        return {
            'total_chunks': count,
            'unique_documents': len(unique_docs),
            'collection_name': self.collection_name
        }


class HybridRetriever:
    """Hybrid retrieval combining vector search and keyword search."""
    
    def __init__(self, vector_store: VectorStore):
        """Initialize hybrid retriever.
        
        Args:
            vector_store: VectorStore instance
        """
        self.vector_store = vector_store
        self.bm25 = None
        self.documents = []
        self._update_bm25_index()
    
    def _update_bm25_index(self):
        """Update BM25 index with current documents."""
        self.documents = self.vector_store.get_all_documents()
        
        if self.documents:
            # Tokenize documents for BM25
            tokenized_docs = [doc.page_content.lower().split() for doc in self.documents]
            self.bm25 = BM25Okapi(tokenized_docs)
    
    def bm25_search(self, query: str, k: int = 10) -> List[Tuple[Document, float]]:
        """Perform BM25 keyword search.
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List of (Document, score) tuples
        """
        if not self.bm25:
            return []
        
        # Tokenize query
        tokenized_query = query.lower().split()
        
        # Get BM25 scores
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top-k results
        top_indices = np.argsort(scores)[::-1][:k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                results.append((self.documents[idx], float(scores[idx])))
        
        return results
    
    def hybrid_search(
        self,
        query: str,
        k: int = None,
        alpha: float = 0.5
    ) -> List[Tuple[Document, float]]:
        """Perform hybrid search combining vector and keyword search.
        
        Args:
            query: Search query
            k: Number of results
            alpha: Weight for vector search (1-alpha for BM25)
            
        Returns:
            List of (Document, score) tuples sorted by combined score
        """
        k = k or Config.TOP_K_RESULTS
        
        # Perform both searches
        vector_results = self.vector_store.similarity_search(query, k=k*2)
        bm25_results = self.bm25_search(query, k=k*2)
        
        # Normalize scores
        def normalize_scores(results: List[Tuple[Document, float]]) -> List[Tuple[Document, float]]:
            if not results:
                return []
            scores = [score for _, score in results]
            max_score = max(scores) if scores else 1.0
            min_score = min(scores) if scores else 0.0
            score_range = max_score - min_score if max_score != min_score else 1.0
            
            return [
                (doc, (score - min_score) / score_range)
                for doc, score in results
            ]
        
        vector_results = normalize_scores(vector_results)
        bm25_results = normalize_scores(bm25_results)
        
        # Combine scores
        combined_scores = {}
        
        for doc, score in vector_results:
            doc_key = doc.page_content
            combined_scores[doc_key] = {
                'doc': doc,
                'score': alpha * score
            }
        
        for doc, score in bm25_results:
            doc_key = doc.page_content
            if doc_key in combined_scores:
                combined_scores[doc_key]['score'] += (1 - alpha) * score
            else:
                combined_scores[doc_key] = {
                    'doc': doc,
                    'score': (1 - alpha) * score
                }
        
        # Sort by combined score
        sorted_results = sorted(
            combined_scores.values(),
            key=lambda x: x['score'],
            reverse=True
        )
        
        # Return top-k
        return [(item['doc'], item['score']) for item in sorted_results[:k]]
    
    def rerank_results(
        self,
        query: str,
        results: List[Tuple[Document, float]]
    ) -> List[Tuple[Document, float]]:
        """Rerank results using cross-encoder (optional enhancement).
        
        Args:
            query: Original query
            results: Initial retrieval results
            
        Returns:
            Reranked results
        """
        # TODO: Implement cross-encoder reranking for better precision
        # For now, return results as-is
        return results
