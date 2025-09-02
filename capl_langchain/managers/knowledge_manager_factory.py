"""
知识库管理器工厂
"""

from typing import Dict, Any, Type
from ..config.config import CAPLGeneratorConfig
from .knowledge_manager import KnowledgeManager


class KnowledgeManagerFactory:
    """知识库管理器工厂"""
    
    @staticmethod
    def create_manager(config: CAPLGeneratorConfig) -> KnowledgeManager:
        """创建知识库管理器
        
        Args:
            config: CAPL生成器配置
            
        Returns:
            知识库管理器实例
        """
        if config.use_hybrid_search:
            print("🔍 使用混合检索方案 (KnowledgeManager)")
        else:
            print("📊 使用纯向量检索方案 (KnowledgeManager)")
        
        return KnowledgeManager(config)
    
    @staticmethod
    def get_available_managers() -> Dict[str, Type[KnowledgeManager]]:
        """获取可用的管理器类型"""
        return {
            "default": KnowledgeManager,
            "hybrid": KnowledgeManager,
            "vector": KnowledgeManager,
        }