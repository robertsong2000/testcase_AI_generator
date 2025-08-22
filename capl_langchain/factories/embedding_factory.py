"""嵌入模型工厂类"""

from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_core.embeddings import Embeddings

from ..config.config import CAPLGeneratorConfig


class EmbeddingFactory:
    """嵌入模型工厂类"""
    
    @staticmethod
    def create_embeddings(config: CAPLGeneratorConfig) -> Embeddings:
        """根据配置创建嵌入模型"""
        if config.api_type == "ollama":
            return OllamaEmbeddings(
                base_url=config.api_url,
                model=config.embedding_model
            )
        elif config.api_type == "openai":
            return OpenAIEmbeddings(
                base_url=config.api_url,
                model=config.embedding_model
            )
        else:
            raise ValueError(f"不支持的嵌入类型: {config.api_type}")