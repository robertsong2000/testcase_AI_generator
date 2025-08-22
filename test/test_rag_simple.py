#!/usr/bin/env python3
"""
LangChain RAG功能测试文件 v2
修复检索器获取问题，增加更多测试场景
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from capl_generator_langchain import CAPLGeneratorConfig, KnowledgeBaseManager

def test_rag_comprehensive():
    """综合RAG功能测试"""
    print("🧪 开始综合RAG功能测试...")
    
    try:
        # 创建配置
        config = CAPLGeneratorConfig()
        config.enable_rag = True  # 强制启用RAG
        
        print(f"📁 知识库目录: {config.knowledge_base_dir}")
        print(f"📁 向量数据库目录: {config.vector_db_dir}")
        
        # 检查向量数据库状态
        vector_db_exists = config.vector_db_dir.exists() and \
                          any(config.vector_db_dir.glob("*"))
        
        if vector_db_exists:
            print("✅ 向量数据库已存在")
            # 列出数据库文件
            for item in config.vector_db_dir.rglob("*"):
                if item.is_file():
                    size = item.stat().st_size
                    print(f"   📄 {item.relative_to(config.vector_db_dir)} ({size} bytes)")
        else:
            print("ℹ️  向量数据库不存在，将创建新的")
        
        # 创建知识库管理器
        kb_manager = KnowledgeBaseManager(config)
        
        # 重新初始化知识库（确保检索器可用）
        print("\n🔄 重新初始化知识库...")
        success = kb_manager.initialize_knowledge_base()
        
        if success:
            print("✅ 知识库重新初始化成功")
            
            # 获取检索器
            retriever = kb_manager.get_retriever()
            if retriever:
                print("✅ 检索器获取成功")
                
                # 测试不同的查询
                test_queries = [
                    "CAPL测试用例",
                    "雨刷器间歇模式",
                    "CAN消息周期",
                    "低功耗测试",
                    "测试标准"
                ]
                
                print("\n🔍 执行检索测试...")
                for query in test_queries:
                    print(f"\n📋 查询: '{query}'")
                    try:
                        docs = retriever.invoke(query)
                        print(f"   ✅ 找到 {len(docs)} 个相关文档")
                        
                        # 显示每个文档的相关内容摘要
                        for i, doc in enumerate(docs[:2], 1):  # 只显示前2个
                            content = doc.page_content.strip()
                            if len(content) > 150:
                                content = content[:150] + "..."
                            print(f"   📄 文档{i}: {content}")
                            
                    except Exception as e:
                        print(f"   ❌ 检索失败: {e}")
                        
                # 测试具体场景
                print("\n🎯 测试具体场景...")
                
                # 测试雨刷器相关查询
                wiper_query = "雨刷器间歇模式测试"
                print(f"\n🔍 雨刷器查询: '{wiper_query}'")
                docs = retriever.invoke(wiper_query)
                if docs:
                    print(f"   ✅ 找到 {len(docs)} 个雨刷器相关文档")
                    # 检查内容相关性
                    for doc in docs[:1]:
                        if "雨刷" in doc.page_content or "wiper" in doc.page_content.lower():
                            print("   ✅ 内容包含雨刷器相关信息")
                        else:
                            print("   ⚠️  内容可能不直接相关")
                
                # 测试CAN通信相关查询
                can_query = "CAN消息通信测试"
                print(f"\n🔍 CAN查询: '{can_query}'")
                docs = retriever.invoke(can_query)
                if docs:
                    print(f"   ✅ 找到 {len(docs)} 个CAN相关文档")
                
            else:
                print("❌ 无法获取检索器")
                return False
                
        else:
            print("❌ 知识库初始化失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    return True

def test_rag_performance():
    """测试RAG性能"""
    print("\n🚀 测试RAG性能...")
    
    try:
        import time
        
        config = CAPLGeneratorConfig()
        config.enable_rag = True
        kb_manager = KnowledgeBaseManager(config)
        
        # 测量初始化时间
        start_time = time.time()
        success = kb_manager.initialize_knowledge_base()
        init_time = time.time() - start_time
        
        if success:
            print(f"   ⏱️  初始化耗时: {init_time:.2f}秒")
            
            retriever = kb_manager.get_retriever()
            if retriever:
                # 测量检索时间
                query = "CAPL测试"
                start_time = time.time()
                docs = retriever.invoke(query)
                search_time = time.time() - start_time
                
                print(f"   ⏱️  检索耗时: {search_time:.3f}秒")
                print(f"   📊 找到 {len(docs)} 个结果")
                
                return True
        
        return False
        
    except Exception as e:
        print(f"   ❌ 性能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("LangChain RAG功能综合测试")
    print("=" * 60)
    
    # 测试1: 综合功能测试
    success1 = test_rag_comprehensive()
    
    # 测试2: 性能测试
    success2 = test_rag_performance()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试结果总结:")
    print(f"综合功能测试: {'✅ 通过' if success1 else '❌ 失败'}")
    print(f"性能测试: {'✅ 通过' if success2 else '❌ 失败'}")
    
    if success1 and success2:
        print("🎉 所有测试通过！RAG功能正常")
        return 0
    else:
        print("⚠️  部分测试失败")
        return 1

if __name__ == "__main__":
    exit(main())