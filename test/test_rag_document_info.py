#!/usr/bin/env python3
"""
测试RAG文档信息显示功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from capl_langchain.services.generator_service import CAPLGeneratorService
from capl_langchain.config.config import CAPLGeneratorConfig

def test_rag_document_display():
    """测试RAG文档信息显示功能"""
    print("🧪 测试RAG文档信息显示功能...")
    
    # 创建配置
    config = CAPLGeneratorConfig()
    config.enable_rag = True  # 强制启用RAG
    
    # 创建服务
    service = CAPLGeneratorService(config)
    
    # 测试不同的查询
    test_queries = [
        "CAPL测试用例",
        "雨刷器间歇模式",
        "CAN消息通信测试",
        "低功耗测试场景"
    ]
    
    print("=" * 60)
    print("RAG文档检索测试")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n🔍 查询: '{query}'")
        print("-" * 40)
        
        try:
            # 使用服务测试RAG搜索
            service.test_rag_search(query, k=3)
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        
        print()

def main():
    """主函数"""
    print("=" * 60)
    print("RAG文档信息显示功能测试")
    print("=" * 60)
    
    try:
        test_rag_document_display()
        print("🎉 测试完成！")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()