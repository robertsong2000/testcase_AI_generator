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
        
        if config.embedding_api_type == "ollama":
            return OllamaEmbeddings(
                base_url=config.embedding_api_url,
                model=config.embedding_model
            )
        elif config.embedding_api_type == "openai":
            # 为LM Studio和本地服务提供兼容性支持
            api_key = os.getenv("EMBEDDING_API_KEY") or os.getenv("OPENAI_API_KEY") or "not-needed"
            
            # 检查是否为本地服务（LM Studio等）
            is_local_service = any(local in config.embedding_api_url.lower() 
                                 for local in ['127.0.0.1', 'localhost', '192.168.', '0.0.0.0'])
            
            if is_local_service:
                # 本地服务配置优化
                return OpenAIEmbeddings(
                    base_url=config.embedding_api_url,
                    model=config.embedding_model,
                    api_key=api_key,
                    check_embedding_ctx_length=False,
                    model_kwargs={"encoding_format": "float"}
                )
            else:
                # 标准OpenAI兼容服务
                return OpenAIEmbeddings(
                    base_url=config.embedding_api_url,
                    model=config.embedding_model,
                    api_key=api_key
                )
        else:
            raise ValueError(f"不支持的嵌入类型: {config.embedding_api_type}")