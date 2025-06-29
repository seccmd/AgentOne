import os
from typing import Literal
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class ModelConfig(BaseModel):
    """大模型配置"""
    provider: Literal["openai", "ollama", "deepseek"]
    model_name: str
    api_key: str = ""
    base_url: str = ""

class Config:
    """全局配置"""
    # 默认模型配置
    DEFAULT_MODEL = ModelConfig(
        provider="openai",
        model_name="gpt-3.5-turbo",
        api_key=os.getenv("OPENAI_API_KEY", ""),
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    )
    
    # Ollama配置
    OLLAMA_CONFIG = ModelConfig(
        provider="ollama",
        model_name="llama2",
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    )
    
    # DeepSeek配置
    DEEPSEEK_CONFIG = ModelConfig(
        provider="deepseek",
        model_name="deepseek-chat",
        api_key=os.getenv("DEEPSEEK_API_KEY", ""),
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    )
    
    @classmethod
    def get_model_config(cls, provider: str) -> ModelConfig:
        """根据提供商获取模型配置"""
        configs = {
            "openai": cls.DEFAULT_MODEL,
            "ollama": cls.OLLAMA_CONFIG,
            "deepseek": cls.DEEPSEEK_CONFIG
        }
        return configs.get(provider, cls.DEFAULT_MODEL) 