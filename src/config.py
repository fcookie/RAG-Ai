"""Configuration management for the RAG Document Assistant."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""
    
    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    CHROMA_DIR = DATA_DIR / "chroma_db"
    UPLOAD_DIR = DATA_DIR / "uploads"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.1"))
    
    # Vector Store Configuration
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "documents")
    
    # Chunking Configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # Retrieval Configuration
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "5"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
    
    # Application Configuration
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
    ENABLE_CONVERSATION_MEMORY: bool = os.getenv("ENABLE_CONVERSATION_MEMORY", "true").lower() == "true"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        
        # Create necessary directories
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.CHROMA_DIR.mkdir(exist_ok=True)
        cls.UPLOAD_DIR.mkdir(exist_ok=True)
        
        return True
    
    @classmethod
    def get_chroma_settings(cls):
        """Get ChromaDB settings."""
        import chromadb
        return chromadb.config.Settings(
            persist_directory=str(cls.CHROMA_DIR),
            anonymized_telemetry=False
        )

# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"Configuration warning: {e}")
