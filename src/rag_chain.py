"""RAG chain for answer generation with citations."""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.documents import Document

from .config import Config
from .vector_store import VectorStore, HybridRetriever


@dataclass
class Citation:
    """Citation information."""
    source: str
    page: Optional[int] = None
    section: Optional[str] = None
    chunk_text: str = ""


@dataclass
class RAGResponse:
    """RAG response with answer and citations."""
    answer: str
    citations: List[Citation]
    confidence: float
    retrieved_chunks: List[Document]
    

class RAGChain:
    """RAG chain for document Q&A with citations."""
    
    def __init__(self, vector_store: VectorStore):
        """Initialize RAG chain.
        
        Args:
            vector_store: VectorStore instance
        """
        self.vector_store = vector_store
        self.retriever = HybridRetriever(vector_store)
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=Config.LLM_MODEL,
            temperature=Config.TEMPERATURE,
            openai_api_key=Config.OPENAI_API_KEY
        )
        
        # Conversation memory
        self.conversation_history: List[Any] = []
        
        # Create prompt template
        self.qa_prompt = self._create_qa_prompt()
    
    def _create_qa_prompt(self) -> ChatPromptTemplate:
        """Create prompt template for QA with citations.
        
        Returns:
            ChatPromptTemplate
        """
        system_message = """You are an intelligent document assistant that answers questions based on provided context.

Your responsibilities:
1. Answer questions accurately using ONLY the provided context
2. Include citations for every claim by referencing [Source: filename, Page: X]
3. If information is not in the context, clearly state that
4. Be concise but comprehensive
5. Maintain a professional, helpful tone

Citation format:
- Use [Source: document.pdf, Page: 5] after each claim
- If multiple sources support a claim, list all: [Source: doc1.pdf, Page: 3; doc2.pdf, Page: 7]
- Include section names when relevant: [Source: report.pdf, Page: 2, Section: Introduction]

If asked to compare information across documents, structure your answer clearly and cite each document.
"""
        
        human_template = """Context from documents:
{context}

Question: {question}

Provide a detailed answer with proper citations."""
        
        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", human_template)
        ])
    
    def _format_context(self, documents: List[Tuple[Document, float]]) -> str:
        """Format retrieved documents as context.
        
        Args:
            documents: List of (Document, score) tuples
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, (doc, score) in enumerate(documents, 1):
            metadata = doc.metadata
            source = metadata.get('filename', 'Unknown')
            page = metadata.get('page', 'N/A')
            section = metadata.get('section', '')
            
            context_part = f"""[Chunk {i}]
Source: {source}
Page: {page}
{f"Section: {section}" if section else ""}
Relevance Score: {score:.3f}

Content:
{doc.page_content}

