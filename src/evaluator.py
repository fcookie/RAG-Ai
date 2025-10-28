"""Evaluation module for RAG system performance."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import json
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.documents import Document

from .config import Config
from .rag_chain import RAGResponse


@dataclass
class EvaluationMetrics:
    """Evaluation metrics for RAG responses."""
    answer_relevance: float  # 0-1
    citation_accuracy: float  # 0-1
    faithfulness: float  # 0-1
    retrieval_precision: float  # 0-1
    response_time: float  # seconds
    timestamp: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class RAGEvaluator:
    """Evaluate RAG system performance."""
    
    def __init__(self):
        """Initialize evaluator."""
        self.llm = ChatOpenAI(
            model=Config.LLM_MODEL,
            temperature=0,
            openai_api_key=Config.OPENAI_API_KEY
        )
        
        self.evaluation_history: List[Dict[str, Any]] = []
    
    def evaluate_answer_relevance(
        self,
        question: str,
        answer: str
    ) -> float:
        """Evaluate how relevant the answer is to the question.
        
        Args:
            question: Original question
            answer: Generated answer
            
        Returns:
            Relevance score (0-1)
        """
        prompt = f"""Evaluate the relevance of the answer to the question on a scale of 0-1.

Question: {question}

Answer: {answer}

Provide only a number between 0 and 1, where:
- 1.0 = Perfectly relevant and directly answers the question
- 0.5 = Partially relevant but misses key points
- 0.0 = Completely irrelevant

Score:"""
        
        try:
            response = self.llm.invoke(prompt)
            score = float(response.content.strip())
            return max(0.0, min(1.0, score))
        except:
            return 0.5  # Default to neutral if parsing fails
    
    def evaluate_citation_accuracy(
        self,
        answer: str,
        citations: List[Any],
        retrieved_chunks: List[Document]
    ) -> float:
        """Evaluate accuracy of citations.
        
        Args:
            answer: Generated answer
            citations: List of citations
            retrieved_chunks: Retrieved document chunks
            
        Returns:
            Citation accuracy score (0-1)
        """
        if not citations:
            # If answer makes claims without citations, score is low
            if len(answer.split()) > 20:  # Non-trivial answer
                return 0.0
            return 0.5
        
        # Check if citations match retrieved documents
        valid_citations = 0
        
        for citation in citations:
            for doc in retrieved_chunks:
                if (doc.metadata.get('filename') == citation.source and
                    (citation.page is None or doc.metadata.get('page') == citation.page)):
                    valid_citations += 1
                    break
        
        accuracy = valid_citations / len(citations) if citations else 0.0
        return accuracy
    
    def evaluate_faithfulness(
        self,
        answer: str,
        retrieved_chunks: List[Document]
    ) -> float:
        """Evaluate if answer is faithful to retrieved context.
        
        Args:
            answer: Generated answer
            retrieved_chunks: Retrieved document chunks
            
        Returns:
            Faithfulness score (0-1)
        """
        context = "\n\n".join([doc.page_content for doc in retrieved_chunks[:3]])
        
        prompt = f"""Evaluate if the answer is faithful to the provided context. Check if the answer makes claims that are not supported by the context.

Context:
{context}

Answer:
{answer}

Rate faithfulness on a scale of 0-1:
- 1.0 = All claims are directly supported by context
- 0.5 = Some claims go beyond context
- 0.0 = Answer contradicts or is unrelated to context

Score:"""
        
        try:
            response = self.llm.invoke(prompt)
            score = float(response.content.strip())
            return max(0.0, min(1.0, score))
        except:
            return 0.5
    
    def evaluate_retrieval_precision(
        self,
        question: str,
        retrieved_chunks: List[Document],
        k: int = 5
    ) -> float:
        """Evaluate precision of retrieval (Precision@K).
        
        Args:
            question: Original question
            retrieved_chunks: Retrieved document chunks
            k: Number of top results to evaluate
            
        Returns:
            Precision score (0-1)
        """
        if not retrieved_chunks:
            return 0.0
        
        chunks_to_eval = retrieved_chunks[:k]
        relevant_count = 0
        
        for doc in chunks_to_eval:
            prompt = f"""Is this document chunk relevant to answering the question?

