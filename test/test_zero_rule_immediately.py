#!/usr/bin/env python3
"""
零规则RAG优化快速测试
"""
import sys
import os
# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from capl_langchain.utils.auto_keyword_extractor import AutoKeywordExtractor

def quick_test():
    print("🚀 零规则RAG优化快速测试")
    print("=" * 40)
    
    try:
        extractor = AutoKeywordExtractor()
        stats = extractor.get_api_statistics()
        
        print(f"📊 已处理API数量: {stats['total_apis']}")
        print(f"📁 文件分布: {stats['files']}")
        print(f"📂 源文件统计: {stats['sources']}")
        
        # Test typical automotive test scenarios
        test_cases = [
            "Set vehicle mode to power on",
            "Connect charging cable for testing",
            "Start diagnostic session",
            "Test wiper intermittent mode",
            "Check battery voltage during engine start",
            "Verify door lock status",
            "Initialize ECU communication",
            "Perform transmission diagnostic"
        ]

        print("\n🧪 Query Expansion Test:")
        print("-" * 25)

        for query in test_cases:
            expanded = extractor.expand_query(query)
            print(f"Original: {query}")
            print(f"Expanded: {expanded}")
            print("-" * 20)
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    
    print("✅ 零规则优化测试完成！")
    return True

if __name__ == "__main__":
    quick_test()
