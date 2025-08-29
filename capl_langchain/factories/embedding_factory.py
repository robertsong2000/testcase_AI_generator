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
        import os
        
        if config.api_type == "ollama":
            return OllamaEmbeddings(
                base_url=config.api_url,
                model=config.embedding_model
            )
        elif config.api_type == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("使用OpenAI兼容API时，必须设置OPENAI_API_KEY环境变量")
            return OpenAIEmbeddings(
                base_url=config.api_url,
                model=config.embedding_model,
                api_key=api_key
            )
        else:
            raise ValueError(f"不支持的嵌入类型: {config.api_type}")