Question: {question}

Chunk: {doc.page_content[:500]}...

Answer with only 'yes' or 'no':"""
            
            try:
                response = self.llm.invoke(prompt)
                if response.content.strip().lower() == 'yes':
                    relevant_count += 1
            except:
                pass
        
        precision = relevant_count / len(chunks_to_eval) if chunks_to_eval else 0.0
        return precision
    
    def evaluate_response(
        self,
        question: str,
        response: RAGResponse,
        response_time: float
    ) -> EvaluationMetrics:
        """Evaluate complete RAG response.
        
        Args:
            question: Original question
            response: RAG response
            response_time: Time taken to generate response (seconds)
            
        Returns:
            EvaluationMetrics object
        """
        print("Evaluating response...")
        
        # Calculate individual metrics
        answer_relevance = self.evaluate_answer_relevance(question, response.answer)
        print(f"  Answer relevance: {answer_relevance:.3f}")
        
        citation_accuracy = self.evaluate_citation_accuracy(
            response.answer,
            response.citations,
            response.retrieved_chunks
        )
        print(f"  Citation accuracy: {citation_accuracy:.3f}")
        
        faithfulness = self.evaluate_faithfulness(
            response.answer,
            response.retrieved_chunks
        )
        print(f"  Faithfulness: {faithfulness:.3f}")
        
        retrieval_precision = self.evaluate_retrieval_precision(
            question,
            response.retrieved_chunks
        )
        print(f"  Retrieval precision: {retrieval_precision:.3f}")
        
        metrics = EvaluationMetrics(
            answer_relevance=answer_relevance,
            citation_accuracy=citation_accuracy,
            faithfulness=faithfulness,
            retrieval_precision=retrieval_precision,
            response_time=response_time,
            timestamp=datetime.now().isoformat()
        )
        
        # Store evaluation
        self.evaluation_history.append({
            'question': question,
            'answer': response.answer,
            'metrics': metrics.to_dict()
        })
        
        return metrics
    
    def get_average_metrics(self) -> Dict[str, float]:
        """Calculate average metrics across all evaluations.
        
        Returns:
            Dictionary of average metrics
        """
        if not self.evaluation_history:
            return {}
        
        metrics_keys = ['answer_relevance', 'citation_accuracy', 'faithfulness', 
                       'retrieval_precision', 'response_time']
        
        averages = {}
        for key in metrics_keys:
            values = [eval['metrics'][key] for eval in self.evaluation_history]
            averages[f'avg_{key}'] = sum(values) / len(values)
        
        return averages
    
    def save_evaluation_report(self, filepath: str):
        """Save evaluation report to file.
        
        Args:
            filepath: Path to save report
        """
        report = {
            'summary': self.get_average_metrics(),
            'evaluations': self.evaluation_history
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Evaluation report saved to {filepath}")


class TestQuestionGenerator:
    """Generate test questions for evaluation."""
    
    def __init__(self):
        """Initialize test question generator."""
        self.llm = ChatOpenAI(
            model=Config.LLM_MODEL,
            temperature=0.7,
            openai_api_key=Config.OPENAI_API_KEY
        )
    
    def generate_questions_from_document(
        self,
        document_text: str,
        num_questions: int = 5
    ) -> List[str]:
        """Generate test questions from document content.
        
        Args:
            document_text: Source document text
            num_questions: Number of questions to generate
            
        Returns:
            List of generated questions
        """
        prompt = f"""Based on the following document excerpt, generate {num_questions} diverse questions that could be answered using this content.

Include:
- Factual questions (who, what, when, where)
- Analytical questions (why, how)
- Comparison questions
- Definition questions

Document excerpt:
{document_text[:2000]}

Generate {num_questions} questions, one per line:"""
        
        response = self.llm.invoke(prompt)
        questions = [q.strip() for q in response.content.split('\n') if q.strip()]
        
        return questions[:num_questions]
