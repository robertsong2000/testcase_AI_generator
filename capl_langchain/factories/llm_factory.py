"""LLM工厂类"""

from typing import Any
from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaLLM

from ..config.config import CAPLGeneratorConfig


class LLMFactory:
    """LLM工厂类，统一管理不同提供商的LLM"""
    
    @staticmethod
    def create_llm(config: CAPLGeneratorConfig) -> Any:
        """根据配置创建LLM实例"""
        if config.api_type == "ollama":
            return OllamaLLM(
                base_url=config.api_url,
                model=config.model,
                temperature=config.temperature,
                top_p=config.top_p,
                num_ctx=config.context_length,
                num_predict=config.max_tokens
            )
        elif config.api_type == "openai":
            return ChatOpenAI(
                base_url=config.api_url,
                model=config.model,
                temperature=config.temperature,
                top_p=config.top_p,
                max_tokens=config.max_tokens
            )
        else:
            raise ValueError(f"不支持的API类型: {config.api_type}")