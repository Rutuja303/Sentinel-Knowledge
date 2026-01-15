import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""
    
    # LLM Provider (ollama or openai)
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
    
    # Ollama Configuration
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_LLM_MODEL = os.getenv("OLLAMA_LLM_MODEL", "llama3.1:8b")
    OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    
    # OpenAI Configuration (fallback/optional)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
    OPENAI_LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "gpt-3.5-turbo")
    
    # Backward compatibility
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", OLLAMA_EMBEDDING_MODEL if LLM_PROVIDER == "ollama" else OPENAI_EMBEDDING_MODEL)
    LLM_MODEL = os.getenv("LLM_MODEL", OLLAMA_LLM_MODEL if LLM_PROVIDER == "ollama" else OPENAI_LLM_MODEL)
    
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
        if cls.LLM_PROVIDER == "openai":
            if not cls.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is required when using OpenAI. Please set it in .env file")
        elif cls.LLM_PROVIDER == "ollama":
            # Check if Ollama is running (optional check, don't fail if not available)
            try:
                import requests
                response = requests.get(f"{cls.OLLAMA_BASE_URL}/api/tags", timeout=2)
                if response.status_code != 200:
                    print(f"⚠️  Warning: Ollama may not be running at {cls.OLLAMA_BASE_URL}")
                    print("   Make sure Ollama is installed and running: https://ollama.ai")
            except ImportError:
                # requests not installed, skip check
                pass
            except Exception:
                print(f"⚠️  Warning: Could not connect to Ollama at {cls.OLLAMA_BASE_URL}")
                print("   Make sure Ollama is installed and running: https://ollama.ai")
                print("   Install: https://ollama.ai/download")
        else:
            raise ValueError(f"Invalid LLM_PROVIDER: {cls.LLM_PROVIDER}. Must be 'ollama' or 'openai'")
    
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
