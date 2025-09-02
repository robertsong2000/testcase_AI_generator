"""
知识库管理器工厂类，根据配置选择使用纯向量检索或混合检索
"""

from pathlib import Path
from typing import Optional, Union

from ..config.config import CAPLGeneratorConfig

# 导入两种知识库管理器
from .knowledge_manager import KnowledgeBaseManager
from .knowledge_manager_hybrid import HybridKnowledgeBaseManager


class KnowledgeManagerFactory:
    """知识库管理器工厂类"""
    
    @staticmethod
    def create_manager(config: CAPLGeneratorConfig) -> Union[KnowledgeBaseManager, HybridKnowledgeBaseManager]:
        """
        根据配置创建合适的知识库管理器
        
        Args:
            config: CAPL生成器配置
            
        Returns:
            知识库管理器实例（纯向量或混合检索）
        """
        if not config.enable_rag:
            print("⚠️ RAG功能已禁用，创建空知识库管理器")
            return KnowledgeBaseManager(config)
        
        if config.use_hybrid_search:
            print("🔍 使用混合检索方案 (HybridKnowledgeBaseManager)")
            print("   ✅ 向量检索 + 关键词检索")
            print("   ✅ 智能结果融合")
            print("   ✅ 支持重排序")
            return HybridKnowledgeBaseManager(config)
        else:
            print("📊 使用纯向量检索方案 (KnowledgeBaseManager)")
            print("   ✅ 基于语义的向量检索")
            print("   ✅ 支持重排序")
            return KnowledgeBaseManager(config)
    
    @staticmethod
    def get_available_managers() -> dict:
        """获取可用的管理器类型"""
        return {
            "knowledge_manager": {
                "class": KnowledgeBaseManager,
                "name": "纯向量检索",
                "description": "基于语义的向量检索，支持重排序",
                "config_key": "USE_HYBRID_SEARCH=false"
            },
            "knowledge_manager_hybrid": {
                "class": HybridKnowledgeBaseManager,
                "name": "混合检索",
                "description": "向量检索 + 关键词检索的混合方案，支持重排序",
                "config_key": "USE_HYBRID_SEARCH=true"
            }
        }
    
    @staticmethod
    def print_manager_info():
        """打印管理器信息"""
        managers = KnowledgeManagerFactory.get_available_managers()
        print("\n📚 可用的知识库管理器类型:")
        for key, info in managers.items():
            print(f"   🔹 {info['name']} ({key})")
            print(f"      {info['description']}")
            print(f"      配置: {info['config_key']}")
            print()