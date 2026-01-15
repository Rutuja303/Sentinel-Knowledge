import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    
    # Paths
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    DOCUMENTS_PATH = os.getenv("DOCUMENTS_PATH", "./data/documents")
    
    # Gap Detection Thresholds
    MIN_SIMILARITY_SCORE = float(os.getenv("MIN_SIMILARITY_SCORE", "0.3"))
    REPEATED_QUERY_THRESHOLD = int(os.getenv("REPEATED_QUERY_THRESHOLD", "3"))
    UNCERTAINTY_PHRASES = os.getenv(
        "UNCERTAINTY_PHRASES",
        "I'm not sure,I don't have information,I cannot find,unable to locate,no documentation found"
    ).split(",")
    
    # Confluence
    CONFLUENCE_URL = os.getenv("CONFLUENCE_URL", "")
    CONFLUENCE_USERNAME = os.getenv("CONFLUENCE_USERNAME", "")
    CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN", "")
    CONFLUENCE_SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY", "")  # Optional: specific space
    
    # Application
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required. Please set it in .env file")
    
    @classmethod
    def validate_confluence(cls):
        """Validate Confluence configuration"""
        if not cls.CONFLUENCE_URL:
            raise ValueError("CONFLUENCE_URL is required for Confluence integration")
        if not cls.CONFLUENCE_USERNAME:
            raise ValueError("CONFLUENCE_USERNAME is required for Confluence integration")
        if not cls.CONFLUENCE_API_TOKEN:
            raise ValueError("CONFLUENCE_API_TOKEN is required for Confluence integration")


config = Config()