---"""
            context_parts.append(context_part)
        
        return "\n\n".join(context_parts)
    
    def _extract_citations(self, answer: str, retrieved_docs: List[Document]) -> List[Citation]:
        """Extract citations from answer.
        
        Args:
            answer: Generated answer with citations
            retrieved_docs: Retrieved documents
            
        Returns:
            List of Citation objects
        """
        citations = []
        
        # Extract citation patterns from answer
        import re
        citation_pattern = r'\[Source:\s*([^,\]]+)(?:,\s*Page:\s*(\d+))?(?:,\s*Section:\s*([^\]]+))?\]'
        matches = re.finditer(citation_pattern, answer)
        
        for match in matches:
            source = match.group(1).strip()
            page = int(match.group(2)) if match.group(2) else None
            section = match.group(3).strip() if match.group(3) else None
            
            # Find corresponding chunk
            chunk_text = ""
            for doc in retrieved_docs:
                if (doc.metadata.get('filename') == source and
                    (page is None or doc.metadata.get('page') == page)):
                    chunk_text = doc.page_content[:200] + "..."
                    break
            
            citations.append(Citation(
                source=source,
                page=page,
                section=section,
                chunk_text=chunk_text
            ))
        
        return citations
    
    def _calculate_confidence(
        self,
        answer: str,
        retrieved_docs: List[Tuple[Document, float]],
        citations: List[Citation]
    ) -> float:
        """Calculate confidence score for the answer.
        
        Args:
            answer: Generated answer
            retrieved_docs: Retrieved documents with scores
            citations: Extracted citations
            
        Returns:
            Confidence score between 0 and 1
        """
        if not answer or answer.lower().startswith("i don't have"):
            return 0.0
        
        # Factors for confidence:
        # 1. Average retrieval score
        avg_score = sum(score for _, score in retrieved_docs) / len(retrieved_docs) if retrieved_docs else 0
        
        # 2. Number of citations (more citations = more grounded)
        citation_factor = min(len(citations) / 3, 1.0)  # Normalized to 3 citations
        
        # 3. Length of answer (very short might indicate uncertainty)
        length_factor = min(len(answer) / 200, 1.0)
        
        # Weighted average
        confidence = (0.5 * avg_score + 0.3 * citation_factor + 0.2 * length_factor)
        
        return min(max(confidence, 0.0), 1.0)
    
    def query(
        self,
        question: str,
        use_conversation_history: bool = True,
        search_mode: str = "hybrid"
    ) -> RAGResponse:
        """Query the RAG system.
        
        Args:
            question: User question
            use_conversation_history: Whether to use conversation history
            search_mode: Search mode - "vector", "keyword", or "hybrid"
            
        Returns:
            RAGResponse with answer and citations
        """
        # Retrieve relevant documents
        if search_mode == "hybrid":
            retrieved_docs = self.retriever.hybrid_search(question)
        elif search_mode == "vector":
            retrieved_docs = self.vector_store.similarity_search(question)
        else:  # keyword
            retrieved_docs = self.retriever.bm25_search(question)
        
        if not retrieved_docs:
            return RAGResponse(
                answer="I couldn't find any relevant information in the documents to answer this question.",
                citations=[],
                confidence=0.0,
                retrieved_chunks=[]
            )
        
        # Format context
        context = self._format_context(retrieved_docs)
        
        # Prepare messages
        messages = []
        
        # Add conversation history if enabled
        if use_conversation_history and Config.ENABLE_CONVERSATION_MEMORY:
            messages = self.conversation_history.copy()
        
        # Generate answer
        prompt = self.qa_prompt.format_messages(
            context=context,
            question=question,
            chat_history=messages if use_conversation_history else []
        )
        
        response = self.llm.invoke(prompt)
        answer = response.content
        
        # Extract citations
        docs_only = [doc for doc, _ in retrieved_docs]
        citations = self._extract_citations(answer, docs_only)
        
        # Calculate confidence
        confidence = self._calculate_confidence(answer, retrieved_docs, citations)
        
        # Update conversation history
        if Config.ENABLE_CONVERSATION_MEMORY:
            self.conversation_history.append(HumanMessage(content=question))
            self.conversation_history.append(AIMessage(content=answer))
            
            # Keep only last 10 messages
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
        
        return RAGResponse(
            answer=answer,
            citations=citations,
            confidence=confidence,
            retrieved_chunks=docs_only
        )
    
    def compare_documents(
        self,
        question: str,
        doc_ids: List[str]
    ) -> RAGResponse:
        """Compare information across specific documents.
        
        Args:
            question: Comparison question
            doc_ids: List of document IDs to compare
            
        Returns:
            RAGResponse with comparative analysis
        """
        # Retrieve from each document
        all_results = []
        
        for doc_id in doc_ids:
            results = self.vector_store.similarity_search(
                question,
                filter_dict={"doc_id": doc_id}
            )
            all_results.extend(results)
        
        # Sort by relevance
        all_results.sort(key=lambda x: x[1], reverse=True)
        
        # Format context
        context = self._format_context(all_results[:Config.TOP_K_RESULTS * 2])
        
        # Special prompt for comparison
        comparison_prompt = f"""Based on the provided context from multiple documents, compare and contrast the information regarding: {question}

Structure your answer as:
1. Summary of each document's perspective
2. Key similarities
3. Key differences
4. Overall conclusion

Include citations for each point."""
        
        prompt = self.qa_prompt.format_messages(
            context=context,
            question=comparison_prompt,
            chat_history=[]
        )
        
        response = self.llm.invoke(prompt)
        answer = response.content
        
        # Extract citations and calculate confidence
        docs_only = [doc for doc, _ in all_results[:Config.TOP_K_RESULTS * 2]]
        citations = self._extract_citations(answer, docs_only)
        confidence = self._calculate_confidence(answer, all_results[:Config.TOP_K_RESULTS * 2], citations)
        
        return RAGResponse(
            answer=answer,
            citations=citations,
            confidence=confidence,
            retrieved_chunks=docs_only
        )
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
