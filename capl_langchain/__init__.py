"""
基于LangChain的CAPL代码生成器

这个包提供了完整的CAPL测试代码生成功能，支持RAG知识库检索。
"""

from .generator import CAPLGenerator
from .config.config import CAPLGeneratorConfig

__version__ = "2.0.0"
__author__ = "CAPL AI Team"

__all__ = [
    "CAPLGenerator",
    "CAPLGeneratorConfig",
]