import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Ollama Configuration for Minimax 2.1
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "minimax")
    USE_OLLAMA: bool = True  # Always use Ollama by default
    
    # Minimax Cloud API (optional, only if user wants cloud instead)
    MINIMAX_API_KEY: str = os.getenv("MINIMAX_API_KEY", "")
    MINIMAX_GROUP_ID: str = os.getenv("MINIMAX_GROUP_ID", "")
    MINIMAX_API_URL: str = "https://api.minimax.chat/v1/text/chatcompletion_v2"
    MINIMAX_MODEL: str = "abab6.5s-chat"
    
    # Application Settings
    MAX_TOOL_ITERATIONS: int = 10
    TIMEOUT_SECONDS: int = 300
    MAX_FILE_SIZE_MB: int = 100
    ALLOWED_EXTENSIONS: set = {".txt", ".py", ".js", ".java", ".md", ".json", ".yaml", ".yml", ".xml", ".html", ".css"}
    
    # Working Directory
    WORKSPACE_DIR: Path = Path(os.getenv("WORKSPACE_DIR", "./workspace"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")
    
    # Safety
    ENABLE_SHELL_COMMANDS: bool = os.getenv("ENABLE_SHELL_COMMANDS", "true").lower() == "true"
    RESTRICTED_COMMANDS: set = {"rm -rf /", "sudo", "mkfs", "dd if=", ":(){:|:&};:"}
    RESTRICTED_PATHS: set = {"/etc", "/sys", "/proc", "/dev", "/boot"}
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        if cls.USE_OLLAMA:
            print(f"Using Ollama at {cls.OLLAMA_HOST} with model '{cls.OLLAMA_MODEL}'")
            print("No API keys needed!")
        elif not cls.MINIMAX_API_KEY or not cls.MINIMAX_GROUP_ID:
            raise ValueError("If not using Ollama, MINIMAX_API_KEY and MINIMAX_GROUP_ID must be set")
        return True

Config.validate()
