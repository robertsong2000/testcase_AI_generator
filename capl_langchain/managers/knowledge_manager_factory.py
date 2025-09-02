"""
知识库管理器工厂类，使用统一的知识库管理器
"""

from pathlib import Path
from typing import Optional, Union

from ..config.config import CAPLGeneratorConfig

# 导入统一的知识库管理器
from .knowledge_manager import UnifiedKnowledgeBaseManager


class KnowledgeManagerFactory:
    """知识库管理器工厂类"""
    
    @staticmethod
    def create_manager(config: CAPLGeneratorConfig) -> UnifiedKnowledgeBaseManager:
        """
        根据配置创建统一的知识库管理器
        
        Args:
            config: CAPL生成器配置
            
        Returns:
            统一知识库管理器实例
        """
        if not config.enable_rag:
            print("⚠️ RAG功能已禁用，创建空知识库管理器")
            return UnifiedKnowledgeBaseManager(config)
        
        if config.use_hybrid_search:
            print("🔍 使用混合检索方案 (UnifiedKnowledgeBaseManager)")
            print("   ✅ 向量检索 + 关键词检索")
            print("   ✅ 智能结果融合")
            print("   ✅ 支持重排序")
        else:
            print("📊 使用纯向量检索方案 (UnifiedKnowledgeBaseManager)")
            print("   ✅ 基于语义的向量检索")
            print("   ✅ 支持重排序")
            
        return UnifiedKnowledgeBaseManager(config)
    
    @staticmethod
    def get_available_managers() -> dict:
        """获取可用的管理器类型"""
        return {
            "unified_knowledge_manager": {
                "class": UnifiedKnowledgeBaseManager,
                "name": "统一知识库管理器",
                "description": "支持纯向量检索和混合检索的统一实现",
                "config_key": "USE_HYBRID_SEARCH=true/false"
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