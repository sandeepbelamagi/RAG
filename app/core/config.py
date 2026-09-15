from functools import lru_cache
import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.app_name = os.getenv("APP_NAME", "rag-app")
        self.app_env = os.getenv("APP_ENV", "development")
        self.app_host = os.getenv("APP_HOST", "0.0.0.0")
        self.app_port = int(os.getenv("APP_PORT", "8000"))
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
        self.ollama_chat_model = os.getenv("OLLAMA_CHAT_MODEL", "llama3.1")
        self.ollama_embed_model = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
        self.ollama_timeout = float(os.getenv("OLLAMA_TIMEOUT", "120"))
        self.chroma_persist_dir = os.getenv("CHROMA_PERSIST_DIR", "data/chroma")
        self.chroma_collection = os.getenv("CHROMA_COLLECTION", "book_chunks")
        self.embedding_batch_size = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))
        self.upload_dir = os.getenv("UPLOAD_DIR", "data/books")
        self.max_upload_mb = int(os.getenv("MAX_UPLOAD_MB", "100"))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
