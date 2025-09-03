#!/usr/bin/env python3
"""
向量数据库状态检查工具
快速查看向量数据库的健康状态和统计信息
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径（从test目录向上）
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from capl_langchain.config.config import CAPLGeneratorConfig
from capl_langchain.managers.knowledge_manager import KnowledgeManager

def check_vector_db_status():
    """检查向量数据库状态"""
    print("🔍 检查向量数据库状态...")
    
    config = CAPLGeneratorConfig()
    
    # 基础信息
    print(f"📁 知识库目录: {config.knowledge_base_dir}")
    print(f"📁 向量数据库目录: {config.vector_db_dir}")
    print(f"🔢 默认K值: {config.k}")
    print(f"📊 分块大小: {config.chunk_size}")
    print(f"🔄 分块重叠: {config.chunk_overlap}")
    
    # 检查目录状态
    kb_exists = config.knowledge_base_dir.exists()
    vector_exists = config.vector_db_dir.exists()
    
    print(f"\n📂 目录状态:")
    print(f"   知识库目录: {'✅ 存在' if kb_exists else '❌ 不存在'}")
    print(f"   向量数据库目录: {'✅ 存在' if vector_exists else '❌ 不存在'}")
    
    if kb_exists:
        # 统计知识库文件
        knowledge_files = list(config.knowledge_base_dir.glob("**/*.md")) + \
                         list(config.knowledge_base_dir.glob("**/*.txt")) + \
                         list(config.knowledge_base_dir.glob("**/*.json")) + \
                         list(config.knowledge_base_dir.glob("**/*.py"))
        
        print(f"   知识库文件: {len(knowledge_files)} 个")
        if knowledge_files:
            print("   文件列表:")
            for f in knowledge_files[:5]:  # 显示前5个
                size = f.stat().st_size
                print(f"     📄 {f.name} ({size} bytes)")
            if len(knowledge_files) > 5:
                print(f"     ... 还有 {len(knowledge_files) - 5} 个文件")
    
    if vector_exists:
        # 检查向量数据库文件
        sqlite_file = config.vector_db_dir / "chroma.sqlite3"
        cache_marker = config.vector_db_dir / ".cache_marker"
        
        print(f"\n💾 向量数据库状态:")
        print(f"   SQLite数据库: {'✅ 存在' if sqlite_file.exists() else '❌ 不存在'}")
        print(f"   缓存标记: {'✅ 存在' if cache_marker.exists() else '❌ 不存在'}")
        
        if sqlite_file.exists():
            size = sqlite_file.stat().st_size
            print(f"   数据库大小: {size:,} bytes ({size/1024/1024:.1f} MB)")
            
        # 检查子目录
        subdirs = [d for d in config.vector_db_dir.iterdir() if d.is_dir()]
        if subdirs:
            print(f"   集合目录: {len(subdirs)} 个")
            for d in subdirs:
                print(f"     📁 {d.name}")
    
    # 测试知识库功能
    print(f"\n🧪 功能测试:")
    try:
        kb_manager = KnowledgeManager(config)
        success = kb_manager.initialize_knowledge_base()
        
        if success:
            print("   ✅ 知识库初始化: 成功")
            
            retriever = kb_manager.get_retriever()
            if retriever:
                print("   ✅ 检索器获取: 成功")
                
                # 测试简单查询
                try:
                    results = retriever.invoke("测试")
                    print(f"   ✅ 检索测试: 成功 ({len(results)} 个结果)")
                    
                    # 显示前几个结果的来源
                    for i, doc in enumerate(results[:3], 1):
                        source = doc.metadata.get('source', '未知')
                        if isinstance(source, str) and 'knowledge_base' in source:
                            source = source.split('knowledge_base/')[-1]
                        print(f"      {i}. {source}")
                        
                except Exception as e:
                    print(f"   ❌ 检索测试: 失败 - {e}")
            else:
                print("   ❌ 检索器获取: 失败")
        else:
            print("   ❌ 知识库初始化: 失败")
            
    except Exception as e:
        print(f"   ❌ 功能测试: 异常 - {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("向量数据库状态检查报告")
    print("=" * 60)
    check_vector_db_status()
    print("\n" + "=" * 60)
    print("检查完成")